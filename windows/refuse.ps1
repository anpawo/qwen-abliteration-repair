param([string]$Models)
# Refusal check for each model (comma-separated path=tag pairs), appended to results.txt.
Set-Location D:\qwen-edit
while (Get-Process llama-server -ErrorAction SilentlyContinue) { Start-Sleep 20 }
foreach ($pair in $Models -split ",") {
  $gguf, $tag = $pair -split "="
  Invoke-RestMethod http://127.0.0.1:11434/api/generate -Method Post -Body '{"model":"qwen3.5-9b-abl","keep_alive":0}' | Out-Null
  $srv = Start-Process -PassThru -WindowStyle Hidden .\llama\llama-server.exe -RedirectStandardError "$tag.refuse.server.log" `
    -ArgumentList "-m `"$gguf`" -c 4096 --jinja --port 8080"
  for ($i = 0; $i -lt 150; $i++) { try { if ((Invoke-RestMethod http://127.0.0.1:8080/health).status -eq "ok") { break } } catch {}; Start-Sleep 2 }
  $env:LLAMA_PORT = "8080"
  python refuse.py $tag | Select-Object -Last 1 | Add-Content results.txt
  Stop-Process -Id $srv.Id
  Start-Sleep 3
}
