#!/bin/bash
# The README's missing evals at BF16 on one node (4 A100 40 GB): original, abliterated and H_8-15, one vLLM
# server per model, thinking off. Dev and held-out batteries for SEEDS, refuse.py, Heretic's 100-prompt test, full MATH-500.
#SBATCH --nodes=1
#SBATCH --gres=gpu:4
#SBATCH --time=02:00:00
#SBATCH --output=logs/evals-%j.out

W=${QWEN_WORK:?set QWEN_WORK}
R=$W/repo
OUT=$R/results/a100
SEEDS=${SEEDS:-"0 1 2"}
# "<model dir> <name>", one per GPU; a dir named R_<first>-<last> missing from models/ is built by restore.py
MODELS=("Qwen3.5-9B original" "Huihui-Qwen3.5-9B-abliterated abliterated" "H_8-15 H_8-15")
[ -n "${ONLY:-}" ] && IFS=';' read -r -a MODELS <<< "$ONLY"  # ONLY="R_10-15 R_10-15;R_12-15 R_12-15"
MATH_CONC=64
export HF_HOME=$W/hf HF_HUB_OFFLINE=1 VLLM_NO_USAGE_STATS=1 PYTHONUNBUFFERED=1
mkdir -p "$OUT"
cd "$R" || exit 1

serve() {  # gpu model-dir name port
  CUDA_VISIBLE_DEVICES=$1 "$W/.venv/bin/vllm" serve "$W/models/$2" --served-model-name "$3" --port "$4" --seed 0 \
    --max-model-len 16384 --gpu-memory-utilization 0.9 --language-model-only > "$W/logs/vllm-$3-$SLURM_JOB_ID.log" 2>&1 &
}

suite() {  # name port server-pid
  until curl -sf "localhost:$2/health" > /dev/null; do
    kill -0 "$3" 2> /dev/null || { echo "$1: vLLM died, see its log"; return 1; }
    sleep 10
  done
  echo "$1 up at $(date +%T)"
  for s in $SEEDS; do
    THINK=0 SEED=$s LLAMA_PORT=$2 "$W/.venv/bin/python" battery.py tests.jsonl "$OUT/bat_$1_nt_s$s.jsonl" > "$OUT/bat_$1_nt_s$s.log" 2>&1
    THINK=0 SEED=$s LLAMA_PORT=$2 "$W/.venv/bin/python" battery.py tests_held.jsonl "$OUT/held_$1_nt_s$s.jsonl" > "$OUT/held_$1_nt_s$s.log" 2>&1
  done
  LLAMA_PORT=$2 "$W/.venv/bin/python" refuse.py "$1" > "$OUT/refuse6_$1.txt" 2>&1
  LLAMA_PORT=$2 "$W/.venv/bin/python" refuse100.py "$W/data/harmful100.jsonl" "$OUT/refuse100_$1.jsonl" "$1" > "$OUT/refuse100_$1.log" 2>&1
  OPENAI_URL=http://127.0.0.1:$2 CONC=$MATH_CONC "$W/.venv/bin/python" results/math500/eval.py "$W/data/math500/test.jsonl" \
    "$OUT/math500_$1_off.jsonl" --model "$1" --think off > "$OUT/math500_$1_off.log" 2>&1
  echo "$1 done at $(date +%T)"
}

P=()
for i in "${!MODELS[@]}"; do
  read -r dir name <<< "${MODELS[$i]}"
  [ -d "$W/models/$dir" ] || "$W/.venv/bin/python" restore.py "$W/models/Huihui-Qwen3.5-9B-abliterated" \
    "$W/models/Qwen3.5-9B" "$W/models/$dir" "${dir#R_}" > "$OUT/restore_$name.txt" 2>&1
  serve "$i" "$dir" "$name" $((8001 + i))
  suite "$name" $((8001 + i)) $! & P+=($!)
done
wait "${P[@]}"
