# ChatGPT's two first experiments (07/11), thinking off, after nt1.ps1:
# M_8-15 = only ffn_down of layers 8-15 restored; H_8-15_S16-19 = H_8-15 plus attn_output/ssm_out of layers 16-19.
Set-Location D:\qwen-edit
while (Get-CimInstance Win32_Process | Where-Object CommandLine -match "-File nt1\.ps1") { Start-Sleep 20 }
python mix.py original\qwen3.5-9b-abl.Q3_K_S.gguf original\Qwen3.5-9B.Q3_K_S.gguf M_8-15.gguf 8-15 0 ffn_down *> M_8-15.mk.log
python mix.py H_8-15.gguf original\Qwen3.5-9B.Q3_K_S.gguf H_8-15_S16-19.gguf 16-19 0 attn_output,ssm_out *> H_8-15_S16-19.mk.log
powershell -NoProfile -File battery.ps1 -Gguf "M_8-15.gguf" -Tag bat_M_8-15_nt -Think 0
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15_S16-19.gguf" -Tag bat_H_8-15_S16-19_nt -Think 0
