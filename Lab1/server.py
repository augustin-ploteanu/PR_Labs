import os, sys, socket, urllib.parse, mimetypes
from datetime import datetime
from pathlib import Path

# --- Settings from command line ---
if len(sys.argv) < 2:
    print("Usage: python server.py <directory> [--port PORT]")
    sys.exit(1)

root = Path(sys.argv[1]).resolve()
port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8080
mime_whitelist = {"text/html", "image/png", "application/pdf"}

# --- Helpers ---
def response(status, body="", ctype="text/html"):
    body_bytes = body.encode() if isinstance(body, str) else body
    headers = [
        f"HTTP/1.1 {status}",
        f"Date: {datetime.utcnow():%a, %d %b %Y %H:%M:%S GMT}",
        f"Content-Type: {ctype}",
        f"Content-Length: {len(body_bytes)}",
        "Connection: close",
        "", "",
    ]
    return "\r\n".join(headers).encode() + body_bytes

def not_found():
    return response("404 Not Found", "<h1>404 Not Found</h1>")

def listing(path):
    rel = str(path.relative_to(root)) if path != root else ""
    items = []
    for entry in sorted(path.iterdir()):
        name = entry.name + ("/" if entry.is_dir() else "")
        href = urllib.parse.quote(name)
        items.append(f'  <li><a href="{href}">{name}</a></li>')

    html = (
        f"<html>\n"
        f"<head><title>Index of /{rel}</title></head>\n"
        f"<body>\n"
        f"<h1>Index of /{rel}</h1>\n"
        f"<ul>\n" + "\n".join(items) + "\n</ul>\n"
        f"</body>\n"
        f"</html>"
    )
    return response("200 OK", html)

# --- Logging helper ---
def log(addr, method, path, status):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {addr[0]} {method} {path} {status}", flush=True)

# --- Server loop ---
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("0.0.0.0", port))
    s.listen(1)
    print(f"Serving {root} on port {port}", flush=True)
    while True:
        conn, addr = s.accept()
        with conn:
            req = conn.recv(1024).decode(errors="ignore")
            if not req:
                continue
            line = req.split("\r\n")[0]
            parts = line.split()
            if len(parts) < 2:
                conn.sendall(response("400 Bad Request", "<h1>400 Bad Request</h1>"))
                log(addr, "?", "?", "400 Bad Request")
                continue

            method, raw_path = parts[0], parts[1]
            path = urllib.parse.unquote(raw_path)
            if method not in ("GET", "HEAD"):
                conn.sendall(response("405 Method Not Allowed", "<h1>405</h1>"))
                log(addr, method, path, "405 Method Not Allowed")
                continue

            fs_path = (root / path.lstrip("/")).resolve()
            if not str(fs_path).startswith(str(root)):
                conn.sendall(not_found())
                log(addr, method, path, "404 Not Found")
                continue

            if fs_path.is_dir():
                conn.sendall(listing(fs_path))
                log(addr, method, path, "200 OK (directory)")
            elif fs_path.is_file():
                ctype = mimetypes.guess_type(fs_path.name)[0] or "application/octet-stream"
                if ctype not in mime_whitelist:
                    conn.sendall(not_found())
                    log(addr, method, path, "404 Not Found (unsupported type)")
                    continue
                with open(fs_path, "rb") as f:
                    data = f.read()
                conn.sendall(response("200 OK", b"" if method == "HEAD" else data, ctype))
                log(addr, method, path, "200 OK")
            else:
                conn.sendall(not_found())
                log(addr, method, path, "404 Not Found")
