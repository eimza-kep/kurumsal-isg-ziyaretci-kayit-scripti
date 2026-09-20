import http.server
import socketserver
import json
import sqlite3
import os
import sys
import random
from urllib.parse import urlparse

PORT = 8089
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isg_ziyaretciler.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_code TEXT UNIQUE,
            visitor_name TEXT,
            visitor_id TEXT,
            visitor_phone TEXT,
            visitor_company TEXT,
            visitor_email TEXT,
            host_employee TEXT,
            host_department TEXT,
            visit_reason TEXT,
            equipment_brought TEXT,
            vehicle_plate TEXT,
            check_in_time TEXT,
            check_out_time TEXT,
            status TEXT DEFAULT 'Tesis İçinde (Aktif)',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

class VisitorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.send_file("index.html", "text/html; charset=utf-8")
        elif path in ("/admin", "/admin.html"):
            self.send_file("admin.html", "text/html; charset=utf-8")
        elif path == "/health":
            self.send_json({"status": "ok", "app": "kurumsal-isg-ziyaretci-kayit-scripti", "port": PORT})
        elif path == "/api/ziyaretciler":
            self.handle_get_visitors()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/ziyaretci-giris":
            self.handle_check_in()
        elif path == "/api/ziyaretci-cikis":
            self.handle_check_out()
        else:
            self.send_error(404, "Endpoint not found")

    def send_file(self, filename, content_type):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if not os.path.exists(filepath):
            self.send_error(404, f"File {filename} not found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def handle_check_in(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            tracking_code = data.get("tracking_code") or f"ISG-2026-{random.randint(1000, 9999)}"

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO visitors (
                    tracking_code, visitor_name, visitor_id, visitor_phone,
                    visitor_company, visitor_email, host_employee, host_department,
                    visit_reason, equipment_brought, vehicle_plate,
                    check_in_time, check_out_time, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tracking_code,
                data.get("visitor_name", ""),
                data.get("visitor_id", ""),
                data.get("visitor_phone", ""),
                data.get("visitor_company", ""),
                data.get("visitor_email", ""),
                data.get("host_employee", ""),
                data.get("host_department", ""),
                data.get("visit_reason", ""),
                data.get("equipment_brought", ""),
                data.get("vehicle_plate", ""),
                data.get("check_in_time", ""),
                "",
                data.get("status", "Tesis İçinde (Aktif)"),
                data.get("created_at", "")
            ))
            conn.commit()
            conn.close()

            self.send_json({"status": "success", "tracking_code": tracking_code})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_get_visitors(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM visitors ORDER BY id DESC")
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            self.send_json(rows)
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_check_out(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            tracking_code = data.get("tracking_code")
            check_out_time = data.get("check_out_time")

            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("""
                UPDATE visitors
                SET status = 'Çıkış Yapıldı', check_out_time = ?
                WHERE tracking_code = ?
            """, (check_out_time, tracking_code))
            conn.commit()
            conn.close()

            self.send_json({"status": "success", "updated": tracking_code})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", PORT))
    print(f"🚀 ISG Ziyaretci Portali Baslatildi: http://localhost:{port}")
    print(f"🦺 Guvenlik Yonetim Paneli: http://localhost:{port}/admin")
    with socketserver.TCPServer(("", port), VisitorHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSunucu kapatildi.")
