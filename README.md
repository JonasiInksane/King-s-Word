# Story workspace

Multi-book workspace. Each novel lives under `books/<slug>/` with its own chapters, lore, progress, style, and Cursor rules. Style and POV are **not** shared at the root.

## Books

| Book | Path | Logline |
|---|---|---|
| **王の言霊 / The King's Word** | [`books/kings-word/`](books/kings-word/) | Three friends in Kōgetsu City — until two of them discover they carry the King's Word, a power that forces anyone who hears a command to obey it. |
| **The Fool's Balance** *(active)* | [`books/the-fools-balance/`](books/the-fools-balance/) | *(logline TBD)* |
| **Where Maps End** | [`books/where-maps-end/`](books/where-maps-end/) | Vol 1 *Where the Maps Disagree*: dated maps that were all correct, a basin that used to move, and a ridiculous jester delighted the dungeon lived — every answer opens two new questions. |

## Add a book

1. Copy the template:
   ```bash
   cp -r templates/book books/your-slug
   ```
   On PowerShell:
   ```powershell
   Copy-Item -Recurse templates\book books\your-slug
   ```
2. In `books/your-slug/.cursor/rules/story-writing.mdc`, replace `BOOK-SLUG` in the globs with `your-slug`.
3. Fill `README.md` (logline, POV, style), `PROGRESS.md`, and `lore/`.
4. Add the book to the catalog table above.

## Working here

- Open this folder (`Story/`) as the workspace so every book is visible.
- Edit under `books/<slug>/` — that book's `.cursor/rules` apply via path globs.
- Resume a book from its own `PROGRESS.md` and `lore/plot-outline.md`.

If an empty leftover `Story/` directory still appears at the root, delete it manually (Windows may keep it locked while Cursor had the old nested path open). All King's Word files live under `books/kings-word/` now.
