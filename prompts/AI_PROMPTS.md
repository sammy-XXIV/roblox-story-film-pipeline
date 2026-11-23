# Copy-Paste AI Prompts for Roblox Story & Horror Films

Use these prompts directly with your AI agent (Antigravity / Claude Code / Cursor) connected to the **Roblox Studio MCP** server.

---

## 1. Master End-to-End Production Prompt

```text
Use the roblox-horror-film-pipeline skill to produce a full animated 3D Roblox story video titled:
"IN THIS WORLD, [YOUR PREMISE HERE]"

Follow the exact 4-phase production order:
1. AUDIO FIRST (1.0x Normal Speed):
   - Break the script into 14-16 contiguous scenes.
   - Generate the voiceover using AI33.pro v3 (`elevenlabs_fBD19tfE58bkETeiwUoC` - Little Dude II) at 1.0x normal speed, 0% pitch shift, with natural `<break time="0.75s" />` pauses between sentences so speech is never rushed.
   - Generate a 2-track instrumental background music score via AI33.pro Suno (`/v1s/task/music-generation`) and crossfade them seamlessly across the full runtime.
   - Build a synced procedural SFX track matching every story cue.

2. ROBLOX WORLD & RIGS ("In This World" Viral Style + All Bug Fixes):
   - Build classic blocky rectangular R6/R15 characters (block torso/limbs + SpecialMesh(Head) on Head only) with 0 MeshParts and 0 external FileMeshes so limbs never turn invisible.
   - Add layered clothing details, 3D hair, and expressive 2D cartoon FaceGuis (glossy black eyes with white circular catchlights + blinking/talking/shocked expressions).
   - Apply the anti-glow lighting calibration (`Bloom.Threshold = 2.4`, `Intensity = 0.20`, no RimLights, `PointLight.Brightness <= 2.0`, skin `Reflectance = 0.02`, flush back hair `z = 0.38`).
   - Never add `Lighting.Atmosphere` (use classic FogStart/FogEnd + `DepthOfFieldEffect` with `FarIntensity = 0.65` so background voxel trees and pastel houses blur softly behind the characters).
   - Build dedicated close-up 3D props for every key noun mentioned in the narration (with UIPadding on all SurfaceGuis so text never clips).

3. BEAT-SYNCED DIRECTOR & ZERO-DROP 60FPS CAPTURE:
   - Cut cameras every 1.5-3.5s with extreme close-up prop inserts synced to the exact Phase 1 voice timestamps.
   - Record hands-free via MCP `video_capture` at `TimeScale = 0.5` in 12s film sections (verifying 0 dropped frames and non-grey center-crop spread between captures, never running FFmpeg during an active capture).
   - Stop Play mode and compile to 1280x720 60fps H.264 MP4 with pure-black cinema bars (`h=58` top/bottom hiding all CoreGui icons).

4. STEREO 3-LAYER MIX, QA, THUMBNAIL & CLEANUP:
   - Mix centered 1.0x voice + sidechain-ducked stereo Suno BGM + synced SFX (`mean ~ -18.5 dB`, `peak -0.4 dB`).
   - Extract 4 check frames to visually verify 0 glow, 0 invisible parts, and readable props.
   - Generate a 1280x720 YouTube thumbnail and clean up all temporary clips, frames, and MCP capture caches.
```

---

## 2. Pre-Flight Bug Audit Prompt (Run Before Recording)

```text
Run a pre-flight Luau audit in Roblox Studio (`Edit` DataModel) across `Lighting` and every character model in our world:
1. Confirm `Lighting:FindFirstChildOfClass("Atmosphere") == nil` (delete it if present and use FogStart/FogEnd + DepthOfFieldEffect).
2. Confirm `BloomEffect.Threshold >= 2.4` and `BloomEffect.Intensity <= 0.22`, and verify no `PointLight` or `SpotLight` near characters exceeds `Brightness = 2.0`.
3. Confirm every character has `0` `MeshPart`s, `0` external `FileMesh`es, skin `Reflectance <= 0.02`, intact `Motor6D` joints, `FaceGui` enabled on `Head.Front`, and `0` unexpected invisible parts.
4. Take a `screen_capture` in Play mode and verify via `read_file` before starting batch `video_capture`.
```

---

## 3. High-CTR YouTube Thumbnail Prompts

### Format A: 3-Panel / 4-Panel "In This World" Story Split (No Title Text)
```text
Generate a 16:9 YouTube thumbnail (1280x720) split into 3 vertical side-by-side panels in the viral "In This World" 3D Roblox story style:
- Classic blocky rectangular Roblox limbs/torso, cylindrical head, 3D hair, expressive 2D cartoon eyes with white catchlights, soft Depth-of-Field background blur, vibrant daylight lighting.
- Panel 1 (left): [Scene 1 moment] with a single bold white black-outlined caption word "[WORD 1]" at lower center.
- Panel 2 (middle): [Scene 2 moment - shocked reaction] with a single bold white black-outlined caption word "[WORD 2]" at lower center.
- Panel 3 (right): [Scene 3 twist/climax tease] with a single bold red/yellow black-outlined caption word "[WORD 3]" at lower center.
No big banner text, no Roblox UI icons.
```

### Format B: Single Emotional Scene + Top White Banner
```text
Generate a 16:9 YouTube thumbnail (1280x720) showing a single dramatic 3D Roblox story scene:
- Center foreground: A classic blocky 3D Roblox character with big expressive cartoon eyes and tearful/shocked expression in [key story setting], lit with high-clarity cinematic lighting and soft Depth-of-Field background blur.
- Top banner: Full-width semi-transparent dark bar across the very top with bold uppercase white sans-serif text reading: "[SHORT 4-WORD HOOK]".
```

### Format C: Dark Night / Horror Confrontation
```text
Generate a 16:9 YouTube thumbnail (1280x720) for a 3D Roblox horror story:
- Foreground right: A terrified 3D Roblox character under a warm amber streetlamp on a foggy night street.
- Directly behind their left shoulder emerging from black mist: A shadowy Roblox doppelganger with hollow glowing white eyes and an eerie wide grin reaching toward their shoulder.
- Background left: Dark houses and a glowing red clock tower reading "12:00".
- Upper-left typography: Bold distressed white and blood-red text reading "DON'T LOOK BACK" with "12:00 AM" below.
```
