# Sukkot games – working notes for Claude

Two Hebrew (RTL) Sukkot games for ages 12–18, published with GitHub Pages and embedded in the owner's Google Site.

## Layout
- `src/game.html` – game 1, "צופן הסוכה" escape room (6 stages, based on *Peninei Halakha – Sukkot* ch. 1–5). Its victory screen has a "למשחק השני" button that opens game 2.
- `src/puzzles-v2.html` – game 2, "חידות חשיבה" drag-and-drop puzzles. This is the version players get.
- `src/puzzles.html` – the original version of game 2. Keep it unchanged unless asked.
- `docs/*.html` – the published pages: the same games, **encrypted**, behind a Hebrew password screen.
- `tools/encrypt_game.py` – rebuilds every `docs/` page from `src/` (AES-256-GCM, PBKDF2-SHA256).

## Rules
- **GitHub Pages publishes only `/docs`.** Never switch Pages to the repo root, and never put a readable game into `docs/`. Otherwise the game becomes playable without the password.
- **Never commit or print the password.** It comes from the `GAME_PASSWORD` environment variable, or ask the owner.
- After editing anything in `src/`, rebuild and commit both the source and the encrypted pages:
  ```sh
  GAME_PASSWORD=... python3 tools/encrypt_game.py   # needs: pip install cryptography
  git add -A && git commit -m "..." && git push
  ```
  Pages redeploys in about 1 minute. The Google Site embeds `https://wreuven.github.io/sukkot-escape-room/` by URL, so it needs no change.
- A link ending in `#k=<password>` opens a game without the password screen. Game 1 passes the key to game 2 the same way.

## Owner preferences
- Talk to the owner in English. Describe Hebrew text in English, and quote Hebrew only when it must be typed exactly.
- Each game-1 stage waits 5 seconds after a correct answer before moving on. Game 1's score screen stays until the player presses the next-game button (no pop-up).
- Game 2: the explanation shows with the fireworks, and after 5 seconds a "next" button appears. There is no auto-advance.
- Halachic content follows *Peninei Halakha*, with measures per R' Chaim Naeh (tefach ≈ 8 cm; lavud < 24 cm; 10 tefachim = 80 cm).
