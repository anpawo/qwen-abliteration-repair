param([string]$Range, [double]$Alpha = 0, [string]$Kinds = "", [string]$Out)
# Builds a restore candidate: layers $Range (a-b) of the abliterated model pulled toward stock, keeping $Alpha of the abliteration delta.
Set-Location D:\qwen-edit
$abl, $stock = "original\qwen3.5-9b-abl.Q3_K_S.gguf", "original\Qwen3.5-9B.Q3_K_S.gguf"
if ($Alpha -eq 0) { python mix.py $abl $stock $Out $Range 0 $Kinds *> "$Out.mk.log"; exit }
python mix.py $abl $stock "tmp_$Out" $Range $Alpha $Kinds *> "$Out.mk.log"
.\llama\llama-quantize.exe --allow-requantize "tmp_$Out" $Out Q3_K_S 4 *>> "$Out.mk.log"
Remove-Item "tmp_$Out"
