# Thinking-off dev runs: stock (the ceiling of a full restore), then the two restore ranges nearest H_8-15.
Set-Location D:\qwen-edit
powershell -NoProfile -File battery.ps1 -Gguf "original\Qwen3.5-9B.Q3_K_S.gguf" -Tag bat_stock_nt -Think 0
powershell -NoProfile -File battery.ps1 -Gguf "H_12-15.gguf" -Tag bat_H_12-15_nt -Think 0
powershell -NoProfile -File battery.ps1 -Gguf "H_0-15.gguf" -Tag bat_H_0-15_nt -Think 0
