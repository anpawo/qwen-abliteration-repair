Get-CimInstance Win32_Process | Where-Object { $_.Name -in "python.exe", "llama-server.exe", "llama-imatrix.exe" -or
  ($_.Name -eq "powershell.exe" -and $_.CommandLine -match "-File \w+\.ps1") } |
  ForEach-Object { "$($_.ProcessId) $($_.Name) $($_.CommandLine -replace '^.*?(eval\.py|edit\.py|-m )', '$1')" }
