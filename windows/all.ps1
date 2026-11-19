Set-Location D:\qwen-edit
powershell -NoProfile -File race.ps1 -Gguf edit.gguf -Split test -Start 0 -Count 30 -Tag edit_test
powershell -NoProfile -File race.ps1 -Gguf original\qwen3.5-9b-abl.Q3_K_S.gguf -Split test -Start 0 -Count 30 -Tag base_test
