# -*- coding: utf-8 -*-
import unittest
import os
import sys
import sqlite3

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server
from scripts.isg_digital_signature import (
    generate_isg_consent_hash,
    verify_isg_consent_hash,
    generate_sms_otp_code,
    get_evacuation_report
)
from scripts.isg_protocol_generator import (
    get_isg_orientation_rules,
    generate_isg_protocol_document_html,
    calculate_isg_audit_metrics,
    generate_isg_audit_report_html,
    generate_isg_csv_export
)

class TestVisitorISGSystem(unittest.TestCase):
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

    def test_database_table_and_columns_exist(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='visitors'")
        row = cur.fetchone()
        self.assertIsNotNone(row, "visitors tablosu oluşturulmuş olmalıdır.")

        cur.execute("PRAGMA table_info(visitors)")
        columns = [r[1] for r in cur.fetchall()]
        self.assertIn("tracking_code", columns)
        self.assertIn("hazard_class", columns)
        self.assertIn("ppe_items", columns)
        self.assertIn("digital_signature_hash", columns)
        self.assertIn("digital_consent_verified", columns)

    def test_visitor_insert_and_retrieve(self):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO visitors (
                tracking_code, visitor_name, visitor_id, visitor_phone,
                visitor_company, visitor_email, host_employee, host_department,
                visit_reason, equipment_brought, vehicle_plate,
                hazard_class, ppe_items, digital_signature_hash, digital_consent_verified,
                check_in_time, check_out_time, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            "Çok Tehlikeli",
            "Baret, Yelek, İş Ayakkabısı",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            1,
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
        self.assertEqual(record["hazard_class"], "Çok Tehlikeli")
        self.assertEqual(record["ppe_items"], "Baret, Yelek, İş Ayakkabısı")

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

    def test_digital_signature_hash_and_verification(self):
        sample_visitor = {
            "visitor_id": "98765432109",
            "visitor_name": "Ayşe Yılmaz",
            "visitor_phone": "05442223344",
            "hazard_class": "Tehlikeli",
            "ppe_items": "Baret, Yelek",
            "check_in_time": "2026-10-23T10:00:00"
        }
        digest = generate_isg_consent_hash(sample_visitor)
        self.assertTrue(len(digest) == 64, "SHA-256 hash 64 karakter olmalıdır.")

        # Doğrulama testi
        is_valid = verify_isg_consent_hash(sample_visitor, digest)
        self.assertTrue(is_valid, "Bütünlüğü korunmuş taahhüt doğrulanmalıdır.")

        # Değiştirilmiş veri ile doğrulama testi (sahtecilik denetimi)
        tampered_visitor = sample_visitor.copy()
        tampered_visitor["visitor_name"] = "Farklı Kişi"
        is_invalid = verify_isg_consent_hash(tampered_visitor, digest)
        self.assertFalse(is_invalid, "Değiştirilmiş verinin hash doğrulaması başarısız olmalıdır.")

    def test_emergency_evacuation_report(self):
        mock_visitors = [
            {"visitor_name": "Ali Veli", "host_department": "Üretim & Fabrika Sahası", "status": "Tesis İçinde (Aktif)"},
            {"visitor_name": "Zeynep Kaya", "host_department": "Üretim & Fabrika Sahası", "status": "Tesis İçinde (Aktif)"},
            {"visitor_name": "Kemal Demir", "host_department": "Bilgi İşlem & IT", "status": "Tesis İçinde (Aktif)"},
            {"visitor_name": "Mustafa Çelik", "host_department": "Yönetim", "status": "Çıkış Yapıldı"},
        ]
        report = get_evacuation_report(mock_visitors)

        # Çıkış yapan hariç, sadece içeride olan 3 kişi raporlanmalıdır
        self.assertEqual(report["total_inside_count"], 3)
        self.assertEqual(report["department_summary"]["Üretim & Fabrika Sahası"], 2)
        self.assertEqual(report["department_summary"]["Bilgi İşlem & IT"], 1)
        self.assertNotIn("Yönetim", report["department_summary"])

    def test_sms_otp_generation(self):
        otp = generate_sms_otp_code()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    def test_files_exist(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertTrue(os.path.exists(os.path.join(base_dir, "index.html")), "index.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "admin.html")), "admin.html bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "server.py")), "server.py bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "api.php")), "api.php bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "scripts", "isg_digital_signature.py")), "isg_digital_signature.py bulunamadı")
        self.assertTrue(os.path.exists(os.path.join(base_dir, "scripts", "isg_protocol_generator.py")), "isg_protocol_generator.py bulunamadı")

    def test_isg_orientation_rules_by_hazard_class(self):
        rules_low = get_isg_orientation_rules("Az Tehlikeli")
        self.assertGreaterEqual(len(rules_low), 5)
        self.assertTrue(any("Yaka Kartı" in r["title"] for r in rules_low))

        rules_mid = get_isg_orientation_rules("Tehlikeli")
        self.assertGreaterEqual(len(rules_mid), 5)
        self.assertTrue(any("Forklift" in r["title"] or "KKD" in r["title"] for r in rules_mid))

        rules_high = get_isg_orientation_rules("Çok Tehlikeli")
        self.assertGreaterEqual(len(rules_high), 5)
        self.assertTrue(any("Sıcak İş" in r["title"] or "Donanımlı" in r["title"] for r in rules_high))

    def test_isg_protocol_document_html_generation(self):
        sample_visitor = {
            "tracking_code": "ISG-2026-TEST-DOC",
            "visitor_name": "Mustafa Kılıç",
            "visitor_id": "11223344556",
            "visitor_phone": "05559876543",
            "visitor_company": "Kılıç Mühendislik & İmalat A.Ş.",
            "host_employee": "Ahmet Bey",
            "host_department": "Üretim & Fabrika Sahası",
            "hazard_class": "Çok Tehlikeli",
            "ppe_items": "Baret, Reflektörlü Yelek, İş Ayakkabısı, Koruyucu Gözlük",
            "visit_reason": "Taşeron & Montaj Çalışması",
            "check_in_time": "2026-10-23T08:30:00Z",
            "digital_signature_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
        html = generate_isg_protocol_document_html(sample_visitor)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("ISG-2026-TEST-DOC", html)
        self.assertIn("6331 SAYILI İSG KANUNU", html)
        self.assertIn("ZİYARETÇİ VE ALT İŞVEREN GİRİŞ PROTOKOLÜ &amp; KABUL TUTANAĞI", html)
        self.assertIn("Mustafa Kılıç", html)
        self.assertIn("SAHA TEHLİKE DERECESİ", html)
        self.assertIn("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", html)
        self.assertIn("@media print", html)

    def test_isg_audit_metrics_calculation(self):
        mock_visitors = [
            {"status": "Tesis İçinde (Aktif)", "hazard_class": "Az Tehlikeli", "host_department": "Yönetim", "ppe_items": "", "digital_signature_hash": "hash1"},
            {"status": "Tesis İçinde (Aktif)", "hazard_class": "Tehlikeli", "host_department": "Depo", "ppe_items": "Baret, Yelek", "digital_signature_hash": "hash2"},
            {"status": "Çıkış Yapıldı", "hazard_class": "Çok Tehlikeli", "host_department": "Fabrika", "ppe_items": "Baret, Yelek, İş Ayakkabısı", "digital_signature_hash": "hash3"},
        ]
        metrics = calculate_isg_audit_metrics(mock_visitors)
        self.assertEqual(metrics["total_visitors"], 3)
        self.assertEqual(metrics["active_inside"], 2)
        self.assertEqual(metrics["checked_out"], 1)
        self.assertEqual(metrics["hazard_counts"]["Az Tehlikeli"], 1)
        self.assertEqual(metrics["hazard_counts"]["Tehlikeli"], 1)
        self.assertEqual(metrics["hazard_counts"]["Çok Tehlikeli"], 1)
        self.assertEqual(metrics["compliance_rate"], 100.0)
        self.assertEqual(metrics["audit_status"], "TAM UYUMLU")

    def test_isg_audit_report_html_generation(self):
        metrics = {
            "report_date": "23.10.2026 21:00:00",
            "total_visitors": 12,
            "active_inside": 4,
            "checked_out": 8,
            "compliance_rate": 100.0,
            "hazard_counts": {"Az Tehlikeli": 5, "Tehlikeli": 4, "Çok Tehlikeli": 3},
            "dept_counts": {"Üretim": 6, "Depo": 4, "IT": 2},
            "ppe_counts": {"Baret": 7, "Reflektörlü Yelek": 7, "İş Ayakkabısı": 5, "Koruyucu Gözlük": 3}
        }
        report_html = generate_isg_audit_report_html(metrics)
        self.assertIn("<!DOCTYPE html>", report_html)
        self.assertIn("İŞ SAĞLIĞI VE GÜVENLİĞİ (İSG) ZİYARETÇİ VE TAŞERON FAALİYET &amp; RİSK DENETİM RAPORU", report_html)
        self.assertIn("Toplam Ziyaretçi / Taşeron", report_html)
        self.assertIn("12", report_html)
        self.assertIn("Zimmet Edilen Adet", report_html)

    def test_isg_csv_export(self):
        visitors = [
            {
                "tracking_code": "ISG-2026-9001",
                "visitor_name": "Selin Aydın",
                "visitor_id": "12345678901",
                "visitor_phone": "05321112233",
                "visitor_company": "Aydın Lojistik",
                "visitor_email": "selin@aydin.com",
                "host_employee": "Mehmet Bey",
                "host_department": "Lojistik",
                "visit_reason": "Mal Teslimi",
                "hazard_class": "Tehlikeli",
                "ppe_items": "Baret, Yelek",
                "equipment_brought": "El Terminali",
                "vehicle_plate": "34 ABC 789",
                "check_in_time": "2026-10-23T11:00:00Z",
                "check_out_time": "",
                "status": "Tesis İçinde (Aktif)",
                "digital_signature_hash": "a1b2c3d4e5f6..."
            }
        ]
        csv_out = generate_isg_csv_export(visitors)
        self.assertTrue(csv_out.startswith("\ufeff"), "Excel uyumlu UTF-8 BOM olmalıdır.")
        self.assertIn("ISG-2026-9001", csv_out)
        self.assertIn("Selin Aydın", csv_out)
        self.assertIn("Tehlikeli", csv_out)
        self.assertIn("Baret, Yelek", csv_out)

if __name__ == "__main__":
    unittest.main()
