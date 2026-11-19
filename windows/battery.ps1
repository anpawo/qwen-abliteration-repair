param([string]$Gguf, [string]$Tag, [string]$Tests = "tests.jsonl", [string]$Think = "1", [string]$Gpu = "99")
# -Gpu auto lets llama-server fit the layers to free GPU memory (a Q4 or larger model does not fit at 99).
# 07/11: an empty -Ngl "" was dropped by powershell -File and the script never started, so the value is a word.
$Ngl = if ($Gpu -eq "auto") { "" } else { "-ngl $Gpu" }
# One model on llama-server, the test battery two at a time, TOTAL and capped lines appended to results.txt.
Set-Location D:\qwen-edit
# 07/11: a second queue started its server beside a running one; Windows let both listen on 8080 and their answers mixed.
while (Get-Process llama-server -ErrorAction SilentlyContinue) { Start-Sleep 20 }
if (-not (Test-Path $Gguf)) { "$Tag missing $Gguf, not run" | Add-Content results.txt; exit 1 }
Invoke-RestMethod http://127.0.0.1:11434/api/generate -Method Post -Body '{"model":"qwen3.5-9b-abl","keep_alive":0}' | Out-Null
for ($i = 0; $i -lt 30 -and (Invoke-RestMethod http://127.0.0.1:11434/api/ps).models.Count -gt 0; $i++) { Start-Sleep 2 }
# 08/11: the server keeps up to 8192 MiB of old prompts in RAM by default; on the 8 GB PC a Q4 run swapped to 0.07 tok/s.
$srv = Start-Process -PassThru -WindowStyle Hidden .\llama\llama-server.exe -RedirectStandardError "$Tag.server.log" `
  -ArgumentList "-m `"$Gguf`" $Ngl -c 16384 -np 2 --cache-ram 0 --jinja --port 8080"
for ($i = 0; $i -lt 150; $i++) { try { if ((Invoke-RestMethod http://127.0.0.1:8080/health).status -eq "ok") { break } } catch {}; Start-Sleep 2 }
$env:LLAMA_PORT = "8080"
$env:THINK = $Think
Start-Process -Wait -NoNewWindow python -ArgumentList "-u battery.py $Tests $Tag.jsonl" -RedirectStandardOutput "$Tag.log"
Stop-Process -Id $srv.Id
python battery.py report "$Tag.jsonl" | Select-Object -Last 2 | ForEach-Object { "$Tag $_" } | Add-Content results.txt
