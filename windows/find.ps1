# Stop the ollama baseline, build the two corpora, record MLP activations on each, scan the layers.
Set-Location D:\qwen-edit
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object CommandLine -like "*eval.py*base_train*" |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force; "stopped baseline pid $($_.ProcessId)" }
Invoke-RestMethod http://127.0.0.1:11434/api/generate -Method Post -Body '{"model":"qwen3.5-9b-abl","keep_alive":0}' | Out-Null
for ($i = 0; $i -lt 30 -and (Invoke-RestMethod http://127.0.0.1:11434/api/ps).models.Count -gt 0; $i++) { Start-Sleep 2 }
$m = "original\qwen3.5-9b-abl.Q3_K_S.gguf"
python split.py base_train.jsonl solve.txt recheck.txt
foreach ($c in "solve", "recheck") {
  .\llama\llama-imatrix.exe -m $m -f "$c.txt" -o "$c.imatrix.gguf" -c 512 -ngl 99 --no-ppl > "$c.imatrix.log" 2>&1
  "$c imatrix exit $LASTEXITCODE"
}
python -c "import gguf; r=gguf.GGUFReader('recheck.imatrix.gguf'); print([t.name for t in r.tensors if 'blk.20.ffn_down' in t.name])"
python edit.py $m recheck.imatrix.gguf solve.imatrix.gguf scan
