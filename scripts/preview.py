#!/usr/bin/env python3
"""Open this static site on loopback only; no dependency installation."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
import webbrowser

root = Path(__file__).resolve().parent.parent
handler = partial(SimpleHTTPRequestHandler, directory=str(root))
try:
    server = ThreadingHTTPServer(('127.0.0.1', 4180), handler)
except OSError:
    print('プレビュー用のポートが使用中です。前のプレビューを終了してから、もう一度開いてください。')
    input('Enterで閉じる: ')
    raise SystemExit(1)
print('ひよりのプレビュー: http://127.0.0.1:4180/')
print('終了するときは、この画面で Ctrl+C を押してください。')
Timer(0.5, lambda: webbrowser.open('http://127.0.0.1:4180/')).start()
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
