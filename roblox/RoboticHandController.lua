-- Ultra-Stable Anatomical Robotic Hand Controller
-- Clean High-Precision Stationary Pedestal Edition
-- Rate-Limit Safe: ~7.1 req/sec (< 500 req/min Roblox HttpService quota)

local HttpService = game:GetService("HttpService")
local RunService = game:GetService("RunService")

local hand = workspace:WaitForChild("RoboticHand", 10)
if not hand then
    warn("[RoboticHandController] RoboticHand not found in workspace!")
    return
end

local SCALE = 2.2
local palm = hand:WaitForChild("PalmBody")
local wristBall = hand:WaitForChild("WristBall")
local wristRing = hand:WaitForChild("WristRing")

local forearmCore = hand:WaitForChild("ForearmCore")
local forearmBackPlate = hand:WaitForChild("ForearmBackPlate")
local pistonRodL = hand:WaitForChild("PistonRodL")
local pistonRodR = hand:WaitForChild("PistonRodR")
local forearmNeon = hand:WaitForChild("ForearmNeonStrip")

local thenar = hand:WaitForChild("PalmThenar")
local hypo = hand:WaitForChild("PalmHypothenar")
local gripPad = hand:WaitForChild("PalmGripPad")
local backArmor = hand:WaitForChild("PalmBackArmor")
local backNeon = hand:WaitForChild("PalmBackNeon")

local basePos = Vector3.new(18, 0.5, 0)
local baseRot = CFrame.lookAt(basePos, Vector3.new(0, 0.5, 0)).Rotation

local forearmLocalY = 3.6
local wristLocalY = forearmLocalY + 3.0
local wristPivotCF = CFrame.new(basePos) * baseRot * CFrame.new(0, wristLocalY * SCALE, 0)

-- Four fingers configuration
local fingerConfigs = {
    Index  = {x = -0.74, y = 1.35, z = -0.06, baseSpread = math.rad(6),   lengths = {1.35, 1.0, 0.78},  w = 0.46},
    Middle = {x = -0.22, y = 1.50, z = 0.00,  baseSpread = 0,             lengths = {1.55, 1.15, 0.90}, w = 0.48},
    Ring   = {x = 0.34,  y = 1.38, z = -0.05, baseSpread = math.rad(-6),  lengths = {1.40, 1.05, 0.82}, w = 0.46},
    Pinky  = {x = 0.86,  y = 1.15, z = -0.10, baseSpread = math.rad(-14), lengths = {1.10, 0.80, 0.65}, w = 0.40},
}

local fingerParts = {}
local fingersFolder = hand:WaitForChild("Fingers")

for fName, cfg in pairs(fingerConfigs) do
    local fFolder = fingersFolder:WaitForChild(fName)
    fingerParts[fName] = {
        cfg = cfg,
        knuckles = {
            fFolder:WaitForChild(fName .. "_Knuckle1"),
            fFolder:WaitForChild(fName .. "_Knuckle2"),
            fFolder:WaitForChild(fName .. "_Knuckle3"),
        },
        ruas = {
            fFolder:WaitForChild(fName .. "_Ruas1"),
            fFolder:WaitForChild(fName .. "_Ruas2"),
            fFolder:WaitForChild(fName .. "_Ruas3"),
        },
        gripPads = {
            fFolder:WaitForChild(fName .. "_GripPad1"),
            fFolder:WaitForChild(fName .. "_GripPad2"),
            fFolder:WaitForChild(fName .. "_GripPad3"),
        },
        armors = {
            fFolder:WaitForChild(fName .. "_Armor1"),
            fFolder:WaitForChild(fName .. "_Armor2"),
            fFolder:WaitForChild(fName .. "_Armor3"),
        },
        neons = {
            fFolder:WaitForChild(fName .. "_Neon1"),
            fFolder:WaitForChild(fName .. "_Neon2"),
            fFolder:WaitForChild(fName .. "_Neon3"),
        },
        sensorTip = fFolder:WaitForChild(fName .. "_SensorTip"),
        optic = fFolder:WaitForChild(fName .. "_Optic"),
    }
end

local thumbFolder = fingersFolder:WaitForChild("Thumb")
local thumbParts = {
    lengths = {0.95 * SCALE, 1.15 * SCALE, 0.95 * SCALE},
    widths = {0.54 * SCALE, 0.50 * SCALE, 0.44 * SCALE},
    knuckles = {
        thumbFolder:WaitForChild("Thumb_Knuckle1"),
        thumbFolder:WaitForChild("Thumb_Knuckle2"),
        thumbFolder:WaitForChild("Thumb_Knuckle3"),
    },
    ruas = {
        thumbFolder:WaitForChild("Thumb_Metacarpal"),
        thumbFolder:WaitForChild("Thumb_Ruas1"),
        thumbFolder:WaitForChild("Thumb_Ruas2"),
    },
    gripPads = {
        thumbFolder:WaitForChild("Thumb_Metacarpal_GripPad"),
        thumbFolder:WaitForChild("Thumb_Ruas1_GripPad"),
        thumbFolder:WaitForChild("Thumb_Ruas2_GripPad"),
    },
    armors = {
        thumbFolder:WaitForChild("Thumb_Metacarpal_Armor"),
        thumbFolder:WaitForChild("Thumb_Ruas1_Armor"),
        thumbFolder:WaitForChild("Thumb_Ruas2_Armor"),
    },
    neons = {
        thumbFolder:WaitForChild("Thumb_Metacarpal_Neon"),
        thumbFolder:WaitForChild("Thumb_Ruas1_Neon"),
        thumbFolder:WaitForChild("Thumb_Ruas2_Neon"),
    },
    sensorTip = thumbFolder:WaitForChild("Thumb_SensorTip"),
    optic = thumbFolder:WaitForChild("Thumb_Optic"),
}

local current = {
    wrist = {pitch = 0, yaw = 0, roll = 0},
    thumb = {cmc_spread = 0.5, cmc_oppose = 0.0, mcp_flex = 0.0, ip_flex = 0.0},
    index = {curl1 = 0, curl2 = 0, curl3 = 0, spread = 0},
    middle = {curl1 = 0, curl2 = 0, curl3 = 0},
    ring = {curl1 = 0, curl2 = 0, curl3 = 0, spread = 0},
    pinky = {curl1 = 0, curl2 = 0, curl3 = 0, spread = 0},
}

local target = {
    wrist = {pitch = 0, yaw = 0, roll = 0},
    thumb = {cmc_spread = 0.5, cmc_oppose = 0.0, mcp_flex = 0.0, ip_flex = 0.0},
    index = {curl1 = 0, curl2 = 0, curl3 = 0, spread = 0},
    middle = {curl1 = 0, curl2 = 0, curl3 = 0},
    ring = {curl1 = 0, curl2 = 0, curl3 = 0, spread = 0},
    pinky = {curl1 = 0, curl2 = 0, curl3 = 0, spread = 0},
}

local HTTP_URL = "http://127.0.0.1:8080/hand"

-- Polling task
task.spawn(function()
    print("[RoboticHandController] High-Precision Controller polling from " .. HTTP_URL)
    while true do
        local ok, res = pcall(function()
            return HttpService:GetAsync(HTTP_URL)
        end)
        
        if ok and res and #res > 0 then
            local parseOk, data = pcall(function()
                return HttpService:JSONDecode(res)
            end)
            
            if parseOk and data and data.detected then
                if data.wrist then
                    target.wrist.pitch = data.wrist.pitch or 0
                    target.wrist.yaw = data.wrist.yaw or 0
                    target.wrist.roll = data.wrist.roll or 0
                end
                if data.thumb then
                    target.thumb.cmc_spread = data.thumb.cmc_spread or data.thumb.spread or 0.5
                    target.thumb.cmc_oppose = data.thumb.cmc_oppose or 0.0
                    target.thumb.mcp_flex = data.thumb.mcp_flex or data.thumb.curl1 or 0.0
                    target.thumb.ip_flex = data.thumb.ip_flex or data.thumb.curl2 or 0.0
                end
                if data.index then
                    target.index.curl1 = data.index.curl1 or 0
                    target.index.curl2 = data.index.curl2 or 0
                    target.index.curl3 = data.index.curl3 or 0
                    target.index.spread = data.index.spread or 0
                end
                if data.middle then
                    target.middle.curl1 = data.middle.curl1 or 0
                    target.middle.curl2 = data.middle.curl2 or 0
                    target.middle.curl3 = data.middle.curl3 or 0
                end
                if data.ring then
                    target.ring.curl1 = data.ring.curl1 or 0
                    target.ring.curl2 = data.ring.curl2 or 0
                    target.ring.curl3 = data.ring.curl3 or 0
                    target.ring.spread = data.ring.spread or 0
                end
                if data.pinky then
                    target.pinky.curl1 = data.pinky.curl1 or 0
                    target.pinky.curl2 = data.pinky.curl2 or 0
                    target.pinky.curl3 = data.pinky.curl3 or 0
                    target.pinky.spread = data.pinky.spread or 0
                end
            end
            task.wait(0.14) -- 7.1 req/sec
        else
            task.wait(0.4)
        end
    end
end)

local function lerp(a, b, t)
    return a + (b - a) * math.clamp(t, 0, 1)
end

-- 60 FPS Heartbeat Loop
RunService.Heartbeat:Connect(function(dt)
    local speed = dt * 15
    
    current.wrist.pitch = lerp(current.wrist.pitch, target.wrist.pitch, speed)
    current.wrist.yaw = lerp(current.wrist.yaw, target.wrist.yaw, speed)
    current.wrist.roll = lerp(current.wrist.roll, target.wrist.roll, speed)
    
    current.thumb.cmc_spread = lerp(current.thumb.cmc_spread, target.thumb.cmc_spread, speed)
    current.thumb.cmc_oppose = lerp(current.thumb.cmc_oppose, target.thumb.cmc_oppose, speed)
    current.thumb.mcp_flex = lerp(current.thumb.mcp_flex, target.thumb.mcp_flex, speed)
    current.thumb.ip_flex = lerp(current.thumb.ip_flex, target.thumb.ip_flex, speed)
    
    current.index.curl1 = lerp(current.index.curl1, target.index.curl1, speed)
    current.index.curl2 = lerp(current.index.curl2, target.index.curl2, speed)
    current.index.curl3 = lerp(current.index.curl3, target.index.curl3, speed)
    current.index.spread = lerp(current.index.spread, target.index.spread, speed)
    
    current.middle.curl1 = lerp(current.middle.curl1, target.middle.curl1, speed)
    current.middle.curl2 = lerp(current.middle.curl2, target.middle.curl2, speed)
    current.middle.curl3 = lerp(current.middle.curl3, target.middle.curl3, speed)
    
    current.ring.curl1 = lerp(current.ring.curl1, target.ring.curl1, speed)
    current.ring.curl2 = lerp(current.ring.curl2, target.ring.curl2, speed)
    current.ring.curl3 = lerp(current.ring.curl3, target.ring.curl3, speed)
    current.ring.spread = lerp(current.ring.spread, target.ring.spread, speed)
    
    current.pinky.curl1 = lerp(current.pinky.curl1, target.pinky.curl1, speed)
    current.pinky.curl2 = lerp(current.pinky.curl2, target.pinky.curl2, speed)
    current.pinky.curl3 = lerp(current.pinky.curl3, target.pinky.curl3, speed)
    current.pinky.spread = lerp(current.pinky.spread, target.pinky.spread, speed)
    
    -- 1. Forearm & Dynamic Wrist Position
    local curForearmCF = CFrame.new(basePos) * baseRot * CFrame.new(0, forearmLocalY * SCALE, 0)
    forearmCore.CFrame = curForearmCF
    forearmBackPlate.CFrame = curForearmCF * CFrame.new(0, 0, 0.42 * SCALE)
    pistonRodL.CFrame = curForearmCF * CFrame.new(-0.85 * SCALE, 0, 0.1 * SCALE)
    pistonRodR.CFrame = curForearmCF * CFrame.new(0.85 * SCALE, 0, 0.1 * SCALE)
    forearmNeon.CFrame = curForearmCF * CFrame.new(0, 0, -0.42 * SCALE)
    
    local wristRot = CFrame.Angles(-current.wrist.pitch * 0.85, current.wrist.yaw * 0.85, -current.wrist.roll * 0.85)
    local curWristCF = wristPivotCF * wristRot
    
    wristBall.CFrame = curWristCF
    wristRing.CFrame = curWristCF * CFrame.Angles(0, 0, math.rad(90))
    
    local curPalmCF = curWristCF * CFrame.new(0, 2.0 * SCALE, 0)
    palm.CFrame = curPalmCF
    
    thenar.CFrame = curPalmCF * CFrame.new(-0.98 * SCALE, -0.42 * SCALE, -0.22 * SCALE) * CFrame.Angles(math.rad(12), math.rad(22), math.rad(24))
    hypo.CFrame = curPalmCF * CFrame.new(1.05 * SCALE, -0.4 * SCALE, -0.1 * SCALE) * CFrame.Angles(0, 0, math.rad(-6))
    gripPad.CFrame = curPalmCF * CFrame.new(0, 0.1 * SCALE, -0.38 * SCALE)
    backArmor.CFrame = curPalmCF * CFrame.new(0, 0, 0.42 * SCALE)
    backNeon.CFrame = curPalmCF * CFrame.new(0, 0.2 * SCALE, 0.52 * SCALE)
    
    -- 2. Four Fingers Kinematics
    for fName, fData in pairs(fingerParts) do
        local cfg = fData.cfg
        local curls = current[fName:lower()]
        local dynSpread = curls.spread or 0
        local totalSpread = cfg.baseSpread - (dynSpread * 1.2)
        
        local cf = curPalmCF * CFrame.new(cfg.x * SCALE, cfg.y * SCALE, cfg.z * SCALE) * CFrame.Angles(0, 0, totalSpread)
        
        for seg = 1, 3 do
            local sLen = cfg.lengths[seg] * SCALE
            local sW = (cfg.w * (1 - (seg-1)*0.08)) * SCALE
            local curlVal = (seg == 1 and curls.curl1) or (seg == 2 and curls.curl2) or curls.curl3
            
            fData.knuckles[seg].CFrame = cf
            cf = cf * CFrame.Angles(-curlVal, 0, 0)
            
            local rCF = cf * CFrame.new(0, sLen / 2, 0)
            fData.ruas[seg].CFrame = rCF
            
            fData.gripPads[seg].CFrame = rCF * CFrame.new(0, 0, -sW / 2 - 0.04 * SCALE)
            fData.armors[seg].CFrame = rCF * CFrame.new(0, 0, sW / 2 + 0.06 * SCALE)
            fData.neons[seg].CFrame = rCF * CFrame.new(0, 0, sW / 2 + 0.14 * SCALE)
            
            if seg == 3 then
                local tipCF = cf * CFrame.new(0, sLen + 0.12 * SCALE, 0)
                fData.sensorTip.CFrame = tipCF
                fData.optic.CFrame = tipCF * CFrame.new(0, 0.08 * SCALE, -sW * 0.25)
            end
            
            cf = cf * CFrame.new(0, sLen, 0)
        end
    end
    
    -- 3. Anatomical Thumb Kinematics
    local cmcOrigin = curPalmCF * CFrame.new(-1.08 * SCALE, -0.42 * SCALE, -0.32 * SCALE)
    local dynSpread = (current.thumb.cmc_spread - 0.5) * math.rad(28)
    local dynOppose = current.thumb.cmc_oppose * math.rad(30)
    
    local cmcRot = CFrame.Angles(0, 0, math.rad(28) + dynSpread)
        * CFrame.Angles(-math.rad(26) - dynOppose * 0.4, dynOppose * 0.6, 0)
        * CFrame.Angles(0, math.rad(-75) - dynOppose * 0.2, 0)
        
    local thbCF = cmcOrigin * cmcRot.Rotation
    
    local sLen1 = thumbParts.lengths[1]
    local sW1 = thumbParts.widths[1]
    thumbParts.knuckles[1].CFrame = thbCF
    local rCF1 = thbCF * CFrame.new(0, sLen1 / 2, 0)
    thumbParts.ruas[1].CFrame = rCF1
    thumbParts.gripPads[1].CFrame = rCF1 * CFrame.new(0, 0, -sW1 / 2 - 0.04 * SCALE)
    thumbParts.armors[1].CFrame = rCF1 * CFrame.new(0, 0, sW1 / 2 + 0.06 * SCALE)
    thumbParts.neons[1].CFrame = rCF1 * CFrame.new(0, 0, sW1 / 2 + 0.14 * SCALE)
    
    thbCF = thbCF * CFrame.new(0, sLen1, 0)
    thumbParts.knuckles[2].CFrame = thbCF
    local mcpAngle = math.clamp(current.thumb.mcp_flex * math.rad(55), 0, math.rad(60))
    thbCF = thbCF * CFrame.Angles(-mcpAngle, 0, 0)
    
    local sLen2 = thumbParts.lengths[2]
    local sW2 = thumbParts.widths[2]
    local rCF2 = thbCF * CFrame.new(0, sLen2 / 2, 0)
    thumbParts.ruas[2].CFrame = rCF2
    thumbParts.gripPads[2].CFrame = rCF2 * CFrame.new(0, 0, -sW2 / 2 - 0.04 * SCALE)
    thumbParts.armors[2].CFrame = rCF2 * CFrame.new(0, 0, sW2 / 2 + 0.06 * SCALE)
    thumbParts.neons[2].CFrame = rCF2 * CFrame.new(0, 0, sW2 / 2 + 0.14 * SCALE)
    
    thbCF = thbCF * CFrame.new(0, sLen2, 0)
    thumbParts.knuckles[3].CFrame = thbCF
    local ipAngle = math.clamp(current.thumb.ip_flex * math.rad(85), 0, math.rad(90))
    thbCF = thbCF * CFrame.Angles(-ipAngle, 0, 0)
    
    local sLen3 = thumbParts.lengths[3]
    local sW3 = thumbParts.widths[3]
    local rCF3 = thbCF * CFrame.new(0, sLen3 / 2, 0)
    thumbParts.ruas[3].CFrame = rCF3
    thumbParts.gripPads[3].CFrame = rCF3 * CFrame.new(0, 0, -sW3 / 2 - 0.04 * SCALE)
    thumbParts.armors[3].CFrame = rCF3 * CFrame.new(0, 0, sW3 / 2 + 0.06 * SCALE)
    thumbParts.neons[3].CFrame = rCF3 * CFrame.new(0, 0, sW3 / 2 + 0.14 * SCALE)
    
    local tipCF = thbCF * CFrame.new(0, sLen3 + 0.12 * SCALE, 0)
    thumbParts.sensorTip.CFrame = tipCF
    thumbParts.optic.CFrame = tipCF * CFrame.new(0, 0.08 * SCALE, -sW3 * 0.25)
end)

print("[RoboticHandController] Pristine Anatomical Controller Ready!")
