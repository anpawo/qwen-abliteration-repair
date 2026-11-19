# Clean reruns after the 07/11 port clash, one at a time: build M_8-15 with no server running, then four dev runs.
Set-Location D:\qwen-edit
"07/11 19:15 note: bat_M_8-15_nt, bat_H_12-15_nt, bat_H_0-15_nt, bat_H_8-15_S16-19_nt above are invalid (two servers on 8080, M_8-15.gguf missing); reruns end in _nt2" | Add-Content results.txt
python mix.py original\qwen3.5-9b-abl.Q3_K_S.gguf original\Qwen3.5-9B.Q3_K_S.gguf M_8-15.gguf 8-15 0 ffn_down *> M_8-15.mk.log
powershell -NoProfile -File battery.ps1 -Gguf "M_8-15.gguf" -Tag bat_M_8-15_nt2 -Think 0
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15_S16-19.gguf" -Tag bat_H_8-15_S16-19_nt2 -Think 0
powershell -NoProfile -File battery.ps1 -Gguf "H_12-15.gguf" -Tag bat_H_12-15_nt2 -Think 0
powershell -NoProfile -File battery.ps1 -Gguf "H_0-15.gguf" -Tag bat_H_0-15_nt2 -Think 0
