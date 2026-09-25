# צופן הסוכה – Sukkot escape room

An interactive Hebrew escape-room game for Sukkot (ages 12–18), based on *Peninei Halakha – Sukkot*, chapters 1–5.

- `src/game.html` – game 1, the escape room (readable source, one self-contained HTML file).
- `src/puzzles.html` – game 2, "חידות חשיבה" thinking puzzles; offered from game 1's victory screen.
- `src/puzzles-v2.html` – game 2 with review improvements (published as `puzzles-v2.html`), for comparison.
- `docs/*.html` – what GitHub Pages publishes: the same games, encrypted, behind a password screen.
- `tools/encrypt_game.py` – rebuilds the `docs/` pages from `src/`.

GitHub Pages publishes only the `docs/` folder, so the games can only be played with the password
(or a link ending in `#k=<password>`, e.g. `…/sukkot-escape-room/#k=…` or `…/puzzles.html#k=…`).

## Updating the game

```sh
# edit src/game.html or src/puzzles.html, then:
GAME_PASSWORD='...' python3 tools/encrypt_game.py
git add -A && git commit -m "Update game" && git push
```
