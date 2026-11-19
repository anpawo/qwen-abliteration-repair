# Stronger candidates, built then raced on 8 practice problems unseen by the corpora (train 16-23).
Set-Location D:\qwen-edit
$m = "original\qwen3.5-9b-abl.Q3_K_S.gguf"
$cands = [ordered]@{
  "B_26-27_all" = @("26,27", 12288)
  "E_26-27-31_all" = @("26,27,31", 12288)
  "D_3-30_all" = @(((3..30) -join ","), 12288)
}
foreach ($c in $cands.Keys) {
  python edit.py $m recheck.imatrix.gguf solve.imatrix.gguf "$c.gguf" $cands[$c][0] $cands[$c][1] 2>$null
  powershell -NoProfile -File race.ps1 -Gguf "$c.gguf" -Split train -Start 16 -Count 8 -Tag "$($c)_train"
}
