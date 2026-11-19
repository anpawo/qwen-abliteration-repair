param([string]$Old, [string]$New)
# Replace one orchestrator by another without touching the race it started.
Set-Location D:\qwen-edit
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq "powershell.exe" -and $_.CommandLine -match "-File $Old\.ps1" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force; "stopped orchestrator $($_.ProcessId)" }
powershell -NoProfile -File bg.ps1 -Cmd "powershell -NoProfile -File $New.ps1 > $New.log 2>&1" | Select-String ReturnValue
