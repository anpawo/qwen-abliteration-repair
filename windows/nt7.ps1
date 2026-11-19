# After nt6 (07/11): Q6_K (6.9 GB) swapped to 0.05 tok/s on the 8 GB PC, 19/74 done in 80 min, so Q6 and Q5 are left out.
Set-Location D:\qwen-edit
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q4_K_M.im.gguf" -Tag bat_H_8-15_Q4im_nt -Think 0 -Gpu auto
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q4_K_M.gguf" -Tag bat_H_8-15_Q4_nt -Think 0 -Gpu auto
powershell -NoProfile -File refuse.ps1 -Models "H_8-15.Q4_K_M.im.gguf=H_8-15_Q4im_refuse"
"nt7: done" | Add-Content results.txt
