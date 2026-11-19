param([string]$Gguf, [string]$Split, [int]$Start, [int]$Count, [string]$Tag)
# One model on llama-server, two eval processes in parallel over [Start, Start+Count), summary appended to results.txt.
Set-Location D:\qwen-edit
Invoke-RestMethod http://127.0.0.1:11434/api/generate -Method Post -Body '{"model":"qwen3.5-9b-abl","keep_alive":0}' | Out-Null
for ($i = 0; $i -lt 30 -and (Invoke-RestMethod http://127.0.0.1:11434/api/ps).models.Count -gt 0; $i++) { Start-Sleep 2 }
$srv = Start-Process -PassThru -WindowStyle Hidden .\llama\llama-server.exe -RedirectStandardError "$Tag.server.log" `
  -ArgumentList "-m `"$Gguf`" -ngl 99 -c 16384 -np 2 --jinja --port 8080"
for ($i = 0; $i -lt 150; $i++) { try { if ((Invoke-RestMethod http://127.0.0.1:8080/health).status -eq "ok") { break } } catch {}; Start-Sleep 2 }
$env:LLAMA_PORT = "8080"
$h = [math]::Ceiling($Count / 2)
$a = Start-Process -PassThru -NoNewWindow python -ArgumentList "-u eval.py $Tag $Split $Start $h $Tag.a.jsonl" -RedirectStandardOutput "$Tag.a.log"
$b = Start-Process -PassThru -NoNewWindow python -ArgumentList "-u eval.py $Tag $Split $($Start + $h) $($Count - $h) $Tag.b.jsonl" -RedirectStandardOutput "$Tag.b.log"
$a, $b | Wait-Process
Stop-Process -Id $srv.Id
python score.py $Tag "$Tag.a.jsonl" "$Tag.b.jsonl" | Add-Content results.txt
