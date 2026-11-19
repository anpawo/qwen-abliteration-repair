# After practice3: the unedited abliterated model and the non-abliterated one, both with the Modelfile sampling, same 8 problems.
Set-Location D:\qwen-edit
while (Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "-File practice3\.ps1|curl\.exe" }) { Start-Sleep 20 }
powershell -NoProfile -File race.ps1 -Gguf original\qwen3.5-9b-abl.Q3_K_S.gguf -Split train -Start 16 -Count 8 -Tag "base_train"
powershell -NoProfile -File race.ps1 -Gguf original\Qwen3.5-9B.Q3_K_S.gguf -Split train -Start 16 -Count 8 -Tag "notabl_train"
