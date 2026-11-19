# 08/11: installs H_8-15.Q4_K_M.im (65/74 dev, 68/74 held-out) as qwen3.5-9b-abl; the Q3 build it replaces stays as qwen3.5-9b-abl-q3.
Set-Location D:\qwen-edit
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$log = "D:\qwen-edit\install.log"
function Log($m) { "$(Get-Date -Format HH:mm:ss) $m" | Add-Content $log }
if (-not (& $ollama list | Select-String "^qwen3.5-9b-abl-q3")) { & $ollama cp qwen3.5-9b-abl qwen3.5-9b-abl-q3 | Out-Null; Log "old build kept as qwen3.5-9b-abl-q3" }
$mf = & $ollama show qwen3.5-9b-abl-q3 --modelfile | ForEach-Object { if ($_ -match "^FROM ") { "FROM D:\qwen-edit\H_8-15.Q4_K_M.im.gguf" } else { $_ } }
$mf | Set-Content -Encoding UTF8 qwen3.5-9b-abl.Q4im.Modelfile
& $ollama create qwen3.5-9b-abl -f qwen3.5-9b-abl.Q4im.Modelfile *> install.create.log
Log "create exit $LASTEXITCODE"
if ($LASTEXITCODE -ne 0) { Log "stopped"; exit 1 }
$body = '{"model":"qwen3.5-9b-abl","messages":[{"role":"user","content":"What is 47 * 83? Answer with the number only."}],"stream":false,"think":false,"options":{"num_ctx":65536}}'
$t = Get-Date; $r = Invoke-RestMethod http://127.0.0.1:11434/api/chat -Method Post -Body $body -TimeoutSec 900
Log "64k answer: $($r.message.content.Trim()) in $([int]((Get-Date) - $t).TotalSeconds) s, eval $([math]::Round($r.eval_count / ($r.eval_duration / 1e9), 1)) tok/s"
$p = (Invoke-RestMethod http://127.0.0.1:11434/api/ps).models | Where-Object name -like "qwen3.5-9b-abl*"
Log "loaded: size $([int]($p.size/1MB)) MB, in VRAM $([int]($p.size_vram/1MB)) MB, ctx $($p.context_length)"
Log "free C: $([int]((Get-PSDrive C).Free/1GB)) GB, free RAM $([int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)) MB"
Log "done"
