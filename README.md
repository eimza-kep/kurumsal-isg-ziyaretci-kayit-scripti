# Kurumsal İSG ve Ziyaretçi Kabul Portalı

[![CI Test Suite](https://github.com/eimza-kep/kurumsal-isg-ziyaretci-kayit-scripti/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/kurumsal-isg-ziyaretci-kayit-scripti/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![PHP: 7.4+](https://img.shields.io/badge/PHP-7.4%2B-purple.svg)](https://php.net)

Şirketler, fabrikalar, plazalar, lojistik depolar ve endüstriyel tesisler için; 6331 sayılı İş Sağlığı ve Güvenliği (İSG) Kanunu ile KVKK gereksinimlerine tam uyumlu olarak **ziyaretçi ve alt işveren girişlerini kayıt altına alan**, **İSG güvenlik taahhütnamesini onaylatan**, **yaka kartı basan** ve **acil durum tahliye listesi üreten** kurumsal güvenlik yazılımı.

---

## 🎯 Temel Yetenekler

- **Ziyaretçi Kimlik & Cihaz Bildirimi:** TCKN/Pasaport doğrulama, firma unvanı, görüşülecek personel ve departman seçimi, getirilen laptop/alet seri numaraları ve otopark araç plakası.
- **6331 Sayılı İSG Talimatı ve Açık Rıza Onayı:** Kişisel koruyucu donanım kuralları, toplanma alanları ve kamera kayıt uyarısı.
- **Ziyaretçi Yaka Kartı Çıktısı:** Takip numaralı (`ISG-2026-XXXX`), giriş saatli ve refakatçi departman bilgilerini içeren şık ve yazdırılabilir yaka kartı.
- **Güvenlik & Resepsiyon Yönetim Paneli (`/admin`):**
  - Tesis içinde anlık bulunan aktif ziyaretçi sayacı.
  - Tek tıkla "Çıkış Ver" (Check-out) butonu ile kalış süresi takibi.
  - **🚨 Acil Durum Tahliye Listesi:** Olası bir yangın, deprem veya tatbikat anında tesis içinde bulunan tüm ziyaretçilerin anlık yoklama listesini tek tıkla yazdırma.
  - Excel uyumlu UTF-8 BOM destekli tek tıkla **CSV Dışa Aktarımı**.
- **Sıfır Bağımlılık (Zero-Dependency):**
  - **Python Motoru:** Dahili SQLite veritabanı ile tek tıkla lokalde veya sunucuda çalışır (`server.py`).
  - **PHP Motoru:** Paylaşımlı hosting ve cPanel için hazır JSON REST backend (`api.php`).
  - **Offline Mod:** İnternetsiz çalışma ve tarayıcı yerel hafızası (`localStorage`) desteği.

---

## 🚀 Hızlı Başlangıç

### Windows (Tek Tıkla Çalıştır)
1. Repoyu klonlayın veya indirin.
2. `Baslat.bat` dosyasına çift tıklayın.
3. Otomatik olarak açılır:
   - Ziyaretçi Giriş Formu: `http://localhost:8089`
   - Güvenlik Paneli: `http://localhost:8089/admin`

### Linux & macOS
```bash
git clone https://github.com/eimza-kep/kurumsal-isg-ziyaretci-kayit-scripti.git
cd kurumsal-isg-ziyaretci-kayit-scripti
chmod +x baslat.sh
./baslat.sh
```

### PHP / Paylaşımlı Hosting
Dosyaları sunucunuzdaki `/ziyaretci/` veya `/isg/` dizinine yükleyin. `api.php` otomatik olarak JSON veritabanını oluşturup yönetecektir.

---

## 📊 Mimari ve Dosya Yapısı

```
kurumsal-isg-ziyaretci-kayit-scripti/
├── index.html              # Ziyaretçi kayıt formu ve yaka kartı çıktısı
├── admin.html              # Güvenlik takip ve acil durum tahliye paneli
├── server.py               # Standalone Python SQLite HTTP sunucusu (Port 8089)
├── api.php                 # PHP tabanlı REST backend
├── Baslat.bat              # Windows tek tıkla başlatıcı
├── baslat.sh               # Linux / macOS başlatıcı
├── scripts/
│   └── test_isg.py         # Otomatik test paketi
├── .github/
│   └── workflows/ci.yml    # GitHub Actions CI testi
└── README.md               # Dokümantasyon
```

---

## 🧪 Testleri Çalıştırma

```bash
python scripts/test_isg.py
```

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak sunulmuştur.
