#!/usr/bin/env python3
"""絵日記の HTML を、ヘッドレス Chrome で描いて PNG に書き出す。

使い方: render_png.py 日記.html 出力.png [横の画素数 (既定 1500、上限 2080)]
クレヨンのざらつきで PNG は重くなり、1500 で 4MB 台、2000 で 7MB 台になる。
Chrome は環境変数 CHROME、なければよくある置き場所から探す。
"""
import base64
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

CANDIDATES = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
]
NAMES = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'chrome']

# ページの描画が終わってから、canvas の画素を data URL で DOM に書き出す。
# preserveDrawingBuffer: true なので WebGL の canvas もそのまま読める。2D で代わりに描いたときは印を付ける
GRAB = """
<script>
(async () => {
  if (document.fonts) await document.fonts.ready;
  await new Promise((r) => setTimeout(r, 4000));
  const c = document.getElementById('page');
  const out = document.createElement('pre');
  out.id = '__png';
  out.dataset.webgl = c.getContext('webgl') ? '1' : '0';
  out.textContent = c.toDataURL('image/png');
  document.body.appendChild(out);
})();
</script>
"""


# AI の sandbox の中では Chrome 本体が起動できないことがある。そのときは、Playwright などが入れる
# chrome-headless-shell を、1プロセスで動かすオプションで使う
SHELLS = ['~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell',
          '~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell',
          '~/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-*/chrome-headless-shell']
IN_SANDBOX = ['--no-sandbox', '--single-process', '--no-zygote', '--in-process-gpu']


def browsers():
    """試す順に (実行ファイル, 追加オプション) を返す。"""
    found = [os.environ['CHROME']] if os.environ.get('CHROME') else []
    found += [p for p in CANDIDATES if os.path.exists(p)][:1] or [p for p in map(shutil.which, NAMES) if p][:1]
    shells = sorted({p for g in SHELLS for p in glob.glob(os.path.expanduser(g))}, reverse=True)
    return [(p, []) for p in found] + [(p, IN_SANDBOX) for p in shells[:1]]


def grab(chrome, extra, doc, width):
    with tempfile.TemporaryDirectory() as tmp:
        html = os.path.join(tmp, 'page.html')
        with open(html, 'w', encoding='utf-8') as f:
            f.write(doc)
        cmd = [chrome, '--headless', '--disable-gpu', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', *extra,
               '--hide-scrollbars', '--force-device-scale-factor=1', f'--window-size={width + 100},{int(width * 1.38) + 100}',
               '--virtual-time-budget=30000', f'--user-data-dir={os.path.join(tmp, "profile")}', '--dump-dom', 'file://' + html]
        try:
            dom = subprocess.run(cmd, capture_output=True, text=True, timeout=180).stdout
        except (OSError, subprocess.TimeoutExpired):
            return None
    return re.search(r'<pre id="__png" data-webgl="(\d)">data:image/png;base64,([A-Za-z0-9+/=]+)</pre>', dom)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    width = min(int(sys.argv[3]) if len(sys.argv) > 3 else 1500, 2080)
    with open(src, encoding='utf-8') as f:
        page = f.read()
    css = f'<style>body{{padding:0!important}}#page{{width:{width}px!important;max-width:none!important;box-shadow:none!important;border-radius:0!important}}</style>'
    doc = page if page.lstrip().lower().startswith('<!doctype') else f'<!doctype html>\n<html lang="ja"><head>\n{page}'
    doc = doc.replace('</style>', '</style>\n' + css, 1) + GRAB
    tries = browsers()
    if not tries:
        sys.exit('Chrome が見つからない。環境変数 CHROME に実行ファイルのパスを入れて、もう一度実行する')
    m = next((m for chrome, extra in tries if (m := grab(chrome, extra, doc, width))), None)
    if not m:
        sys.exit('PNG を取り出せなかった。AI の sandbox の中で動かしているなら、sandbox の外で実行する。'
                 'それでもだめなら、ページのスクリプトが止まっていないか、ブラウザで開いて確かめる')
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    with open(dst, 'wb') as f:
        f.write(base64.b64decode(m.group(2)))
    print(f'{dst}  ({os.path.getsize(dst) // 1024} KB)')
    if m.group(1) != '1':
        print('注意: WebGL が使えず、かすれを簡易表示で描いた')


if __name__ == '__main__':
    main()
