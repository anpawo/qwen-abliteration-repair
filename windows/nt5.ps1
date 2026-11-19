# After nt4 (07/11, ChatGPT's ranking): Q6_K and Q5_K_M of the f16 H_8-15, then Q4_K_M with an imatrix of fresh battery-like prompts.
Set-Location D:\qwen-edit
while (-not (Select-String results.txt -Pattern "H_8-15_S16-19_refuse|nt4:" -Quiet) -or (Get-Process llama-server -ErrorAction SilentlyContinue)) { Start-Sleep 60 }
if (-not (Test-Path f16\H_8-15.f16.gguf)) { "nt5: no f16 H_8-15, stopped" | Add-Content results.txt; exit 1 }
.\llama\llama-quantize.exe f16\H_8-15.f16.gguf H_8-15.Q6_K.gguf Q6_K 4 *> H_8-15.Q6_K.q.log
.\llama\llama-quantize.exe f16\H_8-15.f16.gguf H_8-15.Q5_K_M.gguf Q5_K_M 4 *> H_8-15.Q5_K_M.q.log
python calib.py calib.txt *> calib.log
Invoke-RestMethod http://127.0.0.1:11434/api/generate -Method Post -Body '{"model":"qwen3.5-9b-abl","keep_alive":0}' | Out-Null
.\llama\llama-imatrix.exe -m H_8-15.Q6_K.gguf -f calib.txt -o H_8-15.calib.imatrix.gguf -c 512 --no-ppl *> H_8-15.imatrix.log
"nt5 imatrix exit $LASTEXITCODE" | Add-Content results.txt
.\llama\llama-quantize.exe --imatrix H_8-15.calib.imatrix.gguf f16\H_8-15.f16.gguf H_8-15.Q4_K_M.im.gguf Q4_K_M 4 *> H_8-15.Q4_K_M.im.q.log
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q6_K.gguf" -Tag bat_H_8-15_Q6_nt -Think 0 -Ngl ""
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q5_K_M.gguf" -Tag bat_H_8-15_Q5_nt -Think 0 -Ngl ""
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q4_K_M.im.gguf" -Tag bat_H_8-15_Q4im_nt -Think 0 -Ngl ""
powershell -NoProfile -File refuse.ps1 -Models "H_8-15.Q6_K.gguf=H_8-15_Q6_refuse,H_8-15.Q5_K_M.gguf=H_8-15_Q5_refuse,H_8-15.Q4_K_M.im.gguf=H_8-15_Q4im_refuse"
