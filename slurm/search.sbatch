#!/bin/bash
# Wider weight-restoration search at BF16: each candidate is restore.py on the abliterated model, served by vLLM on one
# A100, scored on the dev battery (SEEDS, thinking off) and both refusal tests. Four GPUs, four workers. The held-out
# set is not run here: it stays for the build this search picks.
#SBATCH --nodes=1
#SBATCH --gres=gpu:4
#SBATCH --time=02:00:00
#SBATCH --output=logs/search-%j.out

W=${QWEN_WORK:?set QWEN_WORK}
R=$W/repo
OUT=$R/results/a100/search
SEEDS=${SEEDS:-"0 1 2"}
GPUS=4
# name layers [name parts]
CANDIDATES=(
  "R_0-7 0-7" "R_4-11 4-11" "R_12-19 12-19" "R_16-23 16-23" "R_20-27 20-27" "R_24-31 24-31"
  "R_4-15 4-15" "R_6-17 6-17" "R_8-19 8-19" "R_8-23 8-23" "R_8-11 8-11" "R_10-15 10-15" "R_12-15 12-15"
  "R_8-15_down 8-15 mlp.down_proj" "R_8-15_out 8-15 linear_attn.out_proj,self_attn.o_proj" "R_0-15 0-15"
)
export HF_HOME=$W/hf HF_HUB_OFFLINE=1 VLLM_NO_USAGE_STATS=1 PYTHONUNBUFFERED=1 CONC=8 THINK=0
mkdir -p "$OUT" "$W/models/search"
cd "$R" || exit 1

candidate() {  # gpu name layers [parts]
  local gpu=$1 name=$2 port=$((8100 + $1)) dir=$W/models/search/$2
  [ -s "$OUT/refuse100_$name.jsonl" ] && return 0
  "$W/.venv/bin/python" restore.py "$W/models/Huihui-Qwen3.5-9B-abliterated" "$W/models/Qwen3.5-9B" "$dir" "$3" $4 \
    > "$OUT/restore_$name.txt" 2>&1 || return 1
  CUDA_VISIBLE_DEVICES=$gpu "$W/.venv/bin/vllm" serve "$dir" --served-model-name "$name" --port $port --seed 0 \
    --max-model-len 8192 --gpu-memory-utilization 0.9 --language-model-only > "$W/logs/vllm-$name-$SLURM_JOB_ID.log" 2>&1 &
  local pid=$!
  until curl -sf "localhost:$port/health" > /dev/null; do
    kill -0 $pid 2> /dev/null || { echo "$name: vLLM died"; return 1; }
    sleep 10
  done
  for s in $SEEDS; do
    SEED=$s LLAMA_PORT=$port "$W/.venv/bin/python" battery.py tests.jsonl "$OUT/bat_${name}_nt_s$s.jsonl" > /dev/null 2>&1
  done
  LLAMA_PORT=$port "$W/.venv/bin/python" refuse.py "$name" > "$OUT/refuse6_$name.txt" 2>&1
  LLAMA_PORT=$port "$W/.venv/bin/python" refuse100.py "$W/data/harmful100.jsonl" "$OUT/refuse100_$name.jsonl" "$name" \
    > "$OUT/refuse100_$name.log" 2>&1
  kill $pid; wait $pid
  rm -rf "$dir"
  echo "$name done at $(date +%T)"
}

worker() {  # gpu: takes every GPUS-th candidate
  for ((i = $1; i < ${#CANDIDATES[@]}; i += GPUS)); do candidate "$1" ${CANDIDATES[$i]}; done
}

for g in $(seq 0 $((GPUS - 1))); do worker $g & done
wait
