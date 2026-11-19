# After candidate B: is the looping from the weights or from the sampling? Then the strongest edit.
Set-Location D:\qwen-edit
while (Get-CimInstance Win32_Process | Where-Object CommandLine -match "race\.ps1") { Start-Sleep 20 }
$m = "original\qwen3.5-9b-abl.Q3_K_S.gguf"
$env:SAMPLE_TEMP = "0.6"; $env:SAMPLE_PRESENCE = "0"
powershell -NoProfile -File race.ps1 -Gguf $m -Split train -Start 16 -Count 8 -Tag "base_t06_p0_train"
Remove-Item Env:SAMPLE_TEMP, Env:SAMPLE_PRESENCE
$c = "D_3-30_all"
python edit.py $m recheck.imatrix.gguf solve.imatrix.gguf tmp.gguf ((3..30) -join ",") 12288 2>$null
.\llama\llama-quantize.exe --allow-requantize tmp.gguf "$c.gguf" Q3_K_S 4 > "$c.quantize.log" 2>&1
Remove-Item tmp.gguf
powershell -NoProfile -File race.ps1 -Gguf "$c.gguf" -Split train -Start 16 -Count 8 -Tag "$($c)_train"
