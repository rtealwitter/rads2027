#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for source in topics/*/problems/problem[0-9][0-9].tex project/*.tex; do
  directory="$(dirname "$source")"
  filename="$(basename "$source")"
  (
    cd "$directory"
    for pass in 1 2; do
      if ! pdflatex -interaction=nonstopmode -halt-on-error "$filename" > /dev/null; then
        tail -60 "${filename%.tex}.log"
        exit 1
      fi
    done
  )
  echo "Compiled $source"
done
