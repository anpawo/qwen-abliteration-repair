# 20/11: two Heretic builds of Qwen3.5-9B at Q4_K_M against H_8-15.Q4_K_M.im on the same tests: dev and held-out
# batteries, the 6 refusal prompts, Heretic's 100-prompt refusal test, then the 150-problem MATH-500 sample through Ollama.
Set-Location D:\qwen-edit
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
[W.P]::SetThreadExecutionState([uint32]2147483649) | Out-Null  # keep the PC awake while this queue runs
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
function Log($m) { "$(Get-Date -Format 'dd/MM HH:mm') bench: $m" | Add-Content results.txt }
function Unload { try { Invoke-RestMethod http://127.0.0.1:11434/api/ps | Select-Object -ExpandProperty models | ForEach-Object {
  Invoke-RestMethod http://127.0.0.1:11434/api/generate -Method Post -Body (@{model = $_.name; keep_alive = 0} | ConvertTo-Json) | Out-Null } } catch {} }
$rivals = @(
  @{Tag = "llmfan46"; Gguf = "rival_llmfan46.Q4_K_M.gguf"; Url = "https://huggingface.co/llmfan46/Qwen3.5-9B-Ultra-Uncensored-Heretic-GGUF/resolve/main/Qwen3.5-9B-Ultra-Uncensored-Heretic-Q4_K_M.gguf"},
  @{Tag = "dsv4"; Gguf = "rival_dsv4.Q4_K_M.gguf"; Url = "https://huggingface.co/mradermacher/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic-GGUF/resolve/main/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic.Q4_K_M.gguf"}
)
foreach ($r in $rivals) {
  if (-not (Test-Path $r.Gguf)) {
    curl.exe -sSL --retry 5 -o "$($r.Gguf).part" $r.Url
    if ($LASTEXITCODE -eq 0 -and (Get-Item "$($r.Gguf).part").Length -gt 5e9) { Move-Item "$($r.Gguf).part" $r.Gguf }
    Log "$($r.Tag) download exit $LASTEXITCODE, $((Get-Item $r.Gguf -ErrorAction SilentlyContinue).Length) bytes"
  }
}
Unload
$refuse100 = @{"H_8-15.Q4_K_M.im.gguf" = "ours"; "original\Qwen3.5-9B.Q3_K_S.gguf" = "original_q3"}
foreach ($r in $rivals) {
  if (-not (Test-Path $r.Gguf)) { continue }
  $refuse100[$r.Gguf] = $r.Tag
  powershell -NoProfile -File battery.ps1 -Gguf $r.Gguf -Tag "bat_$($r.Tag)_nt" -Think 0 -Gpu auto
  powershell -NoProfile -File battery.ps1 -Gguf $r.Gguf -Tests tests_held.jsonl -Tag "held_$($r.Tag)_nt" -Think 0 -Gpu auto
  powershell -NoProfile -File refuse.ps1 -Models "$($r.Gguf)=$($r.Tag)_refuse"
}
Unload
foreach ($g in $refuse100.Keys) {
  $tag = $refuse100[$g]
  $srv = Start-Process -PassThru -WindowStyle Hidden .\llama\llama-server.exe -RedirectStandardError "$tag.refuse100.server.log" `
    -ArgumentList "-m `"$g`" -c 4096 --cache-ram 0 --jinja --port 8080"
  for ($i = 0; $i -lt 150; $i++) { try { if ((Invoke-RestMethod http://127.0.0.1:8080/health).status -eq "ok") { break } } catch {}; Start-Sleep 2 }
  $env:LLAMA_PORT = "8080"
  python -u refuse100.py harmful_test100.jsonl "refuse100_$tag.jsonl" $tag | Select-Object -Last 1 | Add-Content results.txt
  Stop-Process -Id $srv.Id
  while (Get-Process llama-server -ErrorAction SilentlyContinue) { Start-Sleep 2 }
}
Log "batteries and refusal tests done"
$template = (Get-Content qwen3.5-9b-abl.Q4im.Modelfile | Where-Object { $_ -match '^(TEMPLATE|RENDERER|PARSER|PARAMETER) ' }) -join "`n"
foreach ($r in $rivals) {
  if (-not (Test-Path $r.Gguf)) { continue }
  "FROM D:\qwen-edit\$($r.Gguf)`n$template" | Set-Content -Encoding ASCII "rival_$($r.Tag).Modelfile"
  & $ollama create "rival-$($r.Tag)" -f "rival_$($r.Tag).Modelfile" *> "rival_$($r.Tag).create.log"
  Log "$($r.Tag) ollama create exit $LASTEXITCODE"
  Unload
  python -u math500_eval.py math500.jsonl "math500_$($r.Tag).jsonl" --model "rival-$($r.Tag)" --think off --sample 150 *> "math500_$($r.Tag).log"
  python math500_eval.py "math500_$($r.Tag).jsonl" --score | ForEach-Object { "math500 $($r.Tag): $_" } | Add-Content results.txt
}
Unload
Log "done"
