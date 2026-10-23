# -*- coding: utf-8 -*-
"""
isg_digital_signature.py
------------------------
6331 Sayılı İSG Kanunu & 5070 Sayılı Elektronik İmza Kanunu Uyumlu
İSG Taahhütname Dijital Onay ve Acil Durum Tahliye Motoru.
"""

import hashlib
import json
import random
import datetime
from typing import Dict, List, Any, Optional

def generate_isg_consent_hash(visitor_data: Dict[str, Any]) -> str:
    """
    Ziyaretçinin onayladığı İSG taahhütnamesi, kimlik bilgileri, tehlike sınıfı
    ve zaman damgası üzerinden değiştirilemez SHA-256 dijital onay özeti üretir.
    """
    tc = str(visitor_data.get("visitor_id", "")).strip()
    name = str(visitor_data.get("visitor_name", "")).strip().upper()
    phone = str(visitor_data.get("visitor_phone", "")).strip()
    hazard_class = str(visitor_data.get("hazard_class", "Az Tehlikeli")).strip()
    time_str = str(visitor_data.get("check_in_time", "")).strip()
    ppe = str(visitor_data.get("ppe_items", "")).strip()

    raw_payload = f"ISG-TERMS-6331|TC:{tc}|NAME:{name}|TEL:{phone}|HAZARD:{hazard_class}|PPE:{ppe}|TIME:{time_str}"
    digest = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
    return digest

def verify_isg_consent_hash(visitor_data: Dict[str, Any], expected_hash: str) -> bool:
    """
    Kayıtlı dijital imza özetinin veri bütünlüğünü doğrular.
    """
    if not expected_hash:
        return False
    computed = generate_isg_consent_hash(visitor_data)
    return computed.lower() == expected_hash.strip().lower()

def generate_sms_otp_code() -> str:
    """6 haneli SMS onay doğrulama kodu üretir."""
    return f"{random.randint(100000, 999999)}"

def get_evacuation_report(visitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Fabrika/ofis acil durumlarında (yangın, deprem, tahliye tatbikatı)
    tesiste halen içeride bulunan aktif ziyaretçilerin tahliye listesini üretir.
    """
    inside_visitors = [
        v for v in visitors 
        if (v.get("status") or "Tesis İçinde (Aktif)") == "Tesis İçinde (Aktif)"
    ]

    # Departmanlara göre grupla
    dept_groups: Dict[str, List[Dict[str, Any]]] = {}
    for v in inside_visitors:
        dept = v.get("host_department") or "Genel Alan"
        if dept not in dept_groups:
            dept_groups[dept] = []
        dept_groups[dept].append(v)

    now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    return {
        "report_title": "🚨 ACİL DURUM BİNA VE TESİS TAHLİYE YOKLAMA LİSTESİ",
        "generated_at": now_str,
        "total_inside_count": len(inside_visitors),
        "department_summary": {dept: len(items) for dept, items in dept_groups.items()},
        "active_visitors": inside_visitors,
        "grouped_by_department": dept_groups
    }
