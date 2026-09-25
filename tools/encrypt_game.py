#!/usr/bin/env python3
"""Encrypt the games into password-protected pages for GitHub Pages.

Reads each readable game in src/ and writes its page in docs/, which holds only
AES-256-GCM ciphertext (key from PBKDF2-SHA256) plus a small Hebrew password screen that
decrypts in the browser with WebCrypto. A link ending in #k=<password> unlocks directly.

Usage (from the repo root):  GAME_PASSWORD=... python3 tools/encrypt_game.py [input.html output.html]
"""
import base64
import json
import os
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 600_000

LOCK_PAGE = r"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>צופן הסוכה</title>
<style>
  :root { color-scheme: dark; }
  body { margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
         background: #05090e radial-gradient(circle at 50% 0%, rgba(16,185,129,.22), transparent 60%);
         font-family: 'Heebo', Arial, sans-serif; color: #f3f4f6; padding: 16px; box-sizing: border-box; }
  .card { width: 100%; max-width: 380px; background: rgba(12,22,34,.92); border: 1.5px solid rgba(245,158,11,.4);
          border-radius: 24px; padding: 28px 24px; text-align: center; box-shadow: 0 12px 35px -5px rgba(0,0,0,.6); }
  .icon { width: 56px; height: 56px; margin: 0 auto 14px; border-radius: 16px; display: flex; align-items: center;
          justify-content: center; font-size: 28px; background: linear-gradient(135deg,#f59e0b,#b45309); }
  h1 { margin: 0 0 6px; font-size: 26px; color: #fbbf24; }
  p { margin: 0 0 18px; font-size: 15px; color: #d1d5db; }
  input { width: 100%; box-sizing: border-box; padding: 12px 14px; font-size: 17px; border-radius: 12px; text-align: center;
          border: 2px solid #374151; background: #0c1622; color: #fff; outline: none; }
  input:focus { border-color: #f59e0b; }
  button { margin-top: 12px; width: 100%; padding: 12px; font-size: 17px; font-weight: 800; border: 0; border-radius: 12px;
           cursor: pointer; color: #05090e; background: linear-gradient(90deg,#f59e0b,#d97706); }
  button:disabled { opacity: .6; cursor: wait; }
  #err { min-height: 22px; margin-top: 10px; font-size: 14px; color: #fca5a5; font-weight: 700; }
</style>
</head>
<body>
<form class="card" id="lockForm" autocomplete="off">
  <div class="icon">&#x26FA;</div>
  <h1>צופן הסוכה</h1>
  <p>המשחק מוגן בסיסמה. הקלידו את הסיסמה שקיבלתם כדי להיכנס.</p>
  <input id="pw" type="password" placeholder="סיסמה" aria-label="סיסמה" autofocus>
  <button id="go" type="submit">כניסה</button>
  <div id="err" role="alert"></div>
</form>
<script>
(function () {
  const DATA = __DATA__;
  const b64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));

  async function decrypt(password) {
    const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveKey']);
    const key = await crypto.subtle.deriveKey(
      { name: 'PBKDF2', salt: b64(DATA.salt), iterations: DATA.iterations, hash: 'SHA-256' },
      base, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
    const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: b64(DATA.iv) }, key, b64(DATA.data));
    return new TextDecoder().decode(plain);
  }

  async function unlock(password) {
    let html;
    try { html = await decrypt(password); } catch (e) { return false; }
    window.__sukkotKey = password; // lets the game's "open in new tab" button unlock the new tab too
    try { sessionStorage.setItem('sukkotKey', password); } catch (e) {}
    if (location.hash) history.replaceState(null, '', location.pathname + location.search); // hide the key
    document.open(); document.write(html); document.close();
    return true;
  }

  const form = document.getElementById('lockForm');
  const input = document.getElementById('pw');
  const btn = document.getElementById('go');
  const err = document.getElementById('err');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!input.value) return;
    btn.disabled = true; err.textContent = '';
    if (!(await unlock(input.value))) {
      btn.disabled = false; err.textContent = 'סיסמה שגויה, נסו שוב.'; input.select();
    }
  });

  // Key from a shared link (#k=...) or from earlier in this browser tab
  const fromHash = new URLSearchParams(location.hash.slice(1)).get('k');
  let saved = null;
  try { saved = sessionStorage.getItem('sukkotKey'); } catch (e) {}
  const candidate = fromHash || saved;
  if (candidate) {
    btn.disabled = true;
    unlock(candidate).then(ok => {
      if (!ok) { btn.disabled = false; if (fromHash) err.textContent = 'הסיסמה בקישור שגויה.'; }
    });
  }
})();
</script>
</body>
</html>
"""


# Readable source -> published encrypted page. Both games use the same password.
PAGES = [
    ('src/game.html', 'docs/index.html'),      # game 1: escape room
    ('src/puzzles.html', 'docs/puzzles.html'),  # game 2: thinking puzzles (linked from game 1's victory screen)
    ('src/puzzles-v2.html', 'docs/puzzles-v2.html'),  # game 2, improved version for review
]


def encrypt_file(src, out, password):
    plaintext = open(src, 'rb').read()
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS).derive(password.encode())
    ciphertext = AESGCM(key).encrypt(iv, plaintext, None)  # ciphertext || tag, as WebCrypto expects

    data = {
        'salt': base64.b64encode(salt).decode(),
        'iv': base64.b64encode(iv).decode(),
        'iterations': ITERATIONS,
        'data': base64.b64encode(ciphertext).decode(),
    }
    open(out, 'w').write(LOCK_PAGE.replace('__DATA__', json.dumps(data)))
    print(f'wrote {out}: {len(plaintext)} bytes of game -> {os.path.getsize(out)} bytes encrypted page')


def main():
    password = os.environ.get('GAME_PASSWORD')
    if not password:
        sys.exit('Set GAME_PASSWORD in the environment.')
    pages = [(sys.argv[1], sys.argv[2])] if len(sys.argv) > 2 else PAGES
    for src, out in pages:
        encrypt_file(src, out, password)


if __name__ == '__main__':
    main()
