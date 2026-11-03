#!/usr/bin/env bash
# Run a heavy command as a Slurm batch job. Never run compute on the login node.
#
#   tools/run_compute.sh <jobname> <command> [args...]
#
# Example, from inside a topic folder:
#   ../../tools/run_compute.sh demo24 python3 -m nbconvert --to notebook --execute --inplace demo.ipynb
#   ../../tools/run_compute.sh img24  python3 generate_images.py
#
# Blocks until the job finishes, then prints its log, and exits with the job's
# own exit status so a failure is visible to the caller.

set -uo pipefail

if [ $# -lt 2 ]; then
  echo "usage: run_compute.sh <jobname> <command> [args...]" >&2
  exit 2
fi

name="$1"; shift

repo_root="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
logdir="$repo_root/.slurm-logs"
mkdir -p "$logdir"
log="$logdir/${name}.out"
script="$logdir/${name}.sbatch"

# Build the payload script so arbitrary quoting survives (avoids --wrap mangling).
{
  echo '#!/usr/bin/env bash'
  echo 'set -euo pipefail'
  # Pin thread counts: matches --cpus-per-task so BLAS/torch never oversubscribe.
  echo 'export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1'
  printf 'cd %q\n' "$PWD"
  printf 'exec'
  printf ' %q' "$@"
  printf '\n'
} > "$script"
chmod +x "$script"

echo "[run_compute] submitting '$name' -> $log" >&2

sbatch --wait \
  --partition=main \
  --nodelist=himem01 \
  --time=02:00:00 \
  --cpus-per-task=1 \
  --mem=16G \
  --job-name="rads-${name}" \
  --output="$log" \
  "$script"
rc=$?

echo "----- begin job log: $log -----"
cat "$log" 2>/dev/null || echo "(no log produced)"
echo "----- end job log (exit $rc) -----"

exit $rc
