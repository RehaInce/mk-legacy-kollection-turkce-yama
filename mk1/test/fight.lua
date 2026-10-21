-- Automated MK1 run driven by emulated time (seconds): coin, start, pick fighter, punch; snapshot every SNAP s.
local SNAP, END = 4, 150
local plan = { {25, "Coin 1"}, {26, "Coin 1"}, {28, "1 Player Start"}, {38, "P1 High Punch"},
               {75, "P1 High Punch"}, {80, "P1 Low Kick"}, {85, "P1 High Punch"}, {90, "P1 Low Punch"} }
local nextsnap, step, release = SNAP, 1, nil
local function field(n)
  local p = manager.machine.ioport.ports
  return p[":IN1"].fields[n] or p[":IN0"].fields[n]
end
emu.register_periodic(function()
  local t = manager.machine.time:as_double()
  if release and t >= release.t then field(release.n):set_value(0); release = nil end
  if plan[step] and t >= plan[step][1] then
    field(plan[step][2]):set_value(1); release = { n = plan[step][2], t = t + 0.15 }; step = step + 1
  end
  if t >= nextsnap then manager.machine.video:snapshot(); nextsnap = nextsnap + SNAP end
  if t >= END then manager.machine:exit() end
end)
