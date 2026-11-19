# After nt8 (08/11): Q4_K_M.im with every tensor abliteration changed (ffn_down, ssm_out, attn_output) at Q6_K, 5688 MiB.
Set-Location D:\qwen-edit
while (-not (Select-String results.txt -Pattern "nt8: done" -Quiet)) { Start-Sleep 60 }
.\llama\llama-quantize.exe --imatrix H_8-15.calib.imatrix.gguf --tensor-type ffn_down=q6_k --tensor-type ssm_out=q6_k --tensor-type attn_output=q6_k f16\H_8-15.f16.gguf H_8-15.Q4_K_M.im6.gguf Q4_K_M 4 *> H_8-15.Q4_K_M.im6.q.log
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q4_K_M.im6.gguf" -Tag bat_H_8-15_Q4im6_nt -Think 0 -Gpu auto
powershell -NoProfile -File refuse.ps1 -Models "H_8-15.Q4_K_M.im6.gguf=H_8-15_Q4im6_refuse"
"nt9: done" | Add-Content results.txt
