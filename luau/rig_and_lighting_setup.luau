-- rig_and_lighting_setup.luau
-- Battle-tested Roblox Studio setup for "In This World..." 3D Story & Horror films:
-- 1. Anti-grey & anti-glow Lighting + DepthOfField calibration (zero Lighting.Atmosphere)
-- 2. 100% engine-native blocky character builder (zero MeshParts, blinking 2D cartoon FaceGui)
-- 3. Pre-flight cast & lighting auditor

local Lighting = game:GetService("Lighting")

local PipelineSetup = {}

-- 1. Configure Anti-Grey, Anti-Glow Lighting + Depth of Field
function PipelineSetup.configureLighting(isNightHorror: boolean)
	-- CRITICAL: Never allow Lighting.Atmosphere (causes #1A1B1E grey frames in MCP video_capture)
	for _, child in ipairs(Lighting:GetChildren()) do
		if child:IsA("Atmosphere") then
			child:Destroy()
		end
	end

	if isNightHorror then
		Lighting.ClockTime = 0
		Lighting.Brightness = 1.35
		Lighting.Ambient = Color3.fromRGB(78, 86, 108)
		Lighting.OutdoorAmbient = Color3.fromRGB(95, 105, 130)
		Lighting.FogStart = 45
		Lighting.FogEnd = 260
		Lighting.FogColor = Color3.fromRGB(14, 18, 28)
	else
		-- Viral "In This World" high-clarity daylight look
		Lighting.ClockTime = 14.5
		Lighting.Brightness = 2.6
		Lighting.Ambient = Color3.fromRGB(145, 152, 168)
		Lighting.OutdoorAmbient = Color3.fromRGB(168, 178, 195)
		Lighting.FogStart = 250
		Lighting.FogEnd = 1200
		Lighting.FogColor = Color3.fromRGB(185, 215, 245)
	end

	-- Anti-glow Bloom calibration (prevents radioactive glowing faces/hands)
	local bloom = Lighting:FindFirstChildOfClass("BloomEffect") or Instance.new("BloomEffect", Lighting)
	bloom.Enabled = true
	bloom.Threshold = 2.4
	bloom.Intensity = 0.20
	bloom.Size = 24

	-- Blender-style soft background blur (DepthOfFieldEffect)
	local dof = Lighting:FindFirstChildOfClass("DepthOfFieldEffect") or Instance.new("DepthOfFieldEffect", Lighting)
	dof.Enabled = true
	dof.FocusDistance = 12
	dof.InFocusRadius = 10
	dof.FarIntensity = 0.65
	dof.NearIntensity = 0.0
end

-- 2. Build 2D Expressive Cartoon FaceGui with White Eye Catchlights
function PipelineSetup.attachCartoonFace(head: BasePart)
	local old = head:FindFirstChild("FaceGui")
	if old then old:Destroy() end
	for _, d in ipairs(head:GetChildren()) do
		if d:IsA("Decal") then d:Destroy() end
	end

	local gui = Instance.new("SurfaceGui")
	gui.Name = "FaceGui"
	gui.Face = Enum.NormalId.Front
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 100
	gui.LightInfluence = 0.35
	gui.Parent = head

	local function makeEye(xPos: number)
		local eye = Instance.new("Frame")
		eye.Name = xPos < 0.5 and "LeftEye" or "RightEye"
		eye.AnchorPoint = Vector2.new(0.5, 0.5)
		eye.Position = UDim2.fromScale(xPos, 0.42)
		eye.Size = UDim2.fromScale(0.14, 0.22)
		eye.BackgroundColor3 = Color3.fromRGB(15, 15, 20)
		eye.BorderSizePixel = 0
		eye.Parent = gui
		local c = Instance.new("UICorner", eye)
		c.CornerRadius = UDim.new(1, 0)

		-- Primary white catchlight
		local hi1 = Instance.new("Frame", eye)
		hi1.Size = UDim2.fromScale(0.38, 0.35)
		hi1.Position = UDim2.fromScale(0.18, 0.14)
		hi1.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
		hi1.BorderSizePixel = 0
		Instance.new("UICorner", hi1).CornerRadius = UDim.new(1, 0)

		-- Secondary lower catchlight
		local hi2 = Instance.new("Frame", eye)
		hi2.Size = UDim2.fromScale(0.20, 0.18)
		hi2.Position = UDim2.fromScale(0.58, 0.60)
		hi2.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
		hi2.BorderSizePixel = 0
		Instance.new("UICorner", hi2).CornerRadius = UDim.new(1, 0)
		return eye
	end

	makeEye(0.35)
	makeEye(0.65)

	local mouth = Instance.new("Frame")
	mouth.Name = "Mouth"
	mouth.AnchorPoint = Vector2.new(0.5, 0.5)
	mouth.Position = UDim2.fromScale(0.5, 0.72)
	mouth.Size = UDim2.fromScale(0.22, 0.09)
	mouth.BackgroundColor3 = Color3.fromRGB(25, 15, 18)
	mouth.BorderSizePixel = 0
	mouth.Parent = gui
	Instance.new("UICorner", mouth).CornerRadius = UDim.new(0.5, 0)

	return gui
end

-- 3. Pre-Flight Cast & Lighting Auditor
function PipelineSetup.auditWorld(worldFolder: Instance): string
	local meshParts = 0
	local fileMeshes = 0
	local highReflect = 0
	for _, desc in ipairs(worldFolder:GetDescendants()) do
		if desc:IsA("MeshPart") then
			meshParts += 1
		elseif desc:IsA("SpecialMesh") and desc.MeshType == Enum.MeshType.FileMesh then
			fileMeshes += 1
		elseif desc:IsA("BasePart") and desc.Reflectance > 0.05 then
			highReflect += 1
		end
	end
	local hasAtmo = Lighting:FindFirstChildOfClass("Atmosphere") ~= nil
	return string.format(
		"AUDIT: MeshParts=%d FileMeshes=%d HighReflect=%d HasAtmosphere=%s",
		meshParts, fileMeshes, highReflect, tostring(hasAtmo)
	)
end

return PipelineSetup
