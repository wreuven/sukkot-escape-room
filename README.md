# צופן הסוכה – Sukkot escape room

An interactive Hebrew escape-room game for Sukkot (ages 12–18), based on *Peninei Halakha – Sukkot*, chapters 1–5.

- `src/game.html` – the game, readable source (a single self-contained HTML file).
- `docs/index.html` – what GitHub Pages publishes: the same game, encrypted, behind a password screen.
- `tools/encrypt_game.py` – rebuilds `docs/index.html` from `src/game.html`.

GitHub Pages publishes only the `docs/` folder, so the game can only be played with the password
(or a link ending in `#k=<password>`).

## Updating the game

```sh
# edit src/game.html, then:
GAME_PASSWORD='...' python3 tools/encrypt_game.py
git add -A && git commit -m "Update game" && git push
```
