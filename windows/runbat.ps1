# After practice7: the dev battery on the abliterated model, the layers 8-15 restore, and stock (the ceiling of a full restore).
Set-Location D:\qwen-edit
while (Get-CimInstance Win32_Process | Where-Object CommandLine -match "-File practice7\.ps1") { Start-Sleep 20 }
powershell -NoProfile -File battery.ps1 -Gguf "original\qwen3.5-9b-abl.Q3_K_S.gguf" -Tag bat_base
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.gguf" -Tag bat_H_8-15
powershell -NoProfile -File battery.ps1 -Gguf "original\Qwen3.5-9B.Q3_K_S.gguf" -Tag bat_stock
