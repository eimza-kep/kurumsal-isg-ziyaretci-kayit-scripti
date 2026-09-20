import unittest
import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server

class TestVisitorSystem(unittest.TestCase):
    def setUp(self):
        server.init_db()
        self.conn = sqlite3.connect(server.DB_FILE)
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("DELETE FROM visitors WHERE tracking_code LIKE 'ISG-TEST%'")
        self.conn.commit()

    def tearDown(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM visitors WHERE tracking_code LIKE 'ISG-TEST%'")
        self.conn.commit()
        self.conn.close()

    def test_database_table_exists(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='visitors'")
        row = cur.fetchone()
        self.assertIsNotNone(row, "visitors tablosu oluşturulmuş olmalıdır.")

    def test_visitor_insert_and_retrieve(self):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO visitors (
                tracking_code, visitor_name, visitor_id, visitor_phone,
                visitor_company, visitor_email, host_employee, host_department,
                visit_reason, equipment_brought, vehicle_plate,
                check_in_time, check_out_time, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "ISG-TEST-001",
            "Caner Demir",
            "12345678901",
            "05331112233",
            "Tekno Lojistik Ltd.",
            "caner@example.com",
            "Murat Bey",
            "Satın Alma & Tedarik",
            "İş Görüşmesi / Toplantı",
            "Laptop",
            "34 ABC 99",
            "2026-09-20T09:30:00Z",
            "",
            "Tesis İçinde (Aktif)",
            "2026-09-20T09:30:00Z"
        ))
        self.conn.commit()

        cur.execute("SELECT * FROM visitors WHERE tracking_code = 'ISG-TEST-001'")
        record = cur.fetchone()
        self.assertIsNotNone(record)
        self.assertEqual(record["visitor_name"], "Caner Demir")
        self.assertEqual(record["status"], "Tesis İçinde (Aktif)")

    def test_visitor_checkout(self):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO visitors (tracking_code, visitor_name, status, check_in_time)
            VALUES (?, ?, ?, ?)
        """, ("ISG-TEST-002", "Burak Yılmaz", "Tesis İçinde (Aktif)", "2026-09-20T10:00:00Z"))
        self.conn.commit()

        cur.execute("""
            UPDATE visitors
            SET status = 'Çıkış Yapıldı', check_out_time = ?
            WHERE tracking_code = ?
        """, ("2026-09-20T11:45:00Z", "ISG-TEST-002"))
        self.conn.commit()

        cur.execute("SELECT status, check_out_time FROM visitors WHERE tracking_code = 'ISG-TEST-002'")
        row = cur.fetchone()
        self.assertEqual(row["status"], "Çıkış Yapıldı")
        self.assertEqual(row["check_out_time"], "2026-09-20T11:45:00Z")

    def test_files_exist(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertTrue(os.path.exists(os.path.join(base_dir, "index.html")), "index.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "admin.html")), "admin.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "api.php")), "api.php bulunamadı")

if __name__ == "__main__":
    unittest.main()
