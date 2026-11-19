# Replaces nt5 (07/11): its battery calls passed -Ngl "", which powershell -File drops, so none would have run.
# Each build step is skipped when its output exists; a running llama-quantize (nt5's, left alive) is waited for first.
Set-Location D:\qwen-edit
while (Get-Process llama-quantize, llama-imatrix -ErrorAction SilentlyContinue) { Start-Sleep 30 }
if (-not (Test-Path H_8-15.Q5_K_M.gguf)) { .\llama\llama-quantize.exe f16\H_8-15.f16.gguf H_8-15.Q5_K_M.gguf Q5_K_M 4 *> H_8-15.Q5_K_M.q.log }
if (-not (Test-Path calib.txt)) { python calib.py calib.txt *> calib.log }
if (-not (Test-Path H_8-15.calib.imatrix.gguf)) {
  Invoke-RestMethod http://127.0.0.1:11434/api/generate -Method Post -Body '{"model":"qwen3.5-9b-abl","keep_alive":0}' | Out-Null
  .\llama\llama-imatrix.exe -m H_8-15.Q6_K.gguf -f calib.txt -o H_8-15.calib.imatrix.gguf -c 512 --no-ppl *> H_8-15.imatrix.log
  "nt6 imatrix exit $LASTEXITCODE" | Add-Content results.txt
}
if (-not (Test-Path H_8-15.Q4_K_M.im.gguf)) { .\llama\llama-quantize.exe --imatrix H_8-15.calib.imatrix.gguf f16\H_8-15.f16.gguf H_8-15.Q4_K_M.im.gguf Q4_K_M 4 *> H_8-15.Q4_K_M.im.q.log }
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q6_K.gguf" -Tag bat_H_8-15_Q6_nt -Think 0 -Gpu auto
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q4_K_M.im.gguf" -Tag bat_H_8-15_Q4im_nt -Think 0 -Gpu auto
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q5_K_M.gguf" -Tag bat_H_8-15_Q5_nt -Think 0 -Gpu auto
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q4_K_M.gguf" -Tag bat_H_8-15_Q4_nt -Think 0 -Gpu auto
powershell -NoProfile -File refuse.ps1 -Models "H_8-15.Q6_K.gguf=H_8-15_Q6_refuse,H_8-15.Q5_K_M.gguf=H_8-15_Q5_refuse,H_8-15.Q4_K_M.im.gguf=H_8-15_Q4im_refuse"
"nt6: done" | Add-Content results.txt
