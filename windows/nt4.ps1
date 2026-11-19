# Full-precision restore (07/11): layers 8-15 taken back from stock in f16, compressed once to Q4_K_M, then tested.
Set-Location D:\qwen-edit
while (Get-Process curl -ErrorAction SilentlyContinue) { Start-Sleep 60 }
# The f16 build needs the RAM: wait for nt3's last run and its server to end.
while (-not (Select-String results.txt -Pattern "bat_H_0-15_nt2 TOTAL|nt2 missing" -Quiet) -or (Get-Process llama-server -ErrorAction SilentlyContinue)) { Start-Sleep 60 }
foreach ($f in "f16\abl.f16.gguf","f16\stock.f16.gguf") { if ((Get-Item $f).Length -lt 17900000000) { "nt4: $f incomplete, stopped" | Add-Content results.txt; exit 1 } }
python mix.py f16\abl.f16.gguf f16\stock.f16.gguf f16\H_8-15.f16.gguf 8-15 *> f16\H_8-15.mk.log
.\llama\llama-quantize.exe f16\H_8-15.f16.gguf H_8-15.Q4_K_M.gguf Q4_K_M 4 *> H_8-15.Q4_K_M.q.log
powershell -NoProfile -File battery.ps1 -Gguf "H_8-15.Q4_K_M.gguf" -Tag bat_H_8-15_Q4_nt -Think 0 -Ngl ""
powershell -NoProfile -File refuse.ps1 -Models "H_8-15.Q4_K_M.gguf=H_8-15_Q4_refuse,M_8-15.gguf=M_8-15_refuse,H_8-15_S16-19.gguf=H_8-15_S16-19_refuse"
