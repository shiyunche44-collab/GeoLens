---
name: new-adr
description: Write an Architecture Decision Record for GeoLens. Use when changing or loosening an architecture rule, adding a module/infrastructure/engine mode, changing metric definitions, or when an evolution trigger in docs/architecture.md fires.
---

# Write an ADR

1. Next number: `ls docs/adr/` → highest `NNNN` + 1. File: `docs/adr/NNNN-kebab-title.md`.
2. Copy `docs/adr/0000-template.md`. Write in Chinese, concise:
   - **背景**: the forces — include numbers (data volume, latency, cost) when a trigger fired.
   - **决策**: what we will do, stated as rules someone can check.
   - **备选方案**: at least one rejected option and why.
   - **后果**: what gets easier/harder, what is now enforced and **how** (which test/contract/CI
     step changes), migration steps.
3. Status starts as `proposed`; the user flips it to `accepted`. If it replaces an older ADR,
   set the old one to `superseded by NNNN` and link both ways.
4. Update the affected docs (`docs/architecture.md`, module READMEs, `CLAUDE.md` rules) and the
   fitness functions (import contracts / architecture tests) in the same PR, so the rule and its
   enforcement never diverge.
