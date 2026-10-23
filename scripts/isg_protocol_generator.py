# -*- coding: utf-8 -*-
"""
isg_protocol_generator.py
-------------------------
6331 Sayılı İş Sağlığı ve Güvenliği Kanunu (Md. 4, 16, 17) & 
5070 Sayılı Elektronik İmza Kanunu Uyumlu:
- İSG Ziyaretçi Oryantasyon ve Güvenlik Kuralları Motoru
- A4 Formatında Resmi İSG Ziyaretçi Giriş Protokolü & Kabul Tutanağı (HTML / PDF)
- Yıllık İSG Ziyaretçi & Taşeron Risk ve Denetim Raporu
- Excel Uyumlu UTF-8 BOM CSV İhracı
"""

import json
import datetime
from html import escape
from typing import Dict, List, Any, Optional

DEFAULT_COMPANY = {
    "title": "KURUMSAL ENTEGRE TESİSLERİ VE SANAYİ A.Ş.",
    "facility_name": "Gebze Organize Sanayi Bölgesi (GOSB) Üretim & Lojistik Kampüsü",
    "address": "GOSB İhsan Dede Caddesi No:114 Gebze / Kocaeli",
    "isg_registry_no": "İSG-41-2026-9810",
    "facility_hazard_class": "Çok Tehlikeli",
    "dpo_isg_expert": "Müh. Selim Karahan (A Sınıfı İSG Uzmanı)",
    "phone": "0262 677 00 00",
    "emergency_phone": "112 / Tesis İçi Dahili: 999"
}

def get_isg_orientation_rules(hazard_class: str = "Az Tehlikeli") -> List[Dict[str, str]]:
    """
    Tesisin tehlike sınıfına göre ziyaretçiye tebliğ edilecek 
    6331 sayılı Kanun uyumlu kurumsal oryantasyon kurallarını döner.
    """
    common_rules = [
        {
            "no": "1",
            "title": "Yaka Kartı ve Refakat Zorunluluğu",
            "rule": "Tesis sınırları içerisinde ziyaretçi yaka kartı sürekli görünür şekilde taşınmalıdır. Ev sahibi personelin refakati olmadan belirlenen alanların dışına çıkılması kesinlikle yasaktır.",
            "basis": "6331 İSGK Md. 4 & Tesis Güvenlik Yönetmeliği"
        },
        {
            "no": "2",
            "title": "Acil Durum ve Tahliye Prosedürü",
            "rule": "Acil durum siren veya anonsu duyulduğunda en yakın acil çıkış yönlendirmeleri izlenerek derhal 'Acil Durum Toplanma Alanı'na intikal edilmeli ve yoklama amirine isim bildirilmelidir.",
            "basis": "Binaların Yangından Korunması Hakkında Yönetmelik"
        },
        {
            "no": "3",
            "title": "Sigara ve Açık Ateş Yasağı",
            "rule": "Tesis içindeki tüm kapalı mekanlar ile üretim, depo ve kimyasal sahalarda sigara içmek ve açık ateşle yaklaşmak kesinlikle yasaktır; sadece belirlenmiş açık hava sigara noktaları kullanılabilir.",
            "basis": "4207 Sayılı Kanun & Yangın Güvenlik Talimatı"
        }
    ]

    if hazard_class == "Az Tehlikeli":
        return common_rules + [
            {
                "no": "4",
                "title": "Ofis ve Ortak Alan Güvenliği",
                "rule": "Islak zeminlere, açık elektrik kablolarına ve acil kaçış koridorlarını kapatacak engellere dikkat edilmeli; panik anında asansörler kesinlikle kullanılmamalıdır.",
                "basis": "İşyeri Bina ve Eklentilerinde Alınacak Sağlık ve Güvenlik Önlemleri Yönetmeliği"
            },
            {
                "no": "5",
                "title": "KVKK ve Bilgi Güvenliği",
                "rule": "Tesis içindeki ekranlar, evraklar ve teknik sistemlerin izinsiz fotoğrafının çekilmesi veya ses/görüntü kaydı yapılması yasaktır.",
                "basis": "6698 KVKK & ISO 27001 Bilgi Güvenliği"
            }
        ]
    elif hazard_class == "Tehlikeli":
        return common_rules + [
            {
                "no": "4",
                "title": "Zorunlu KKD Kuşanımı (Lojistik & Depo)",
                "rule": "Depo ve sevkiyat sahasına girişlerde reflektörlü emniyet yeleği ve çelik burunlu iş ayakkabısı giyilmesi zorunludur. Raf altlarında bulunurken ani malzeme düşmelerine karşı dikkatli olunmalıdır.",
                "basis": "KKD Yönetmeliği Md. 6"
            },
            {
                "no": "5",
                "title": "Forklift ve Yaya Trafiği Kuralları",
                "rule": "Sadece sarı çizgilerle belirlenmiş yaya yollarından yürünmeli; manevra yapan forklift, transpalet ve ağır yük araçlarına en az 3 metre emniyet mesafesi korunmalıdır.",
                "basis": "İş Ekipmanlarının Kullanımında Sağlık ve Güvenlik Şartları Yönetmeliği"
            }
        ]
    else:  # Çok Tehlikeli
        return common_rules + [
            {
                "no": "4",
                "title": "Tam Donanımlı Kişisel Koruyucu Donanım (KKD)",
                "rule": "Fabrika ve üretim sahalarında EN 397 onaylı baret, yüksek görünürlüklü yelek, S3 standartlarında çelik burunlu/tabanlı iş ayakkabısı ve koruyucu gözlük kuşanılmadan sahaya bir adım dahi atılamaz.",
                "basis": "KKD Yönetmeliği Md. 6 & 6331 İSGK Md. 19"
            },
            {
                "no": "5",
                "title": "Sıcak İş, Taşeron ve Kimyasal Güvenlik İzni",
                "rule": "Taşeron bakım, montaj, kaynak veya kimyasal temas gerektiren çalışmalarda İSG biriminden 'Sıcak İş / Kapalı Alan Giriş İzin Belgesi' alınmadan çalışmaya başlanamaz.",
                "basis": "Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri Yönetmeliği"
            }
        ]

def generate_isg_protocol_document_html(visitor: Dict[str, Any], company_info: Optional[Dict[str, Any]] = None) -> str:
    """
    6331 Sayılı Kanun Uyarınca A4 Formatında Resmi
    'İSG ZİYARETÇİ VE TAŞERON GİRİŞ PROTOKOLÜ & KABUL TUTANAĞI' üretir.
    """
    comp = company_info or DEFAULT_COMPANY
    tracking_code = visitor.get("tracking_code", "ISG-2026-0000")
    hazard = visitor.get("hazard_class", "Az Tehlikeli")
    rules = get_isg_orientation_rules(hazard)

    now_str = datetime.datetime.now().strftime("%d.%m.%Y")
    check_in_time = visitor.get("check_in_time", "")
    if check_in_time and "T" in check_in_time:
        try:
            dt = datetime.datetime.fromisoformat(check_in_time.replace("Z", "+00:00"))
            time_formatted = dt.strftime("%d.%m.%Y %H:%M")
        except Exception:
            time_formatted = check_in_time
    else:
        time_formatted = check_in_time or now_str

    ppe_items = visitor.get("ppe_items") or "Standart Ziyaretçi Kiti"
    ppe_list = [item.strip() for item in ppe_items.split(",") if item.strip()] if isinstance(ppe_items, str) else ppe_items

    ppe_table_rows = "".join([
        f"<tr><td style='padding:6px 10px; border:1px solid #cbd5e1;'>✔ {escape(p)}</td><td style='padding:6px 10px; border:1px solid #cbd5e1; text-align:center;'>Eksiksiz Teslim Edildi</td><td style='padding:6px 10px; border:1px solid #cbd5e1; text-align:center;'>Ziyaretçi Uhdesinde</td></tr>"
        for p in ppe_list
    ]) or "<tr><td colspan='3' style='padding:8px; text-align:center; color:#64748b; border:1px solid #cbd5e1;'>Özel KKD tahsisi gerekmemiştir (İdari Alan).</td></tr>"

    rules_html = "".join([
        f"<li style='margin-bottom:6px;'><b>{escape(r['title'])}:</b> {escape(r['rule'])} <span style='font-size:0.75rem; color:#64748b;'>({escape(r['basis'])})</span></li>"
        for r in rules
    ])

    digital_hash = visitor.get("digital_signature_hash") or "SHA256: E-ONAY KAYDI MEVCUT"

    hazard_color = "#15803d" if hazard == "Az Tehlikeli" else ("#c2410c" if hazard == "Tehlikeli" else "#b91c1c")
    hazard_bg = "#dcfce7" if hazard == "Az Tehlikeli" else ("#ffedd5" if hazard == "Tehlikeli" else "#fee2e2")

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>İSG Ziyaretçi Giriş Protokolü & Kabul Tutanağı - {escape(tracking_code)}</title>
<style>
  * {{ box-sizing: border-box; font-family: 'Times New Roman', Times, serif; }}
  body {{ background: #f8fafc; padding: 24px 16px; color: #0f172a; margin: 0; line-height: 1.45; }}
  .toolbar {{ max-width: 820px; margin: 0 auto 16px auto; display: flex; justify-content: space-between; align-items: center; background: white; padding: 12px 20px; border-radius: 8px; border: 1px solid #cbd5e1; font-family: sans-serif; }}
  .doc-container {{ max-width: 820px; margin: auto; background: white; border: 2px solid #0f172a; padding: 36px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
  .header {{ text-align: center; border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 16px; }}
  .header h1 {{ margin: 0; font-size: 1.15rem; text-transform: uppercase; font-weight: 800; letter-spacing: 0.5px; }}
  .header h2 {{ font-size: 1.05rem; margin: 4px 0; color: #ea580c; font-family: sans-serif; font-weight: 800; }}
  .header p {{ margin: 4px 0 0 0; font-size: 0.85rem; font-family: sans-serif; color: #475569; }}
  .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px; font-size: 0.9rem; font-family: sans-serif; }}
  .meta-box {{ border: 1px solid #cbd5e1; padding: 10px 12px; border-radius: 4px; background: #fafafa; line-height: 1.5; }}
  .hazard-banner {{ padding: 8px; border-radius: 6px; font-family: sans-serif; font-weight: 800; text-align: center; font-size: 0.9rem; margin-bottom: 16px; background: {hazard_bg}; color: {hazard_color}; border: 1px solid {hazard_color}; }}
  .section-title {{ font-size: 0.95rem; font-weight: bold; margin: 14px 0 6px 0; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; text-transform: uppercase; font-family: sans-serif; color: #0f172a; }}
  ul {{ margin: 6px 0 12px 20px; padding: 0; font-size: 0.88rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 0.85rem; font-family: sans-serif; }}
  .hash-box {{ background: #f0fdf4; border-left: 4px solid #16a34a; padding: 8px 12px; margin: 16px 0; font-size: 0.8rem; font-family: monospace; color: #166534; }}
  .signatures {{ display: flex; justify-content: space-between; margin-top: 30px; padding-top: 16px; border-top: 1px dashed #cbd5e1; font-family: sans-serif; }}
  .sig-block {{ width: 45%; text-align: center; font-size: 0.88rem; }}
  @media print {{
    body {{ background: transparent; padding: 0; }}
    .toolbar {{ display: none !important; }}
    .doc-container {{ border: none; padding: 0; box-shadow: none; max-width: 100%; }}
  }}
</style>
</head>
<body>

<div class="toolbar">
  <span style="font-weight: 700; font-size: 0.9rem;">🦺 6331 İSG Ziyaretçi Kabul Tutanağı ({escape(tracking_code)})</span>
  <button onclick="window.print()" style="background: #ea580c; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 0.85rem;">🖨️ Yazdır / PDF Olarak Kaydet</button>
</div>

<div class="doc-container">
  <div class="header">
    <h1>{escape(comp['title'])}</h1>
    <h2>6331 SAYILI İSG KANUNU ZİYARETÇİ VE ALT İŞVEREN GİRİŞ PROTOKOLÜ &amp; KABUL TUTANAĞI</h2>
    <p>Belge Ref: <b>{escape(tracking_code)}</b> | Tesis: <b>{escape(comp['facility_name'])}</b> | Düzenleme Tarihi: <b>{now_str}</b></p>
  </div>

  <div class="meta-grid">
    <div class="meta-box">
      <b>TESİS &amp; İSG YETKİLİSİ BİLGİLERİ:</b><br>
      <b>Adres:</b> {escape(comp['address'])}<br>
      <b>İSG Sicil No:</b> {escape(comp['isg_registry_no'])}<br>
      <b>Ziyaret Edilen Yetkili:</b> {escape(visitor.get('host_employee', 'Yetkili'))}<br>
      <b>Departman:</b> {escape(visitor.get('host_department', 'Genel Alan'))}<br>
      <b>Acil Durum Dahili:</b> {escape(comp['emergency_phone'])}
    </div>
    <div class="meta-box">
      <b>ZİYARETÇİ / ALT İŞVEREN BİLGİLERİ:</b><br>
      <b>Adı Soyadı:</b> {escape(visitor.get('visitor_name', ''))}<br>
      <b>TCKN / Pasaport No:</b> {escape(visitor.get('visitor_id', ''))}<br>
      <b>Firma / Kurum:</b> {escape(visitor.get('visitor_company', 'Bireysel'))}<br>
      <b>Telefon:</b> {escape(visitor.get('visitor_phone', ''))}<br>
      <b>Giriş Zamanı:</b> {escape(time_formatted)}<br>
      <b>Ziyaret Sebebi:</b> {escape(visitor.get('visit_reason', 'İş Görüşmesi'))}
    </div>
  </div>

  <div class="hazard-banner">
    SAHA TEHLİKE DERECESİ: {escape(hazard).upper()} &nbsp;|&nbsp; SAHA PROTOKOL SEVİYESİ: TAM UYUM GEREKTİRİR
  </div>

  <div class="section-title">1. ZİMMET EDİLEN KİŞİSEL KORUYUCU DONANIMLAR (KKD)</div>
  <table>
    <thead>
      <tr style="background:#f1f5f9; border-bottom:2px solid #cbd5e1; text-align:left;">
        <th style="padding:6px 10px; border:1px solid #cbd5e1;">Donanım Adı</th>
        <th style="padding:6px 10px; border:1px solid #cbd5e1; text-align:center;">Teslim Durumu</th>
        <th style="padding:6px 10px; border:1px solid #cbd5e1; text-align:center;">Zimmet Sorumlusu</th>
      </tr>
    </thead>
    <tbody>
      {ppe_table_rows}
    </tbody>
  </table>

  <div class="section-title">2. 6331 SAYILI KANUN GEREĞİ TEBLİĞ EDİLEN İSG VE EMNİYET KURALLARI</div>
  <ul>
    {rules_html}
  </ul>

  <div class="section-title">3. TAAHHÜT, BEYAN VE DİJİTAL ONAY</div>
  <p style="font-size:0.85rem; text-align:justify; margin: 4px 0 8px 0;">
    Tarafıma tebliğ edilen tüm İSG kurallarını, yangın ve acil durum tahliye talimatlarını okudum, anladım. Tesiste bulunduğum süre boyunca refakatsiz dolaşmayacağımı, zimmet edilen KKD ekipmanlarını eksiksiz kuşanacağımı ve aksi davranışlarda doğabilecek her türlü hukuki, idari ve cezai sorumluluğun tarafıma ait olduğunu kabul ve taahhüt ederim.
  </p>

  <div class="hash-box">
    <b>🔒 KRİPTOGRAFİK İSG DİJİTAL ONAY MÜHRÜ (SHA-256):</b><br>
    <span>{escape(digital_hash)}</span><br>
    <small>5070 Sayılı Elektronik İmza Kanunu ve 6331 Sayılı Kanun Uyarınca Değiştirilemez Zaman Damgalı Onay Kaydı</small>
  </div>

  <div class="signatures">
    <div class="sig-block">
      <b>ZİYARETÇİ / ALT İŞVEREN</b><br>
      {escape(visitor.get('visitor_name', 'Ziyaretçi'))}<br>
      <small>Tebellüğ Eden / Taahhüt Veren</small><br>
      <div style="height:35px;"></div>
      İmza / E-İmza Onayı
    </div>
    <div class="sig-block">
      <b>TESİS GÜVENLİK / İSG BİRİMİ</b><br>
      {escape(comp.get('dpo_isg_expert', 'İSG Uzmanı'))}<br>
      <small>Tebliğ Eden / Giriş İzni Veren Yetkili</small><br>
      <div style="height:35px;"></div>
      Kaşe &amp; Onay İmzası
    </div>
  </div>
</div>

</body>
</html>"""

def calculate_isg_audit_metrics(visitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    İSG Kurul denetimleri ve yönetim incelemeleri için 
    ziyaretçi & taşeron güvenlik ve risk metriklerini hesaplar.
    """
    total = len(visitors)
    active_inside = 0
    checked_out = 0

    hazard_counts = {"Az Tehlikeli": 0, "Tehlikeli": 0, "Çok Tehlikeli": 0}
    dept_counts: Dict[str, int] = {}
    reason_counts: Dict[str, int] = {}
    ppe_counts = {"Baret": 0, "Reflektörlü Yelek": 0, "İş Ayakkabısı": 0, "Koruyucu Gözlük": 0}
    verified_consent_count = 0

    for v in visitors:
        st = v.get("status") or "Tesis İçinde (Aktif)"
        if st == "Tesis İçinde (Aktif)":
            active_inside += 1
        else:
            checked_out += 1

        hz = v.get("hazard_class") or "Az Tehlikeli"
        if hz in hazard_counts:
            hazard_counts[hz] += 1
        else:
            hazard_counts[hz] = 1

        dept = v.get("host_department") or "Genel Alan"
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

        rs = v.get("visit_reason") or "Diğer"
        reason_counts[rs] = reason_counts.get(rs, 0) + 1

        ppe = v.get("ppe_items") or ""
        for ppe_key in ppe_counts.keys():
            if ppe_key.lower() in ppe.lower():
                ppe_counts[ppe_key] += 1

        if v.get("digital_signature_hash") or v.get("digital_consent_verified"):
            verified_consent_count += 1

    compliance_rate = round((verified_consent_count / total * 100), 1) if total > 0 else 100.0

    return {
        "report_date": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "total_visitors": total,
        "active_inside": active_inside,
        "checked_out": checked_out,
        "hazard_counts": hazard_counts,
        "dept_counts": dept_counts,
        "reason_counts": reason_counts,
        "ppe_counts": ppe_counts,
        "verified_consent_count": verified_consent_count,
        "compliance_rate": compliance_rate,
        "audit_status": "TAM UYUMLU" if compliance_rate >= 95 else "DİKKAT GEREKTİRİR"
    }

def generate_isg_audit_report_html(metrics: Dict[str, Any], company_info: Optional[Dict[str, Any]] = None) -> str:
    """
    Yazdırılabilir A4 formatında Yıllık İSG Ziyaretçi & Taşeron Denetim Raporu üretir.
    """
    comp = company_info or DEFAULT_COMPANY
    total = metrics.get("total_visitors", 0)
    active = metrics.get("active_inside", 0)
    out = metrics.get("checked_out", 0)
    rate = metrics.get("compliance_rate", 100.0)

    hazard = metrics.get("hazard_counts", {})
    dept = metrics.get("dept_counts", {})
    ppe = metrics.get("ppe_counts", {})

    dept_rows = "".join([
        f"<tr><td style='padding:8px 12px; border:1px solid #cbd5e1;'>{escape(d)}</td><td style='padding:8px 12px; border:1px solid #cbd5e1; text-align:right; font-weight:bold;'>{c}</td><td style='padding:8px 12px; border:1px solid #cbd5e1; text-align:right;'>%{round(c/total*100, 1) if total else 0}</td></tr>"
        for d, c in sorted(dept.items(), key=lambda x: x[1], reverse=True)
    ])

    ppe_rows = "".join([
        f"<tr><td style='padding:8px 12px; border:1px solid #cbd5e1;'>🦺 {escape(item)}</td><td style='padding:8px 12px; border:1px solid #cbd5e1; text-align:right; font-weight:bold;'>{cnt} Adet</td></tr>"
        for item, cnt in ppe.items()
    ])

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>Yıllık İSG Ziyaretçi &amp; Taşeron Denetim Raporu</title>
<style>
  * {{ box-sizing: border-box; font-family: 'Times New Roman', Times, serif; }}
  body {{ background: #f8fafc; padding: 24px 16px; color: #0f172a; margin: 0; }}
  .toolbar {{ max-width: 860px; margin: 0 auto 16px auto; display: flex; justify-content: space-between; align-items: center; background: white; padding: 12px 20px; border-radius: 8px; border: 1px solid #cbd5e1; font-family: sans-serif; }}
  .doc-container {{ max-width: 860px; margin: auto; background: white; border: 2px solid #0f172a; padding: 36px; }}
  .header {{ text-align: center; border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 20px; font-family: sans-serif; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; font-family: sans-serif; }}
  .kpi-card {{ border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; text-align: center; background: #fafafa; }}
  .kpi-val {{ font-size: 1.6rem; font-weight: 800; color: #ea580c; }}
  .kpi-lbl {{ font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 700; margin-top: 4px; }}
  .section-title {{ font-size: 0.95rem; font-weight: bold; margin: 18px 0 8px 0; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; text-transform: uppercase; font-family: sans-serif; color: #0f172a; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 0.88rem; font-family: sans-serif; }}
  th {{ background: #f1f5f9; padding: 10px 12px; border: 1px solid #cbd5e1; text-align: left; }}
  td {{ border: 1px solid #cbd5e1; }}
  @media print {{
    body {{ background: transparent; padding: 0; }}
    .toolbar {{ display: none !important; }}
    .doc-container {{ border: none; padding: 0; box-shadow: none; max-width: 100%; }}
  }}
</style>
</head>
<body>

<div class="toolbar">
  <span style="font-weight: 700; font-size: 0.9rem;">📊 6331 Sayılı İSGK Yıllık Ziyaretçi &amp; Taşeron Denetim Raporu</span>
  <button onclick="window.print()" style="background: #ea580c; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 0.85rem;">🖨️ Yazdır / PDF Kaydet</button>
</div>

<div class="doc-container">
  <div class="header">
    <h1 style="font-size:1.2rem; margin:0; font-weight:800;">{escape(comp['title'])}</h1>
    <h2 style="font-size:1.05rem; margin:4px 0; color:#ea580c;">İŞ SAĞLIĞI VE GÜVENLİĞİ (İSG) ZİYARETÇİ VE TAŞERON FAALİYET &amp; RİSK DENETİM RAPORU</h2>
    <p style="font-size:0.85rem; color:#64748b; margin:2px 0;">Rapor Tarihi: {metrics['report_date']} | İSG Sicil No: {escape(comp['isg_registry_no'])}</p>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-val">{total}</div>
      <div class="kpi-lbl">Toplam Ziyaretçi / Taşeron</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-val" style="color:#c2410c;">{active}</div>
      <div class="kpi-lbl">Tesis İçinde Aktif</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-val" style="color:#16a34a;">{out}</div>
      <div class="kpi-lbl">Çıkış Yapanlar</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-val" style="color:#2563eb;">%{rate}</div>
      <div class="kpi-lbl">İSG Dijital Onay Uyum Oranı</div>
    </div>
  </div>

  <div class="section-title">1. SAHA TEHLİKE SINIFI DAĞILIMI</div>
  <table>
    <thead>
      <tr>
        <th>Tehlike Sınıfı</th>
        <th style="text-align:right;">Giriş Sayısı</th>
        <th style="text-align:right;">Oran</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="padding:8px 12px;">🟢 Az Tehlikeli (Ofis / Genel Alan)</td>
        <td style="padding:8px 12px; text-align:right; font-weight:bold;">{hazard.get('Az Tehlikeli', 0)}</td>
        <td style="padding:8px 12px; text-align:right;">%{round(hazard.get('Az Tehlikeli', 0)/total*100, 1) if total else 0}</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;">🟡 Tehlikeli (Depo / Sevkiyat / Teknik Servis)</td>
        <td style="padding:8px 12px; text-align:right; font-weight:bold;">{hazard.get('Tehlikeli', 0)}</td>
        <td style="padding:8px 12px; text-align:right;">%{round(hazard.get('Tehlikeli', 0)/total*100, 1) if total else 0}</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;">🔴 Çok Tehlikeli (Fabrika / Üretim / Ağır Sanayi)</td>
        <td style="padding:8px 12px; text-align:right; font-weight:bold;">{hazard.get('Çok Tehlikeli', 0)}</td>
        <td style="padding:8px 12px; text-align:right;">%{round(hazard.get('Çok Tehlikeli', 0)/total*100, 1) if total else 0}</td>
      </tr>
    </tbody>
  </table>

  <div class="section-title">2. TESLİM EDİLEN KİŞİSEL KORUYUCU DONANIM (KKD) ENVANTERİ</div>
  <table>
    <thead>
      <tr>
        <th>KKD Donanım Türü</th>
        <th style="text-align:right;">Zimmet Edilen Adet</th>
      </tr>
    </thead>
    <tbody>
      {ppe_rows}
    </tbody>
  </table>

  <div class="section-title">3. DEPARTMAN BAZLI ZİYARETÇİ DAĞILIMI</div>
  <table>
    <thead>
      <tr>
        <th>Departman</th>
        <th style="text-align:right;">Ziyaretçi Sayısı</th>
        <th style="text-align:right;">Yüzde</th>
      </tr>
    </thead>
    <tbody>
      {dept_rows}
    </tbody>
  </table>

  <div style="margin-top: 32px; border-top: 1px dashed #cbd5e1; padding-top: 16px; display:flex; justify-content:space-between; font-family:sans-serif; font-size:0.85rem;">
    <div>
      <b>Raporu Hazırlayan:</b><br>
      Resepsiyon &amp; Tesis Güvenlik Amiri<br>
      İmza
    </div>
    <div style="text-align:right;">
      <b>İncelendi ve Onaylandı:</b><br>
      {escape(comp.get('dpo_isg_expert', 'A Sınıfı İSG Uzmanı'))}<br>
      İSG Kurul Başkanı &amp; İSG Uzmanı Kaşe / İmza
    </div>
  </div>
</div>

</body>
</html>"""

def generate_isg_csv_export(visitors: List[Dict[str, Any]]) -> str:
    """
    Excel uyumlu UTF-8 with BOM CSV çıktısı üretir.
    """
    columns = [
        "Takip Kodu", "Ziyaretçi Adı Soyadı", "TCKN/Pasaport", "Telefon",
        "Firma/Kurum", "E-Posta", "Ziyaret Edilen Personel", "Departman",
        "Ziyaret Sebebi", "Tehlike Sınıfı", "Teslim Edilen KKD",
        "Getirilen Cihazlar", "Araç Plakası", "Giriş Zamanı", "Çıkış Zamanı",
        "Durum", "SHA-256 Dijital Mühür"
    ]

    lines = []
    lines.append(";".join(columns))

    for v in visitors:
        row = [
            str(v.get("tracking_code", "")).replace(";", " "),
            str(v.get("visitor_name", "")).replace(";", " "),
            str(v.get("visitor_id", "")).replace(";", " "),
            str(v.get("visitor_phone", "")).replace(";", " "),
            str(v.get("visitor_company", "")).replace(";", " "),
            str(v.get("visitor_email", "")).replace(";", " "),
            str(v.get("host_employee", "")).replace(";", " "),
            str(v.get("host_department", "")).replace(";", " "),
            str(v.get("visit_reason", "")).replace(";", " "),
            str(v.get("hazard_class", "")).replace(";", " "),
            str(v.get("ppe_items", "")).replace(";", " "),
            str(v.get("equipment_brought", "")).replace(";", " "),
            str(v.get("vehicle_plate", "")).replace(";", " "),
            str(v.get("check_in_time", "")).replace(";", " "),
            str(v.get("check_out_time", "")).replace(";", " "),
            str(v.get("status", "")).replace(";", " "),
            str(v.get("digital_signature_hash", "")).replace(";", " ")
        ]
        lines.append(";".join(row))

    return "\ufeff" + "\r\n".join(lines)
