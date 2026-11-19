# After runbat: paired GSM8K test[40:70] races (cap 6144) for the abliterated model, the layers 8-15 restore and stock.
Set-Location D:\qwen-edit
while (Get-CimInstance Win32_Process | Where-Object CommandLine -match "-File runbat\.ps1") { Start-Sleep 20 }
powershell -NoProfile -File race.ps1 -Gguf "original\qwen3.5-9b-abl.Q3_K_S.gguf" -Split test -Start 40 -Count 30 -Tag "gsm40_base"
powershell -NoProfile -File race.ps1 -Gguf "H_8-15.gguf" -Split test -Start 40 -Count 30 -Tag "gsm40_H_8-15"
powershell -NoProfile -File race.ps1 -Gguf "original\Qwen3.5-9B.Q3_K_S.gguf" -Split test -Start 40 -Count 30 -Tag "gsm40_stock"
