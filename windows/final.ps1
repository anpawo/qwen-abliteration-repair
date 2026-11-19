# Held-out race after practice7: the installed abliterated model against the layers 8-15 restore, 30 GSM8K test problems.
Set-Location D:\qwen-edit
while (Get-CimInstance Win32_Process | Where-Object CommandLine -match "-File practice7\.ps1") { Start-Sleep 20 }
powershell -NoProfile -File race.ps1 -Gguf "H_8-15.gguf" -Split test -Start 0 -Count 30 -Tag "H_8-15_test"
powershell -NoProfile -File race.ps1 -Gguf "original\qwen3.5-9b-abl.Q3_K_S.gguf" -Split test -Start 0 -Count 30 -Tag "base_test"
