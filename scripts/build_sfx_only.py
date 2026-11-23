"""Generate a rich 442.484s SFX + dark horror ambience WAV track (ZERO voiceover) synced to every visual beat."""
import math
import random
import struct
import wave
from pathlib import Path

SR = 44100
DUR = 442.484
N = int(round(DUR * SR))
OUT = Path(r"C:\Users\Dell\never-look-behind\audio\sfx_only_7m22s.wav")
OUT.parent.mkdir(parents=True, exist_ok=True)


def add_buf(dst, start_s, samples, gain=1.0):
    i0 = int(round(start_s * SR))
    for k, v in enumerate(samples):
        idx = i0 + k
        if 0 <= idx < N:
            dst[idx] += v * gain


def synth_drone(n_samples):
    # Deep eerie dark horror sub-drone + slow wind modulation
    out = [0.0] * n_samples
    r = random.Random(42)
    lp = 0.0
    for i in range(n_samples):
        t = i / SR
        # Slow ominous pulsing sub-bass (46 Hz + 69 Hz + 92 Hz)
        env = 0.65 + 0.35 * math.sin(2 * math.pi * 0.07 * t)
        sub = (
            0.55 * math.sin(2 * math.pi * 46.25 * t)
            + 0.30 * math.sin(2 * math.pi * 69.30 * t + 0.5 * math.sin(0.3 * t))
            + 0.15 * math.sin(2 * math.pi * 92.50 * t)
        )
        # Soft dark night wind (low-pass filtered noise)
        lp = lp * 0.985 + (r.uniform(-1, 1)) * 0.015
        wind = lp * (0.4 + 0.3 * math.sin(2 * math.pi * 0.13 * t))
        # Quiet tension during morning library (249..301s) & morning aftermath (357..385s)
        mood_mul = 0.35 if (249 <= t <= 301 or 357 <= t <= 385) else 1.0
        # Silence right after climax blackout scream (353..357.4s)
        if 353.0 <= t <= 357.4:
            mood_mul = 0.04
        out[i] = (sub * 0.11 * env + wind * 0.14) * mood_mul
    return out


def footstep(heavy=False, wet=False):
    dur = 0.16 if heavy else 0.11
    n = int(dur * SR)
    r = random.Random(101 if heavy else 202)
    out = []
    lp = 0.0
    for i in range(n):
        t = i / SR
        env = math.exp(-t * (22 if heavy else 34))
        thud = math.sin(2 * math.pi * (68 if heavy else 110) * t * (1 - 0.5 * t / dur)) * env
        nz = r.uniform(-1, 1)
        lp = lp * (0.88 if not wet else 0.65) + nz * (0.12 if not wet else 0.35)
        splash = lp * math.exp(-t * (16 if wet else 42)) * (0.55 if wet else 0.25)
        out.append((thud * (0.85 if heavy else 0.55) + splash))
    return out


def clock_chime():
    n = int(2.6 * SR)
    out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 1.45)
        v = (
            0.55 * math.sin(2 * math.pi * 196.0 * t)
            + 0.30 * math.sin(2 * math.pi * 392.0 * t) * math.exp(-t * 1.2)
            + 0.18 * math.sin(2 * math.pi * 587.3 * t) * math.exp(-t * 2.5)
            + 0.12 * math.sin(2 * math.pi * 246.9 * t)
        )
        out.append(v * env)
    return out


def click_switch():
    n = int(0.06 * SR)
    r = random.Random(303)
    return [r.uniform(-1, 1) * math.exp(-i / (SR * 0.009)) * 0.6 for i in range(n)]


def door_slam(heavy=True):
    n = int(0.55 * SR)
    r = random.Random(404)
    lp = 0.0
    out = []
    for i in range(n):
        t = i / SR
        lp = lp * 0.90 + r.uniform(-1, 1) * 0.10
        boom = math.sin(2 * math.pi * (55 * math.exp(-t * 4)) * t) * math.exp(-t * 9)
        crack = lp * math.exp(-t * 24) * 0.9
        out.append((boom + crack) * (0.95 if heavy else 0.65))
    return out


def door_knock():
    n = int(0.22 * SR)
    r = random.Random(505)
    lp = 0.0
    out = []
    for i in range(n):
        t = i / SR
        lp = lp * 0.85 + r.uniform(-1, 1) * 0.15
        wood = math.sin(2 * math.pi * 145 * t) * math.exp(-t * 28) + 0.5 * math.sin(2 * math.pi * 260 * t) * math.exp(-t * 36)
        out.append(wood * 0.75 + lp * math.exp(-t * 45) * 0.35)
    return out


def phone_ring():
    n = int(1.6 * SR)
    out = []
    for i in range(n):
        t = i / SR
        gate = 1.0 if ((t % 0.5) < 0.32) else 0.0
        tone = (math.sin(2 * math.pi * 880 * t) + 0.7 * math.sin(2 * math.pi * 1108.7 * t)) * 0.35
        out.append(tone * gate)
    return out


def horror_sting(dur=2.2, intense=False):
    n = int(dur * SR)
    r = random.Random(606)
    out = []
    for i in range(n):
        t = i / SR
        env = min(1.0, t / 0.04) * math.exp(-t * (1.1 if intense else 1.7))
        # Dissonant tritone + sub impact
        boom = math.sin(2 * math.pi * (48 * math.exp(-t * 1.8)) * t) * 0.75
        screech = (
            0.35 * math.sin(2 * math.pi * (520 + 40 * math.sin(t * 18)) * t)
            + 0.30 * math.sin(2 * math.pi * (735 - 25 * t) * t)
        ) * (1.0 if intense else 0.55)
        grit = r.uniform(-1, 1) * 0.15 * math.exp(-t * 6)
        out.append((boom + screech + grit) * env)
    return out


def heartbeat_beat():
    n = int(0.45 * SR)
    out = []
    for i in range(n):
        t = i / SR
        b1 = math.sin(2 * math.pi * 48 * t) * math.exp(-t * 22)
        b2 = (math.sin(2 * math.pi * 44 * (t - 0.16)) * math.exp(-(t - 0.16) * 26)) if t > 0.16 else 0.0
        out.append((b1 * 0.75 + b2 * 0.55))
    return out


def main():
    print("Synthesizing 7m22s SFX-only horror soundscape...", flush=True)
    buf = synth_drone(N)

    # Opening midnight chimes (0:04, 0:07) + eerie opening sting (0:18, 0:30)
    ch = clock_chime()
    add_buf(buf, 4.5, ch, 0.55)
    add_buf(buf, 7.2, ch, 0.45)
    add_buf(buf, 18.2, horror_sting(1.8), 0.50)
    add_buf(buf, 30.8, horror_sting(2.0), 0.65)

    # Opening footsteps (0:09..0:28)
    fs_norm = footstep(False, True)
    fs_heavy = footstep(True, True)
    for t in [9.5 + k * 0.48 for k in range(18)]:
        add_buf(buf, t, fs_norm, 0.35)

    # 0:42..0:53: Townspeople locking doors & clicking house lights OFF one by one!
    ck = click_switch()
    sl_light = door_slam(False)
    for t in [44.0, 46.2, 48.0, 49.4, 50.6, 51.8]:
        add_buf(buf, t, ck, 0.75)
    for t in [45.0, 48.6, 50.2]:
        add_buf(buf, t, sl_light, 0.55)

    # 1:06..1:13: Daniel walking from friend's porch + phone unlock click at 1:10
    for t in [66.5 + k * 0.52 for k in range(10)]:
        add_buf(buf, t, fs_norm, 0.38)
    add_buf(buf, 70.0, ck, 0.65)

    # 1:13..1:19: Daniel sprinting + MIDNIGHT CLOCK STRIKES 12:00!
    for t in [73.8 + k * 0.28 for k in range(16)]:
        add_buf(buf, t, fs_norm, 0.48)
    add_buf(buf, 76.2, ch, 0.78)
    add_buf(buf, 78.6, ch, 0.65)
    add_buf(buf, 80.3, horror_sting(1.6), 0.45)

    # 1:23..1:56: Slow heavy footsteps getting faster behind him + heartbeat!
    hb = heartbeat_beat()
    for t in [83.5, 84.5, 85.5, 86.5, 87.4, 88.3, 89.2, 90.1, 91.0, 91.9]:
        add_buf(buf, t, fs_heavy, 0.62)
    # Stops when Mom's voice calls (1:37..1:46) -> heartbeat pulses
    for t in [97.5, 98.4, 99.3, 100.2, 101.1, 102.0, 103.0, 104.0]:
        add_buf(buf, t, hb, 0.58)
    # Faster footsteps (1:47..1:56)
    for t in [107.8 + k * 0.36 for k in range(24)]:
        add_buf(buf, t, fs_heavy, 0.65)

    # 1:57..2:11: Flashlight click + second shadow reveal sting!
    add_buf(buf, 118.2, ck, 0.85)
    add_buf(buf, 124.2, horror_sting(2.2, True), 0.72)

    # 2:11..2:43: Full sprint + phone ringing + call disconnect sting!
    for t in [131.0 + k * 0.24 for k in range(38)]:
        add_buf(buf, t, fs_heavy, 0.58)
    pr = phone_ring()
    add_buf(buf, 139.6, pr, 0.62)
    add_buf(buf, 142.8, ck, 0.70)
    for t in [147.0, 148.0, 149.0, 150.0, 151.0, 152.0]:
        add_buf(buf, t, hb, 0.52)
    add_buf(buf, 158.0, horror_sting(2.4, True), 0.78)
    add_buf(buf, 161.9, ck, 0.80)

    # 2:45..3:11: Slow footsteps approaching porch + Copy-Mom smile sting!
    for t in [179.0 + k * 0.75 for k in range(7)]:
        add_buf(buf, t, fs_norm, 0.35)
    add_buf(buf, 189.0, horror_sting(2.0, True), 0.75)

    # 3:11..3:23: Runs inside + HUGE FRONT DOOR SLAM + locks clicking!
    add_buf(buf, 193.5, door_slam(True), 0.92)
    add_buf(buf, 200.2, ck, 0.80)
    add_buf(buf, 201.1, ck, 0.80)

    # 3:58..4:08: Window turn -> Copy-Daniel outside sting!
    add_buf(buf, 241.0, horror_sting(2.5, True), 0.78)

    # 4:18..4:32: Library 1998 newspaper reveal sting!
    add_buf(buf, 261.0, horror_sting(2.0), 0.55)
    add_buf(buf, 268.0, horror_sting(2.2), 0.62)

    # 5:08..5:56: FINAL NIGHT — 3 VIOLENT DOOR KNOCKS + CLIMAX TRANSFORMATION + LAMP BURST BLACKOUT!
    kn = door_knock()
    add_buf(buf, 308.4, kn, 0.95)
    add_buf(buf, 309.2, kn, 0.95)
    add_buf(buf, 310.0, kn, 0.98)
    for t in [316.0 + k * 0.75 for k in range(18)]:
        add_buf(buf, t, hb, 0.65)
    add_buf(buf, 323.5, horror_sting(2.0), 0.68)
    add_buf(buf, 335.8, horror_sting(2.6, True), 0.82)
    add_buf(buf, 344.2, horror_sting(2.8, True), 0.88)
    # Lamp blows out & blackout crash at 351.7s!
    add_buf(buf, 351.7, door_slam(True), 0.95)
    add_buf(buf, 351.8, horror_sting(2.6, True), 0.95)

    # 5:57..6:11: Next morning door creak/open
    add_buf(buf, 357.8, door_slam(False), 0.45)

    # 6:20..7:22: School twist + final horror sting!
    add_buf(buf, 381.0, horror_sting(1.6), 0.55)
    add_buf(buf, 408.0, horror_sting(2.2), 0.68)
    add_buf(buf, 415.5, horror_sting(2.8, True), 0.88)
    add_buf(buf, 434.0, horror_sting(3.2, True), 0.82)

    # Soft-clip & write 16-bit PCM WAV
    pcm = bytearray(N * 2)
    for i, s in enumerate(buf):
        v = math.tanh(s * 0.92)
        iv = max(-32767, min(32767, int(v * 32767)))
        struct.pack_into("<h", pcm, i * 2, iv)

    with wave.open(str(OUT), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm)
    print(f"SFX_READY {OUT} dur={DUR:.2f}s size_mb={OUT.stat().st_size / 1048576:.2f}", flush=True)


if __name__ == "__main__":
    main()
