"""Hands-free slow-mo MCP 60fps capture manifest & compiler (SFX-only, no voiceover/subtitles yet)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Dell\never-look-behind")
SEC_DIR = ROOT / "sections_60fps"
SEC_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST = ROOT / "clips_60fps.json"
FFMPEG = r"C:\Users\Dell\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
FFPROBE = str(Path(FFMPEG).with_name("ffprobe.exe"))
SFX_WAV = ROOT / "audio" / "sfx_only_7m22s.wav"


def load_clips():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {}


def detect_slate_end(video: str) -> float:
    frames_probe = json.loads(subprocess.check_output([
        FFPROBE, "-v", "error", "-select_streams", "v:0",
        "-read_intervals", "%+20", "-show_entries",
        "frame=best_effort_timestamp_time", "-of", "json", video,
    ]))["frames"]
    px_slate = subprocess.check_output([
        FFMPEG, "-v", "error", "-i", video, "-t", "20",
        "-vf", "scale=1:1", "-pix_fmt", "rgb24", "-fps_mode", "passthrough", "-f", "rawvideo", "-",
    ])
    cols = [tuple(px_slate[k:k + 3]) for k in range(0, len(px_slate), 3)]
    saw_mag, first_film = False, None
    for k, (r, g, b) in enumerate(cols):
        if r > 200 and g < 60 and b > 200:
            saw_mag = True
        elif saw_mag:
            first_film = k
            break
    if not saw_mag or first_film is None:
        raise RuntimeError(f"NO_SLATE saw_mag={saw_mag} frames={len(cols)}")
    return float(frames_probe[min(first_film, len(frames_probe) - 1)]["best_effort_timestamp_time"])


def add_clip(idx: int, video: str, manifest: str, lead_rec: float, film_dur: float, time_scale: float):
    """Verify clip captured at slow-mo time_scale (e.g. 0.5 -> rec_dur = film_dur / time_scale)."""
    meta = json.loads(Path(manifest).read_text(encoding="utf-8"))
    vsize = Path(video).stat().st_size
    dur = meta["video"]["duration_seconds"]
    frames = meta["video"]["encoded_frame_count"]
    w = meta["video"]["width"]
    h = meta["video"]["height"]
    drops = meta.get("capture_health", {}).get("observed_capture_drops", -1)
    if vsize < 600000:
        raise RuntimeError(f"CLIP_{idx:02d}_TOO_SMALL size={vsize}")
    slate_end = detect_slate_end(video)
    need_rec = film_dur / time_scale
    avail_rec = dur - (slate_end + lead_rec)
    if avail_rec < need_rec - 0.15:
        raise RuntimeError(f"CLIP_{idx:02d}_SHORT avail={avail_rec:.2f}s < need={need_rec:.2f}s (slate_end={slate_end:.2f}s)")

    sample_t = min(slate_end + lead_rec + 4.0, max(2.0, dur - 2.0))
    px = subprocess.check_output([
        FFMPEG, "-v", "error", "-ss", f"{sample_t:.1f}", "-i", video,
        "-frames:v", "1", "-vf", "crop=iw/2:ih/2:iw/4:ih/4,scale=8:8", "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
    ])
    vals = list(px)
    spread = (max(vals) - min(vals)) if vals else 0
    if spread < 12 and idx != 56:  # center-crop spread=0 on solid #1A1B1E grey!
        raise RuntimeError(f"CLIP_{idx:02d}_GREY_FRAME spread={spread} size={vsize}")

    eff_fps = (frames / max(dur, 0.1)) / time_scale
    data = load_clips()
    data[str(idx)] = {
        "idx": idx, "video": video, "manifest": manifest,
        "lead_rec": lead_rec, "film_dur": film_dur, "time_scale": time_scale,
        "slate_end": slate_end, "raw_dur": dur, "raw_frames": frames,
    }
    MANIFEST.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"CLIP_{idx:02d}_OK {w}x{h} slate={slate_end:.2f}s avail={avail_rec:.2f}s/{need_rec:.2f}s eff_fps={eff_fps:.1f} drops={drops} size_mb={vsize/1048576:.2f} spread={spread}", flush=True)


def compile_all(num_sections: int, out_fps: int = 60):
    data = load_clips()
    missing = [i for i in range(num_sections) if str(i) not in data]
    if missing:
        raise RuntimeError(f"Missing clips: {missing}")

    for i in range(num_sections):
        c = data[str(i)]
        src = c["video"]
        ts = c["time_scale"]
        trim_start = c["slate_end"] + c["lead_rec"]
        out = SEC_DIR / f"sec_{i:02d}.mp4"
        target_frames = int(round(c["film_dur"] * out_fps))
        # Speed up slow-mo recording by 1/ts -> locked out_fps, cleanly 1280x720 with pure-black cinema bars!
        vf = (
            f"setpts=(PTS-STARTPTS)*{ts:.6f},"
            f"fps={out_fps},"
            f"scale=1280:720:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad=1280:720:(ow-iw)/2:(oh-ih)/2:black,"
            f"drawbox=x=0:y=0:w=1280:h=58:color=black:t=fill,"
            f"drawbox=x=0:y=662:w=1280:h=58:color=black:t=fill,"
            f"tpad=stop_mode=clone:stop_duration=0.3"
        )
        subprocess.run([
            FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{trim_start:.4f}", "-i", src, "-an",
            "-vf", vf,
            "-frames:v", str(target_frames),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
            "-pix_fmt", "yuv420p", "-video_track_timescale", "90000",
            str(out),
        ], check=True)
        print(f"TRIM_{i:02d}_OK frames={target_frames} size={out.stat().st_size}", flush=True)

    listing = SEC_DIR / "concat.txt"
    listing.write_text("".join(f"file 'sec_{i:02d}.mp4'\n" for i in range(num_sections)), encoding="utf-8")
    silent = ROOT / "Never_Look_Behind_You_60fps_Silent.mp4"
    final = Path(r"C:\Users\Dell\Downloads\Never_Look_Behind_You_60fps_SFX.mp4")

    subprocess.run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(listing),
        "-c", "copy", "-movflags", "+faststart", str(silent),
    ], check=True)

    subprocess.run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(silent), "-i", str(SFX_WAV),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        str(final),
    ], check=True)

    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-i", str(final), "-f", "null", "-"], check=True)
    dur = float(subprocess.check_output([
        FFPROBE, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(final),
    ]).decode().strip())
    print(f"FINAL_60FPS_READY {final} duration={dur:.2f}s size_mb={final.stat().st_size / 1048576:.2f}", flush=True)


def export_preview(n_clips: int = 5):
    data = load_clips()
    for i in range(n_clips):
        c = data[str(i)]
        ts = c["time_scale"]
        trim_start = c["slate_end"] + c["lead_rec"]
        out = SEC_DIR / f"prev_{i:02d}.mp4"
        target_frames = int(round(c["film_dur"] * 30))
        vf = (
            f"setpts=(PTS-STARTPTS)*{ts:.6f},fps=30,"
            f"scale=1280:720:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad=1280:720:(ow-iw)/2:(oh-ih)/2:black,"
            f"drawbox=x=0:y=0:w=1280:h=58:color=black:t=fill,"
            f"drawbox=x=0:y=662:w=1280:h=58:color=black:t=fill,"
            f"tpad=stop_mode=clone:stop_duration=0.3"
        )
        subprocess.run([
            FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{trim_start:.4f}", "-i", c["video"], "-an",
            "-vf", vf, "-frames:v", str(target_frames),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
            "-pix_fmt", "yuv420p", "-video_track_timescale", "90000", str(out),
        ], check=True)
    listing = SEC_DIR / "prev_concat.txt"
    listing.write_text("".join(f"file 'prev_{i:02d}.mp4'\n" for i in range(n_clips)), encoding="utf-8")
    silent = SEC_DIR / "prev_silent.mp4"
    final = Path(r"C:\Users\Dell\Downloads\Preview_First60s_Smooth.mp4")
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(silent)], check=True)
    subprocess.run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(silent), "-i", str(SFX_WAV),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final),
    ], check=True)
    print(f"PREVIEW_READY {final} size_mb={final.stat().st_size / 1048576:.2f}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "add":
        add_clip(int(sys.argv[2]), sys.argv[3], sys.argv[4], float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]))
    elif cmd == "compile":
        compile_all(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 60)
    elif cmd == "preview":
        export_preview(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
