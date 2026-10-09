# Reproduction status (as packaged)

- Software tests: 7 synthetic pytest tests passed on the build environment.
- Synthetic end-to-end example: ran D06R-like baseline, D08 single/bundled closures, D10 six restoration sequences; frozen-target audit correctly reported `NOT_VERIFIED`.
- Full archived data replay: **NOT RUN** by the newly written code.
- Original D06R/D08/D10 producer script recovery: **NOT CONFIRMED**.
- Actual origin-level numerical parity: **NOT VERIFIED**.
- 27-location sensitivity parity: **NOT VERIFIED** (shifted full edge/interval members needed).
- Code provenance: independent reimplementation drafted with AI assistance from manuscript methods and archived QC; not historical producer source.

Do not replace these statuses without dated, reproducible command logs and verified outputs.
