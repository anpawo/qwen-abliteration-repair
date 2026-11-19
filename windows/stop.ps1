# Stop every run of this experiment (orchestrators, evals, llama-server); the ollama baseline is not touched.
Get-CimInstance Win32_Process | Where-Object {
  ($_.Name -eq "powershell.exe" -and $_.CommandLine -match "(all|race|practice)\.ps1") -or
  ($_.Name -eq "python.exe" -and $_.CommandLine -match "eval\.py \S+_(test|train)") -or
  $_.Name -eq "llama-server.exe"
} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; "stopped $($_.Name) $($_.ProcessId)" }
