"""
绿美怀集 - 评论同步服务器
用法：双击运行此脚本，或在终端执行 python sync_server.py
保持窗口打开，浏览器中的评论会自动同步到云端。
当db.json更新并被push后，所有用户刷新页面即可看到新评论。
"""
import http.server, json, subprocess, os, sys, time, threading

PORT = 8765
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.json')
LOCK = threading.Lock()
PENDING = False
LAST_PUSH = 0

def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"c": {}, "u": []}

def save_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def push_to_github():
    global LAST_PUSH
    now = time.time()
    if now - LAST_PUSH < 10:
        return "skipped (too soon)"
    LAST_PUSH = now
    try:
        subprocess.run(["git", "add", "db.json"], cwd=os.path.dirname(DB_PATH), capture_output=True, timeout=10)
        r = subprocess.run(["git", "commit", "-m", "sync: 评论/用户数据更新"], cwd=os.path.dirname(DB_PATH), capture_output=True, timeout=10)
        if b"nothing to commit" not in r.stdout and b"nothing to commit" not in r.stderr:
            subprocess.run(["git", "push", "origin", "main"], cwd=os.path.dirname(DB_PATH), capture_output=True, timeout=30)
        return "pushed"
    except Exception as e:
        return f"error: {e}"

class SyncHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/db.json":
            data = load_db()
            self._json_response(data)
        elif self.path == "/ping":
            self._json_response({"status": "ok", "time": time.strftime("%H:%M:%S")})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/sync":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                incoming = json.loads(body)
                with LOCK:
                    db = load_db()
                    if "c" in incoming:
                        for key, arr in incoming["c"].items():
                            if key not in db.setdefault("c", {}):
                                db["c"][key] = []
                            existing_ids = {c.get("id") for c in db["c"][key]}
                            for c in arr:
                                if c.get("id") and c["id"] not in existing_ids:
                                    db["c"][key].append(c)
                    if "u" in incoming:
                        existing_ids = {u.get("id") for u in db.setdefault("u", [])}
                        for u in incoming.get("u", []):
                            if u.get("id") and u["id"] not in existing_ids:
                                db["u"].append(u)
                    save_db(db)
                result = push_to_github()
                self._json_response({"status": "ok", "git": result})
            except Exception as e:
                self._json_response({"status": "error", "message": str(e)}, 500)
        else:
            self.send_response(404)
            self.end_headers()

    def _json_response(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 50)
    print("  绿美怀集 - 评论同步服务器")
    print(f"  监听端口: {PORT}")
    print(f"  数据库: {DB_PATH}")
    print("  保持此窗口打开，评论将自动同步到云端")
    print("=" * 50)
    server = http.server.HTTPServer(("127.0.0.1", PORT), SyncHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
