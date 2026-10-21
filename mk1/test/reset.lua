-- MAME reloads this script on every boot, so each START line in MK_LOG is one boot:
-- a crash triggers the watchdog reset and shows up as an extra START. Exits after MK_END emulated seconds.
local END = tonumber(os.getenv("MK_END") or "90")
local f = io.open(os.getenv("MK_LOG"), "a")
f:write("START\n"); f:flush()
emu.register_periodic(function()
  if manager.machine.time:as_double() >= END then f:write("END\n"); f:close(); manager.machine:exit() end
end)
