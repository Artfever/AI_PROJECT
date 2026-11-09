# Shared repository layout

P01-A1 / [issue #32](https://github.com/Artfever/AI_PROJECT/issues/32).

The shared repository is `Artfever/FleetpulseAI` (formerly `Artfever/AI_PROJECT`;
GitHub redirects the historical links). The Python distribution remains
`fleetpulse-ai`, and its import package is `fleetpulse`. The original plan's
`fleetpulse-ai/` root denotes this project; a clone's local directory name need
not match the distribution name.
On 9 November 2026, Abdullah confirmed team agreement on this interpretation,
Python 3.12, the planned folder names, and working access for all three teammates.
GitHub's collaborator API independently showed write access for Abdullah and
Taha and owner/admin access for Shaheer (`Artfever`).

```text
FleetpulseAI/
  pyproject.toml
  app/
    Home.py
    pages/.gitkeep
  src/fleetpulse/
    __init__.py
    data/__init__.py
    features/__init__.py
    models/__init__.py
    evaluation/__init__.py
    optimization/__init__.py
    services/__init__.py
  tests/test_bootstrap.py
  docs/
  data/
    raw/.gitkeep
    demo/.gitkeep
  artifacts/
    development/.gitkeep
    final/.gitkeep
    experiments/.gitkeep
```

At the inspected base `45b8279`, the root package, Home, bootstrap tests and docs
were tracked. The six package subfolders, `app/pages/`, `data/`, and `artifacts/`
were absent. This change adds package markers and empty-directory markers only.
The package docstrings describe pending work; they supply no loader, features,
models, evaluation, scheduling, or service implementation. Taha owns the actual
app pages in P01-T1. The data and artifact directories contain no dataset,
trained bundle, predictions, or metrics.

Git records files, so `.gitkeep` files preserve the empty directories in a
fresh checkout. Ignore exceptions admit only these markers under data and
artifacts; other contents remain ignored pending their own reviewed policies.
`src/fleetpulse/data/` holds Python code; root `data/` holds local data files.

Inspect the committed layout with:

```powershell
git ls-files src/fleetpulse app tests docs data artifacts
git check-ignore data/raw/train_FD001.txt data/demo/example.csv artifacts/development/model.pkl artifacts/final/model.pkl artifacts/experiments/result.json Abdullah.md FleetPulse_Phase_Implementation_Plan.md
git diff --check
```

The ignore command should print every supplied path. An ignored path need not
exist for Git to check its policy. See `handoff_Abdullah.md` for the actual
installation and test results, environment versions, and remaining human checks.
The existing setup instructions remain in README and CONTRIBUTING; portable
imports and configuration are separately accepted under P01-A2, followed by
P01-A3's setup tests and command documentation.
