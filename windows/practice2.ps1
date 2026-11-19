# Same as practice.ps1 after candidate B, but each edit is brought back to Q3_K_S (only edited tensors change).
Set-Location D:\qwen-edit
while (Get-CimInstance Win32_Process | Where-Object CommandLine -match "race\.ps1") { Start-Sleep 20 }
$m = "original\qwen3.5-9b-abl.Q3_K_S.gguf"
$cands = [ordered]@{
  "E_26-27-31_all" = @("26,27,31", 12288)
  "D_3-30_all" = @(((3..30) -join ","), 12288)
}
foreach ($c in $cands.Keys) {
  python edit.py $m recheck.imatrix.gguf solve.imatrix.gguf tmp.gguf $cands[$c][0] $cands[$c][1] 2>$null
  .\llama\llama-quantize.exe --allow-requantize tmp.gguf "$c.gguf" Q3_K_S 4 > "$c.quantize.log" 2>&1
  Remove-Item tmp.gguf
  powershell -NoProfile -File race.ps1 -Gguf "$c.gguf" -Split train -Start 16 -Count 8 -Tag "$($c)_train"
}
