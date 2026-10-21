-- Scripted console run (any MAME driver; buttons by input field name): MK_PLAN = "t:Button,t:Button,..." (emulated seconds), snapshot every MK_SNAP s, stop at MK_END.
local SNAP, END = tonumber(os.getenv("MK_SNAP") or "2"), tonumber(os.getenv("MK_END") or "120")
local plan = {}
for t, b in string.gmatch(os.getenv("MK_PLAN") or "", "([%d%.]+):([^,]+)") do plan[#plan + 1] = {tonumber(t), b} end
local nextsnap, step, release = SNAP, 1, nil
local function field(n)
  for _, p in pairs(manager.machine.ioport.ports) do if p.fields[n] then return p.fields[n] end end
end
emu.register_periodic(function()
  local t = manager.machine.time:as_double()
  if release and t >= release.t then field(release.n):set_value(0); release = nil end
  if not release and plan[step] and t >= plan[step][1] then
    field(plan[step][2]):set_value(1); release = { n = plan[step][2], t = t + 0.15 }; step = step + 1
  end
  if t >= nextsnap then manager.machine.video:snapshot(); nextsnap = nextsnap + SNAP end
  if t >= END then manager.machine:exit() end
end)
