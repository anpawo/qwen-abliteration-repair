# After nt7 (08/11): Q4_K_M.im scored 65/74 dev thinking off; the held-out set checks it against H_8-15 Q3 (installed, 59 dev).
Set-Location D:\qwen-edit
while (-not (Select-String results.txt -Pattern "nt7: done" -Quiet)) { Start-Sleep 60 }
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q4_K_M.im.gguf" -Tag held_H_8-15_Q4im_nt -Tests tests_held.jsonl -Think 0 -Gpu auto
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.gguf" -Tag held_H_8-15_nt -Tests tests_held.jsonl -Think 0
"nt8: done" | Add-Content results.txt
