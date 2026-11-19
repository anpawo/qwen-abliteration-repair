# Split layers 8-15 the same way.
Set-Location D:\qwen-edit
$abl = "original\qwen3.5-9b-abl.Q3_K_S.gguf"; $orig = "original\Qwen3.5-9B.Q3_K_S.gguf"
foreach ($r in "8-11", "12-15") {
  if (-not (Test-Path "H_$r.gguf")) { python mix.py $abl $orig "H_$r.gguf" $r 2>$null }
  powershell -NoProfile -File race.ps1 -Gguf "H_$r.gguf" -Split train -Start 16 -Count 8 -Tag "H_$($r)_train"
}
powershell -NoProfile -File refuse.ps1 -Models "H_8-11.gguf=H_8-11_refuse,H_12-15.gguf=H_12-15_refuse"
