# Kurumsal İSG ve Ziyaretçi Kabul Portalı

[![CI Test Suite](https://github.com/eimza-kep/kurumsal-isg-ziyaretci-kayit-scripti/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/kurumsal-isg-ziyaretci-kayit-scripti/actions/workflows/ci.yml)
[![Canlı Demo](https://img.shields.io/badge/Demo-Canl%C4%B1%20Test%20Et-brightgreen.svg)](https://eimza-kep.github.io/kurumsal-isg-ziyaretci-kayit-scripti/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![PHP: 7.4+](https://img.shields.io/badge/PHP-7.4%2B-purple.svg)](https://php.net)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)

Şirketler, fabrikalar, plazalar, lojistik depolar ve endüstriyel tesisler için; **6331 sayılı İş Sağlığı ve Güvenliği (İSG) Kanunu**, **5070 sayılı Elektronik İmza Kanunu** ile **KVKK** gereksinimlerine tam uyumlu olarak **ziyaretçi ve alt işveren girişlerini kayıt altına alan**, **İSG taahhütnamesini SHA-256 dijital mührü ve SMS OTP ile onaylatan**, **yaka kartı basan** ve **yangın/deprem anında tek tıkla bina acil tahliye yoklama listesi üreten** kurumsal güvenlik yazılımı.

---

## 🎯 Temel Yetenekler ve Yenilikler

### 1. 🚨 Acil Durum (Yangın/Deprem/Tatbikat) Tek Tıkla Bina Tahliye Listesi (Issue #1)
- Olası bir acil durumda (yangın, deprem veya İSG tahliye tatbikatı alarmı), tesiste halen içeride bulunan (çıkış yapmamış) tüm ziyaretçi, alt işveren ve firma personelinin anlık listesi tek tıkla alınır.
- **Toplanma Alanı Yoklama Çıktısı:** Ziyaretçi adı, telefonu, firması, görüştüğü personel, departmanı ve yoklama kutucuğu içeren A4 formatında yazdırılabilir veya PDF olarak kaydedilebilir yoklama listesi.
- **Departman Bazlı Sayım:** Üretim sahası, depo, IT vb. birimlerde kaç kişinin bulunduğu anlık olarak özetlenir.
- **Otomasyon ve Yangın Alarm Entegrasyonu:** Tesis otomasyon sistemleri veya SMS acil durum botları için `/api/acil-tahliye` JSON API uç noktası hazır olarak sunulur.

### 2. ✍️ İSG Taahhütnamesi Dijital Onay & SMS OTP Kancası (Issue #2)
- **Tesis Tehlike Sınıfı Seçimi:**
  - **Az Tehlikeli:** Ofis ve genel idari binalar.
  - **Tehlikeli:** Depo, lojistik, sevkiyat ve atölye sahaları.
  - **Çok Tehlikeli:** Fabrika, ağır sanayi, kimyasal ve inşaat/şantiye alanları.
- **Zorunlu KKD (Kişisel Koruyucu Donanım) Taahhüdü:** Tehlikeli ve Çok Tehlikeli alanlara girişlerde baret, reflektörlü ikaz yeleği, çelik burunlu iş ayakkabısı ve koruyucu gözlük taahhüdü otomatik olarak devreye girer.
- **Kriptografik Dijital Mühür (SHA-256 Consent Hash):** Ziyaretçinin kimlik numarası, adı, tehlike sınıfı, KKD seçimleri ve onay zamanı kriptografik olarak imzalanır; basılan yaka kartına ve yönetim paneline denetime hazır SHA-256 mührü olarak işlenir.
- **SMS OTP Onay Kancası:** Tesis girişinde cep telefonuna gönderilen 6 haneli doğrulama kodu ile dijital onay kanıtı oluşturulur.

### 3. 📄 A4 Resmi İSG Ziyaretçi Giriş Protokolü & Kabul Tutanağı (HTML / PDF)
- 6331 Sayılı Kanun Madde 4 ve 17 uyarınca, Çalışma ve Sosyal Güvenlik Bakanlığı iş müfettişleri denetimlerinde ibraz edilecek resmi A4 formatında **İSG Ziyaretçi Kabul Tutanağı**.
- Tesis resmi anteti, ziyaretçi kimlik bilgileri, ziyaret edilen yetkili, teslim edilen KKD zimmet listesi, 5 temel İSG kuralı tebliği, SHA-256 dijital mührü ve imza/kaşe alanları içerir.
- Form doldurulduğunda ziyaretçi tarafından doğrudan indirilebilir veya `/admin` paneli üzerinden tek tıkla yazdırılabilir.

### 4. 📊 Yıllık İSG Ziyaretçi & Taşeron Faaliyet ve Risk Denetim Raporu
- Tesis tehlike sınıfı dağılımı (Az Tehlikeli, Tehlikeli, Çok Tehlikeli), teslim edilen KKD donanım envanteri, departman dağılımı ve İSG dijital onay uyum oranını (%100 hedefi) hesaplar.
- A4 formatında yazdırılabilir resmi İSG Kurul Denetim Raporu (`/api/isg-denetim-raporu-html`) ve otomasyonlar için JSON API (`/api/isg-denetim-raporu-json`).

### 5. 🪪 Yazdırılabilir Ziyaretçi Yaka Kartı
- Takip kodu (`ISG-2026-XXXX`), ad-soyad, firma, tehlike sınıfı rozeti, görüşülen yetkili ve dijital onay parmak izini içeren kurumsal yaka kartı formatı.

### 6. 🦺 Güvenlik & Resepsiyon Yönetim Paneli (`/admin`)
- Tesis içi aktif ziyaretçi sayacı ve tek tıkla çıkış (Check-out) işlemi.
- Departman ve tehlike sınıfına göre filtreleme ve arama.
- Excel uyumlu UTF-8 BOM destekli tek tıkla Türkçe karakter korumalı CSV dışa aktarımı (`/api/export-csv`).

---

## 🚀 Hızlı Başlangıç

### Windows (Tek Tıkla Çalıştır)
1. Repoyu klonlayın veya indirin.
2. `Baslat.bat` dosyasına çift tıklayın.
3. Otomatik olarak açılır:
   - **Ziyaretçi Giriş Portalı:** `http://localhost:8089`
   - **Güvenlik Yönetim Paneli:** `http://localhost:8089/admin`

### Linux & macOS
```bash
git clone https://github.com/eimza-kep/kurumsal-isg-ziyaretci-kayit-scripti.git
cd kurumsal-isg-ziyaretci-kayit-scripti
chmod +x baslat.sh
./baslat.sh
```

### Docker ile Çalıştırma
```bash
docker build -t isg-ziyaretci .
docker run -d -p 8089:8089 --name isg-app isg-ziyaretci
```

### PHP / Paylaşımlı Hosting (cPanel / Plesk)
Dosyaları sunucunuzdaki `/ziyaretci/` veya `/isg/` dizinine yükleyin. `api.php` otomatik olarak JSON veritabanını oluşturup yönetecektir.

---

## 📡 REST API Referansı

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `POST` | `/api/ziyaretci-giris` | Yeni ziyaretçi kaydını alır, SHA-256 İSG dijital mührünü üretir ve takip kodu döner. |
| `GET` | `/api/ziyaretciler` | Tüm ziyaretçileri ve güncel durumlarını listeler. |
| `POST` | `/api/ziyaretci-cikis` | Ziyaretçinin tesisten çıkış saatini kaydeder ve durumunu 'Çıkış Yapıldı' olarak günceller. |
| `GET` | `/api/isg-oryantasyon-kurallari?hazard=...` | Tesis tehlike sınıfına göre 6331 sayılı Kanun uyumlu güvenlik talimatlarını döner. |
| `GET` | `/api/isg-tutanak-html?code=...` | Ziyaretçinin resmi A4 formatındaki İSG Kabul Tutanağını üretir. |
| `GET` | `/api/isg-denetim-raporu-json` | Yıllık İSG ziyaretçi/taşeron denetim ve risk analizi metriklerini döner. |
| `GET` | `/api/isg-denetim-raporu-html` | Yazdırılabilir A4 formatında Yıllık İSG Faaliyet ve Denetim Raporu sunar. |
| `GET` | `/api/export-csv` | Excel uyumlu UTF-8 BOM destekli tam ziyaretçi listesini CSV formatında indirir. |
| `GET` | `/api/acil-tahliye` | Yangın/deprem anında binada içeride kalan aktif kişilerin acil tahliye raporunu döner. |
| `GET` | `/api/generate-otp` | Ziyaretçi telefon doğrulaması için 6 haneli SMS OTP kodu üretir. |
| `GET` | `/api/isg-taahhut-dogrula?code=...` | Kayıtlı İSG taahhütname hash'inin veri bütünlüğünü ve geçerliliğini denetler. |
| `GET` | `/health` | Servis sağlık durum kontrolü. |

---

## 📊 Mimari ve Dosya Yapısı

```
kurumsal-isg-ziyaretci-kayit-scripti/
├── index.html              # Ziyaretçi kayıt formu, dinamik İSG kuralları, KKD & yaka kartı
├── admin.html              # Güvenlik yönetim paneli, denetim raporu & acil durum tahliyesi
├── server.py               # SQLite veritabanlı standalone Python HTTP sunucusu (Port 8089)
├── api.php                 # PHP tabanlı JSON REST backend (cPanel / Paylaşımlı hosting)
├── Dockerfile              # Docker container dağıtım dosyası
├── Baslat.bat              # Windows tek tıkla başlatıcı
├── baslat.sh               # Linux / macOS başlatıcı
├── scripts/
│   ├── isg_digital_signature.py  # SHA-256 dijital mühür, OTP ve acil tahliye motoru
│   ├── isg_protocol_generator.py # A4 İSG Kabul Tutanağı, oryantasyon kuralları & denetim raporu
│   └── test_isg.py               # 12/12 testten oluşan otomatik birim ve entegrasyon test paketi
├── .github/
│   └── workflows/ci.yml    # GitHub Actions CI testi
└── README.md               # Dokümantasyon
```

---

## 🧪 Testleri Çalıştırma

Tüm fonksiyonları ve kriptografik onay mekanizmasını test etmek için:

```bash
python scripts/test_isg.py
```

---

## 🌐 Kurumsal & E-Dönüşüm Açık Kaynak Ekosistemi

Bu ziyaretçi ve İSG kayıt aracı, [@eimza-kep](https://github.com/eimza-kep) açık kaynak ekosisteminin tesis güvenliği ve iş sağlığı modülüdür. İlgili diğer araçlar:

* 🔒 [kurumsal-kvkk-basvuru-scripti](https://github.com/eimza-kep/kurumsal-kvkk-basvuru-scripti) - Ziyaretçi kişisel verileri, kamera kayıtları ve KVKK başvuru/takip portali.
* 👥 [kurumsal-ik-is-basvuru-scripti](https://github.com/eimza-kep/kurumsal-ik-is-basvuru-scripti) - Kurum içine iş görüşmesine gelen adayların takibi ve İSG bilgilendirmesi.
* 🏢 [kurumsal-bayi-basvuru-scripti](https://github.com/eimza-kep/kurumsal-bayi-basvuru-scripti) - Bayi ve yetkili servis ön kayıt ve akreditasyon portali.
* ⭐ [kobi-musteri-memnuniyet-nps-scripti](https://github.com/eimza-kep/kobi-musteri-memnuniyet-nps-scripti) - KOBİ müşteri deneyimi, NPS analitiği ve Google Haritalar kancası.
* 🌟 [awesome-turkiye-e-donusum](https://github.com/eimza-kep/awesome-turkiye-e-donusum) - Türkiye e-Dönüşüm açık kaynak araçları ve kütüphaneleri kürasyonu.

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak sunulmuştur.
