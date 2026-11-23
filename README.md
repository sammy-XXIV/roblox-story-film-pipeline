# Viral Roblox Story & Horror Film Pipeline ("In This World..." Style)

End-to-end automated pipeline for creating, animating, recording (`60 fps`), voicing (**AI33.pro / ElevenLabs**), scoring (**Suno BGM + procedural SFX**), captioning, and packaging viral **"In This World..."** 3D Roblox story & horror YouTube videos using **Roblox Studio MCP** + **FFmpeg** + **AI Agents (Antigravity / Claude Code)**.

---

## Repository Structure

```text
roblox-story-film-pipeline/
├── README.md                         # Complete setup & production guide (this file)
├── SKILL.md                          # Drop-in Antigravity / Claude Code skill
├── .env.example                      # Environment variables template (AI33_API_KEY)
├── prompts/
│   └── AI_PROMPTS.md                 # Copy-paste AI prompts for every stage
├── luau/
│   └── rig_and_lighting_setup.luau   # Engine-native blocky rigs, anti-glow lighting, DoF & Director template
└── scripts/
    ├── ai33_client.py                # AI33.pro v3 TTS (Little Dude II) & Suno BGM CLI client
    ├── compile_60fps_mcp.py          # Zero-drop 0.5x slow-mo MCP capture verifier & 60fps compiler
    └── build_sfx_only.py             # Procedural story/horror SFX generator
```

---

## 1. Prerequisites & Setup

### A. Tools Required
1. **Roblox Studio** (logged in on Windows/macOS).
2. **Roblox Studio MCP Server** connected to your AI agent (exposes `execute_luau`, `video_capture`, `screen_capture`, `start_stop_play`, `save_place`).
3. **Python 3.10+** (standard library only for `ai33_client.py` and `compile_60fps_mcp.py`).
4. **FFmpeg 7.x+** (`ffmpeg.exe` and `ffprobe.exe` with `libx264`, `rubberband`, and `sidechaincompress`).
5. **AI33.pro API Key** (provides both ElevenLabs v3 TTS voices like **Little Dude II** and **Suno** instrumental music generation).

### B. Install the Skill into Antigravity / Claude Code
Copy `SKILL.md` and `scripts/ai33_client.py` into your agent skills directory:
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.agents\skills\roblox-horror-film-pipeline\scripts" | Out-Null
Copy-Item ".\SKILL.md" "$HOME\.agents\skills\roblox-horror-film-pipeline\SKILL.md" -Force
Copy-Item ".\scripts\ai33_client.py" "$HOME\.agents\skills\roblox-horror-film-pipeline\scripts\ai33_client.py" -Force
```

Set your AI33.pro key in your environment:
```powershell
$env:AI33_API_KEY = "sk_your_ai33_api_key_here"
```

---

## 2. Setting Up Roblox Studio (Critical Before Recording)

Before pressing **Play** or calling `video_capture`, configure Roblox Studio so Direct3D11 capture never produces grey frames, dropped frames, invisible bodies, or glowing skin:

### Rule 1: Device Emulator ON (`1072×592` 16:9 HD) & Window Uncovered
- In Roblox Studio, open the **Test** / **View** tab → toggle **Device Emulator ON** (set to a clean 16:9 HD resolution such as `1072×592` or `1280×720` with touch UI controls hidden).
- Keep the Roblox Studio window **visible on screen** (never minimize it or cover it completely with another maximized window during `video_capture`).

### Rule 2: Anti-Grey Capture Fix — NEVER Use `Lighting.Atmosphere`
- On Direct3D11 / Intel integrated GPUs, having a `Lighting.Atmosphere` instance causes MCP `video_capture` to output solid `#1A1B1E` grey video.
- **Fix:** Delete `Lighting.Atmosphere` and use classic `Lighting.FogStart`, `Lighting.FogEnd`, and `Lighting.FogColor` instead, paired with `Lighting.DepthOfFieldEffect` for soft background blur.

### Rule 3: Anti-Invisible Character Fix — Zero `MeshPart`s
- `Players:CreateHumanoidModelFromDescription` spawns `MeshPart` limbs whose external CDN `MeshId`s can fail to stream mid-capture, leaving floating hair, faces, and backpacks.
- **Fix:** Build characters with **100% engine-native `Part` blocks** (`Shape = Enum.PartType.Block` for torso/arms/legs) and `SpecialMesh(Enum.MeshType.Head)` on the `Head` only. Skip `BaseWrap` children when migrating from `MeshPart`.

### Rule 4: Anti-Glow Skin & Lighting Calibration
Bright local lights + low Bloom threshold + high reflectance make pale character faces and hands glow like neon bulbs.
- `BloomEffect.Threshold = 2.4` *(never `< 1.5`)*
- `BloomEffect.Intensity = 0.20`
- Remove all character `RimLight`s.
- Cap nearby room/porch `PointLight.Brightness` to **`1.45–2.0`**.
- Set skin `Material = Enum.Material.SmoothPlastic` and `Reflectance = 0.02`.
- Seal back hair flush (`z = 0.38`) so backlighting never leaks through head seams.

---

## 3. The Viral "In This World..." Visual & Editing Formula

1. **Classic Blocky Bodies + Cylindrical Head:**
   - Rectangular blocky torso (`2×2×1`) and limbs (`1×2×1`) with a classic cylindrical head (`SpecialMesh(Head)`).
2. **Textured Clothing & Expressive 2D Faces:**
   - Layered clothing details (hoodie pocket/drawstrings, plaid flannel strips, denim seams) and blinking 2D cartoon eyes with **white circular catchlights** + swapping mouth/eyebrow expressions (`Happy`, `Talking`, `Shocked`, `Sad`, `Scared`).
3. **Depth-of-Field + Voxel Environment:**
   - `DepthOfFieldEffect` (`FarIntensity = 0.65`, `InFocusRadius = 10`) blurs background houses and voxel cube trees so foreground characters pop like a Blender render.
4. **Fast Cuts (`1.5–2.5s`) + Literal Prop Close-Ups:**
   - Every noun mentioned in narration (wrist button, phone screen, framed hallway photo, clock tower, newspaper, pizza box) gets a dedicated 3D prop and an instant close-up cut (`FOV = 35–45`).
5. **1.0× Normal Voice Speed + Natural Breathing Pauses:**
   - Keep **Little Dude II** (`elevenlabs_fBD19tfE58bkETeiwUoC`) at **`speed="1"`** and **`0%` pitch shift**, using `<break time="0.75s" />` between sentences inside each scene so narration is never rushed and never has empty dead air while Suno BGM plays underneath.

---

## 4. End-to-End Production Workflow

### Phase 1: Generate Natural Voiceover + Suno BGM First
Always generate audio **first** so your 3D camera cuts match the exact spoken timing:

```powershell
# Check AI33.pro credits
python scripts/ai33_client.py credits

# Generate a scene voiceover with Little Dude II at 1.0x normal speed
python scripts/ai33_client.py tts "In this world, there is one rule everyone must follow. <break time='0.75s' /> Never look behind you after midnight." scene_01.mp3

# Generate 2 complementary Suno instrumental background music tracks (~6.5 min total)
python scripts/ai33_client.py bgm "Dark atmospheric horror suspense cinematic underscore, slow haunting minor piano, eerie low cello drone, no drums, instrumental" ./audio/suno_bgm
```

### Phase 2: Build World, Rigs & Director in Roblox Studio
Run `luau/rig_and_lighting_setup.luau` via `execute_luau(datamodel_type="Edit")` to:
- Strip `Atmosphere`, configure anti-glow `BloomEffect` + `DepthOfFieldEffect`,
- Spawn engine-native blocky characters with animated 2D faces,
- Install the `FilmDirector` `LocalScript` supporting `TimeScale`, `SeekTime`, and `SlateVisible` (fullscreen magenta sync slate).

### Phase 3: Hands-Free Zero-Drop Slow-Mo Capture (`TimeScale = 0.5`)
Unfocused Roblox Studio throttles to `15.0 fps (0 drops)`. Recording at `TimeScale = 0.5` captures **30 unique rendered frames per film second with 0 dropped frames**, which compiles cleanly into a 60fps MP4:

1. Start Play mode (`start_stop_play(is_start=True)`).
2. For each `12.0s` film section (`24.0s` real-time capture at `0.5x`), call in **one parallel turn**:
   - `video_capture(datamodel_type="Client", is_start=True)`
   - `execute_luau(Client)`:
     ```lua
     workspace:SetAttribute("TimeScale", 0.5)
     workspace:SetAttribute("SeekTime", nil)
     workspace:SetAttribute("SeekTime", 12.25)
     task.wait(0.05)
     workspace:SetAttribute("SlateVisible", false)
     return "GO"
     ```
   - Wait `30s`, then stop `video_capture(is_start=False)` and set `SlateVisible = true`.
3. Between captures (never run FFmpeg while recording!), verify and register each clip:
   ```powershell
   python scripts/compile_60fps_mcp.py add <idx> "<capture.mp4>" "<manifest.json>" 0.5 12.0 0.5
   ```
4. Stop Play mode (`start_stop_play(is_start=False)`) and compile all sections with black cinema bars (`h=58` top/bottom hiding all Roblox CoreGui icons):
   ```powershell
   python scripts/compile_60fps_mcp.py compile <num_sections> 60
   ```

### Phase 4: 3-Layer Stereo Sidechain Mix (Voice + Suno BGM + SFX)
Mix the centered voiceover, stereo Suno BGM (sidechain-ducked smoothly under speech), and synced SFX cues:
```powershell
ffmpeg -y -i voice.wav -i suno_bgm_stereo.wav -i sfx.wav -filter_complex `
  "[0:a]highpass=f=75,acompressor=threshold=-20dB:ratio=2.2:attack=10:release=140:makeup=2dB,volume=1.18,pan=stereo|c0=c0|c1=c0,asplit=3[v_mix][v_sc1][v_sc2]; `
   [1:a]volume=0.35[bgm_in];[bgm_in][v_sc1]sidechaincompress=threshold=0.03:ratio=2.3:attack=35:release=480:makeup=1[bgm_duck]; `
   [2:a]highpass=f=45,volume=0.50,pan=stereo|c0=c0|c1=c0[sfx_in];[sfx_in][v_sc2]sidechaincompress=threshold=0.03:ratio=3.2:attack=20:release=260:makeup=1[sfx_duck]; `
   [v_mix][bgm_duck][sfx_duck]amix=inputs=3:duration=longest:dropout_transition=0:normalize=0,alimiter=limit=0.95[out]" `
  -map "[out]" -ar 44100 -ac 2 master_mix.wav

ffmpeg -y -i silent_60fps.mp4 -i master_mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart Final_Movie_60fps.mp4
```

---

## 5. AI Prompts
See **[prompts/AI_PROMPTS.md](./prompts/AI_PROMPTS.md)** for ready-to-paste prompts for script generation, Roblox Studio MCP world building, slow-mo capture automation, and high-CTR YouTube thumbnails.
