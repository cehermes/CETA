import http.server, os, re, json, webbrowser, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB, OUT = os.path.join(ROOT, "web"), os.path.join(ROOT, "output")
STATE = os.path.join(ROOT, "user", "state.json")  # 上次关闭前的工作流
os.makedirs(OUT, exist_ok=True)


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k):
        super().__init__(*a, directory=WEB, **k)

    def end_headers(s):
        s.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(s):
        if s.path.split("?")[0] == "/api/state":
            data = open(STATE, "rb").read() if os.path.exists(STATE) else b"{}"
            s.send_response(200)
            s.send_header("Content-Type", "application/json")
            s.end_headers()
            s.wfile.write(data)
            return
        super().do_GET()

    def _json(s, obj):
        s.send_response(200)
        s.send_header("Content-Type", "application/json")
        s.end_headers()
        s.wfile.write(json.dumps(obj, ensure_ascii=False).encode())

    def do_POST(s):
        u = urllib.parse.urlparse(s.path)
        if u.path == "/api/open":  # 打开 output 文件夹
            if hasattr(os, "startfile"):
                os.startfile(OUT)
            return s._json({"ok": True})
        if u.path == "/api/state":
            body = s.rfile.read(int(s.headers.get("Content-Length", 0)))
            os.makedirs(os.path.dirname(STATE), exist_ok=True)
            with open(STATE + ".tmp", "wb") as f:
                f.write(body)
            os.replace(STATE + ".tmp", STATE)
            return s._json({"ok": True})
        if u.path != "/api/save":
            return s.send_error(404)
        rel = urllib.parse.parse_qs(u.query).get("path", [""])[0]
        parts = [re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", p).strip(". ") or "_" for p in rel.split("/")[:2]]
        dest = os.path.join(OUT, *parts)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(dest), "归档"), exist_ok=True)  # 每个股票文件夹里放一个归档子文件夹
        with open(dest, "wb") as f:
            f.write(s.rfile.read(int(s.headers.get("Content-Length", 0))))
        s._json({"saved": "output/" + "/".join(parts)})

    def log_message(s, *a):
        pass


for port in range(8199, 8220):
    try:
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), H)
        break
    except OSError:
        continue
url = f"http://127.0.0.1:{port}/"
print("NodeFlow 已启动：", url, "\n保存的图片在：", OUT, "\n关闭此窗口即停止。")
webbrowser.open(url)
srv.serve_forever()
