# After races.ps1: base french-1 with the current prompt, then H_8-15 with thinking off (agreed with Codex).
Set-Location D:\qwen-edit
while (Get-CimInstance Win32_Process | Where-Object CommandLine -match "-File races\.ps1") { Start-Sleep 20 }
python subset.py tests.jsonl tests_fr1.jsonl french-1
powershell -NoProfile -File battery.ps1 -Gguf "original\qwen3.5-9b-abl.Q3_K_S.gguf" -Tag bat_base_fr1 -Tests tests_fr1.jsonl
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.gguf" -Tag bat_H_8-15_nt -Think 0
