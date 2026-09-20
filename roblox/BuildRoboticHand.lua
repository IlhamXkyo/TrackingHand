-- ==============================================================================
-- ROBLOX STUDIO: STANDALONE BIONIC HAND & PEDESTAL GENERATOR
-- Run this script in the Roblox Studio Command Bar to instantly build the complete
-- 107-component anatomical robotic hand, high-friction grip pads, and neon pedestal!
-- ==============================================================================

local hand = workspace:FindFirstChild("RoboticHand")
if hand then hand:Destroy() end

hand = Instance.new("Model")
hand.Name = "RoboticHand"
hand.Parent = workspace

local SCALE = 2.2
local basePos = Vector3.new(18, 0.5, 0)
local baseRot = CFrame.lookAt(basePos, Vector3.new(0, 0.5, 0)).Rotation

local function makePart(name, size, cf, color, mat, parent, shape)
    local p = Instance.new("Part")
    p.Name = name
    p.Size = size
    p.CFrame = cf
    p.Color = color
    p.Material = mat or Enum.Material.Metal
    p.Anchored = true
    p.CanCollide = false
    p.CastShadow = true
    if shape then p.Shape = shape end
    p.Parent = parent
    return p
end

-- 1. PEDESTAL & NEON RING
local pedestal = makePart("PedestalPlatform", Vector3.new(14 * SCALE * 0.45, 1.2 * SCALE, 14 * SCALE * 0.45), CFrame.new(basePos), Color3.fromRGB(28, 30, 36), Enum.Material.DiamondPlate, hand)
pedestal.CanCollide = true

local neonRing = makePart("PedestalNeonRing", Vector3.new(0.4 * SCALE, 12 * SCALE * 0.45, 12 * SCALE * 0.45), CFrame.new(basePos + Vector3.new(0, 0.7 * SCALE, 0)) * CFrame.Angles(0, 0, math.rad(90)), Color3.fromRGB(0, 230, 255), Enum.Material.Neon, hand, Enum.PartType.Cylinder)

-- 2. FOREARM & WRIST BALL
local forearmLocalY = 3.6
local curForearmCF = CFrame.new(basePos) * baseRot * CFrame.new(0, forearmLocalY * SCALE, 0)
makePart("ForearmCore", Vector3.new(1.8 * SCALE, 5.0 * SCALE, 1.8 * SCALE), curForearmCF, Color3.fromRGB(35, 38, 46), Enum.Material.Metal, hand)
makePart("ForearmBackPlate", Vector3.new(2.1 * SCALE, 4.8 * SCALE, 0.4 * SCALE), curForearmCF * CFrame.new(0, 0, 0.42 * SCALE), Color3.fromRGB(50, 55, 65), Enum.Material.DiamondPlate, hand)
makePart("PistonRodL", Vector3.new(0.35 * SCALE, 4.5 * SCALE, 0.35 * SCALE), curForearmCF * CFrame.new(-0.85 * SCALE, 0, 0.1 * SCALE), Color3.fromRGB(200, 205, 215), Enum.Material.Metal, hand, Enum.PartType.Cylinder)
makePart("PistonRodR", Vector3.new(0.35 * SCALE, 4.5 * SCALE, 0.35 * SCALE), curForearmCF * CFrame.new(0.85 * SCALE, 0, 0.1 * SCALE), Color3.fromRGB(200, 205, 215), Enum.Material.Metal, hand, Enum.PartType.Cylinder)
makePart("ForearmNeonStrip", Vector3.new(0.12 * SCALE, 4.4 * SCALE, 0.1 * SCALE), curForearmCF * CFrame.new(0, 0, -0.42 * SCALE), Color3.fromRGB(0, 230, 255), Enum.Material.Neon, hand)

local wristLocalY = forearmLocalY + 3.0
local wristPivotCF = CFrame.new(basePos) * baseRot * CFrame.new(0, wristLocalY * SCALE, 0)
makePart("WristBall", Vector3.new(1.5 * SCALE, 1.5 * SCALE, 1.5 * SCALE), wristPivotCF, Color3.fromRGB(220, 225, 235), Enum.Material.Metal, hand, Enum.PartType.Ball)
makePart("WristRing", Vector3.new(0.35 * SCALE, 2.0 * SCALE, 2.0 * SCALE), wristPivotCF * CFrame.Angles(0, 0, math.rad(90)), Color3.fromRGB(0, 230, 255), Enum.Material.Neon, hand, Enum.PartType.Cylinder)

-- 3. PALM CHASSIS & ARMOR
local curPalmCF = wristPivotCF * CFrame.new(0, 2.0 * SCALE, 0)
makePart("PalmBody", Vector3.new(2.4 * SCALE, 2.6 * SCALE, 0.75 * SCALE), curPalmCF, Color3.fromRGB(35, 38, 46), Enum.Material.Metal, hand)
makePart("PalmThenar", Vector3.new(1.1 * SCALE, 1.4 * SCALE, 0.7 * SCALE), curPalmCF * CFrame.new(-0.98 * SCALE, -0.42 * SCALE, -0.22 * SCALE) * CFrame.Angles(math.rad(12), math.rad(22), math.rad(24)), Color3.fromRGB(48, 52, 62), Enum.Material.Metal, hand)
makePart("PalmHypothenar", Vector3.new(0.85 * SCALE, 1.3 * SCALE, 0.65 * SCALE), curPalmCF * CFrame.new(1.05 * SCALE, -0.4 * SCALE, -0.1 * SCALE) * CFrame.Angles(0, 0, math.rad(-6)), Color3.fromRGB(48, 52, 62), Enum.Material.Metal, hand)

local gripPad = makePart("PalmGripPad", Vector3.new(2.1 * SCALE, 2.2 * SCALE, 0.12 * SCALE), curPalmCF * CFrame.new(0, 0.1 * SCALE, -0.38 * SCALE), Color3.fromRGB(20, 22, 25), Enum.Material.Rubber, hand)
gripPad.CanCollide = true
gripPad.CustomPhysicalProperties = PhysicalProperties.new(1.5, 2.5, 0.0, 2.0, 1.0)

makePart("PalmBackArmor", Vector3.new(2.2 * SCALE, 2.3 * SCALE, 0.16 * SCALE), curPalmCF * CFrame.new(0, 0, 0.42 * SCALE), Color3.fromRGB(60, 65, 75), Enum.Material.DiamondPlate, hand)
makePart("PalmBackNeon", Vector3.new(0.7 * SCALE, 0.7 * SCALE, 0.08 * SCALE), curPalmCF * CFrame.new(0, 0.2 * SCALE, 0.52 * SCALE), Color3.fromRGB(0, 230, 255), Enum.Material.Neon, hand)

-- 4. FINGERS (Index, Middle, Ring, Pinky)
local fingersFolder = Instance.new("Folder")
fingersFolder.Name = "Fingers"
fingersFolder.Parent = hand

local fingerConfigs = {
    Index  = {x = -0.74, y = 1.35, z = -0.06, baseSpread = math.rad(6),   lengths = {1.35, 1.0, 0.78},  w = 0.46},
    Middle = {x = -0.22, y = 1.50, z = 0.00,  baseSpread = 0,             lengths = {1.55, 1.15, 0.90}, w = 0.48},
    Ring   = {x = 0.34,  y = 1.38, z = -0.05, baseSpread = math.rad(-6),  lengths = {1.40, 1.05, 0.82}, w = 0.46},
    Pinky  = {x = 0.86,  y = 1.15, z = -0.10, baseSpread = math.rad(-14), lengths = {1.10, 0.80, 0.65}, w = 0.40},
}

for fName, cfg in pairs(fingerConfigs) do
    local fFolder = Instance.new("Folder")
    fFolder.Name = fName
    fFolder.Parent = fingersFolder
    
    local cf = curPalmCF * CFrame.new(cfg.x * SCALE, cfg.y * SCALE, cfg.z * SCALE) * CFrame.Angles(0, 0, cfg.baseSpread)
    
    for seg = 1, 3 do
        local sLen = cfg.lengths[seg] * SCALE
        local sW = (cfg.w * (1 - (seg-1)*0.08)) * SCALE
        
        makePart(fName .. "_Knuckle" .. seg, Vector3.new(sW * 1.08, sW * 1.08, sW * 1.08), cf, Color3.fromRGB(210, 215, 225), Enum.Material.Metal, fFolder, Enum.PartType.Ball)
        
        local rCF = cf * CFrame.new(0, sLen / 2, 0)
        makePart(fName .. "_Ruas" .. seg, Vector3.new(sW, sLen, sW), rCF, Color3.fromRGB(42, 45, 52), Enum.Material.Metal, fFolder)
        
        local pad = makePart(fName .. "_GripPad" .. seg, Vector3.new(sW * 0.88, sLen * 0.88, 0.08 * SCALE), rCF * CFrame.new(0, 0, -sW / 2 - 0.04 * SCALE), Color3.fromRGB(22, 24, 28), Enum.Material.Rubber, fFolder)
        pad.CanCollide = true
        pad.CustomPhysicalProperties = PhysicalProperties.new(1.5, 2.5, 0.0, 2.0, 1.0)
        
        makePart(fName .. "_Armor" .. seg, Vector3.new(sW * 0.92, sLen * 0.82, 0.12 * SCALE), rCF * CFrame.new(0, 0, sW / 2 + 0.06 * SCALE), Color3.fromRGB(65, 70, 80), Enum.Material.Metal, fFolder)
        makePart(fName .. "_Neon" .. seg, Vector3.new(0.08 * SCALE, sLen * 0.70, 0.06 * SCALE), rCF * CFrame.new(0, 0, sW / 2 + 0.14 * SCALE), Color3.fromRGB(0, 230, 255), Enum.Material.Neon, fFolder)
        
        if seg == 3 then
            local tipCF = cf * CFrame.new(0, sLen + 0.12 * SCALE, 0)
            makePart(fName .. "_SensorTip", Vector3.new(sW * 0.85, 0.24 * SCALE, sW * 0.85), tipCF, Color3.fromRGB(55, 60, 70), Enum.Material.Metal, fFolder, Enum.PartType.Ball)
            makePart(fName .. "_Optic", Vector3.new(sW * 0.55, 0.08 * SCALE, 0.10 * SCALE), tipCF * CFrame.new(0, 0.08 * SCALE, -sW * 0.25), Color3.fromRGB(0, 230, 255), Enum.Material.Neon, fFolder)
        end
        
        cf = cf * CFrame.new(0, sLen, 0)
    end
end

-- 5. THUMB (Anatomical 3-Segment Ray)
local thumbFolder = Instance.new("Folder")
thumbFolder.Name = "Thumb"
thumbFolder.Parent = fingersFolder

local thumbLengths = {0.95 * SCALE, 1.15 * SCALE, 0.95 * SCALE}
local thumbWidths = {0.54 * SCALE, 0.50 * SCALE, 0.44 * SCALE}
local thumbNames = {"Thumb_Metacarpal", "Thumb_Ruas1", "Thumb_Ruas2"}

local cmcOrigin = curPalmCF * CFrame.new(-1.08 * SCALE, -0.42 * SCALE, -0.32 * SCALE)
local cmcRot = CFrame.Angles(0, 0, math.rad(28))
    * CFrame.Angles(-math.rad(26), 0, 0)
    * CFrame.Angles(0, math.rad(-75), 0)

local thbCF = cmcOrigin * cmcRot.Rotation

for seg = 1, 3 do
    local sLen = thumbLengths[seg]
    local sW = thumbWidths[seg]
    local bName = thumbNames[seg]
    
    makePart("Thumb_Knuckle" .. seg, Vector3.new(sW * 1.05, sW * 1.05, sW * 1.05), thbCF, Color3.fromRGB(210, 215, 225), Enum.Material.Metal, thumbFolder, Enum.PartType.Ball)
    
    local rCF = thbCF * CFrame.new(0, sLen / 2, 0)
    makePart(bName, Vector3.new(sW, sLen, sW), rCF, Color3.fromRGB(42, 45, 52), Enum.Material.Metal, thumbFolder)
    
    local pad = makePart(bName .. "_GripPad", Vector3.new(sW * 0.88, sLen * 0.88, 0.08 * SCALE), rCF * CFrame.new(0, 0, -sW / 2 - 0.04 * SCALE), Color3.fromRGB(22, 24, 28), Enum.Material.Rubber, thumbFolder)
    pad.CanCollide = true
    pad.CustomPhysicalProperties = PhysicalProperties.new(1.5, 2.5, 0.0, 2.0, 1.0)
    
    makePart(bName .. "_Armor", Vector3.new(sW * 0.92, sLen * 0.82, 0.12 * SCALE), rCF * CFrame.new(0, 0, sW / 2 + 0.06 * SCALE), Color3.fromRGB(65, 70, 80), Enum.Material.Metal, thumbFolder)
    makePart(bName .. "_Neon", Vector3.new(0.08 * SCALE, sLen * 0.70, 0.06 * SCALE), rCF * CFrame.new(0, 0, sW / 2 + 0.14 * SCALE), Color3.fromRGB(0, 230, 255), Enum.Material.Neon, thumbFolder)
    
    if seg == 3 then
        local tipCF = thbCF * CFrame.new(0, sLen + 0.12 * SCALE, 0)
        makePart("Thumb_SensorTip", Vector3.new(sW * 0.85, 0.24 * SCALE, sW * 0.85), tipCF, Color3.fromRGB(55, 60, 70), Enum.Material.Metal, thumbFolder, Enum.PartType.Ball)
        makePart("Thumb_Optic", Vector3.new(sW * 0.55, 0.08 * SCALE, 0.10 * SCALE), tipCF * CFrame.new(0, 0.08 * SCALE, -sW * 0.25), Color3.fromRGB(0, 230, 255), Enum.Material.Neon, thumbFolder)
    end
    
    thbCF = thbCF * CFrame.new(0, sLen, 0)
end

print("[RoboticHand Generator] Complete 107-component RoboticHand built successfully at Vector3.new(18, 0.5, 0)!")
