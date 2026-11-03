# Homework problems

All 22 homework Colabs linked by the 2026 course have been downloaded and
converted to LaTeX. The handouts live beside their related readings in
`topics/NN_name/problems/problemNN.tex` and `problemNN.pdf`.

The conversion preserves the problem statements, mathematics, hints,
computational tasks, three embedded figures, and the two starter-code cells.
Each handout links back to its original Colab. Original notebook snapshots
are in `archive/colab2026/`; they retain their historical 2026 dates.
The live handouts use the 2027 deadlines in `manifest.json`.

Compile from the repository, so each handout can find its shared preamble,
images, and starter code:

```bash
bash tools/compile_problem_pdfs.sh
```

On Hopper, prefix this with `tools/run_compute.sh handouts`.
To edit a handout, edit its TeX source and recompile. To regenerate every
handout from the archived notebooks and manifest, run
`python3 tools/import_colab_problems.py` first. Reimporting overwrites manual
TeX edits. It never executes a notebook or modifies the online Colabs.

The import normalizes display-math delimiters, updates submission dates,
repairs the original notebook typo “solutions python notebook,” removes a
stray closing brace in Problem 16, and repairs a spaced math delimiter in
Problem 12. It does not rewrite or solve the mathematical questions.

The manifest records the source URL, snapshot SHA-256, cell counts,
extracted figure count, deadline, and output paths for every problem.
