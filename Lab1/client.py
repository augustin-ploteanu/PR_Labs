import sys, socket, os

if len(sys.argv) not in (4, 5):
    print("Usage:")
    print("  HTML : python client.py server_host server_port url_path")
    print("  FILE : python client.py server_host server_port url_path directory")
    sys.exit(1)

host, port, path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
save_dir = sys.argv[4] if len(sys.argv) == 5 else None

if save_dir:
    os.makedirs(save_dir, exist_ok=True)

# --- Send HTTP GET request ---
req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
with socket.create_connection((host, port)) as s:
    s.sendall(req.encode())
    data = b""
    while chunk := s.recv(4096):
        data += chunk

# --- Separate headers and body ---
sep = data.find(b"\r\n\r\n")
if sep == -1:
    print("Malformed HTTP response")
    sys.exit(1)
headers, body = data[:sep].decode(errors="ignore"), data[sep + 4:]

# --- Parse headers ---
status_line = headers.split("\r\n", 1)[0]
status_parts = status_line.split()
if len(status_parts) < 2 or not status_parts[1].isdigit():
    print(f"Invalid status line: {status_line}")
    sys.exit(1)
status_code = int(status_parts[1])

ctype = ""
for line in headers.split("\r\n"):
    if line.lower().startswith("content-type:"):
        ctype = line.split(":", 1)[1].strip().lower()
        break

# --- Handle response ---
if status_code != 200:
    print(f"Error {status_code}: {status_line}")
    sys.exit(1)

if ctype.startswith("text/html"):
    print(body.decode(errors="ignore"))
elif ctype in ("image/png", "application/pdf"):
    if not save_dir:
        print("Error: must specify a directory to save binary files (PNG/PDF)")
        sys.exit(1)
    fname = os.path.basename(path.rstrip("/")) or "index"
    ext = ".png" if "png" in ctype else ".pdf"
    if not fname.endswith(ext):
        fname += ext
    file_path = os.path.join(save_dir, fname)
    with open(file_path, "wb") as f:
        f.write(body)
    print(f"Saved {file_path}")
else:
    print(f"Unsupported content type: {ctype}")
