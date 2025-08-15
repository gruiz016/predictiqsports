Dev Journal — How To
====================

Naming:
  docs/journal/YYYY-MM-DD-<shortsha>-dev-journal.txt

Commit message:
  Include a line:
    Journal: docs/journal/YYYY-MM-DD-<shortsha>-dev-journal.txt

Bypass (rare):
  Add [skip-journal] to your commit message for trivial changes (README, comments).

Workflow:
  1) Copy _template.txt to the date+shortsha filename.
  2) Fill sections succinctly.
  3) Commit with the Journal: line.
  4) Push and open PR. CI enforces presence on main.
