#  Kelime Ezberleme Uygulaması

Bu proje, Manisa Celal Bayar Üniversitesi YZM-2122 dersi kapsamında dönem projesi olarak geliştirilmiştir. Ticari amaçla kullanılmaması gerekmektedir. Proje, Aykut Gökbulut, İbrahim Delibay, Nurettin Oğuz ve Oğuzhan Deveci tarafından hazırlanmıştır.Kullanıcıların İngilizce kelimeleri öğrenmesini kolaylaştırmak için geliştirilmiş bir **web tabanlı ezber uygulamasıdır**. Kullanıcılar kelime ekleyebilir, test çözebilir, performans analizlerini görebilir ve Wordle oyunuyla kelimeleri pekiştirebilir.

---

##  Özellikler

- Kullanıcı kayıt / giriş / çıkış sistemi
- Şifre sıfırlama (token destekli form üzerinden)
- Yeni kelime ekleme (görsel, örnek cümle, kategori dahil)
- Global kelime havuzundan otomatik kelime ataması
- Günlük sınav sistemi (6 tekrar kuralı ve zamanlı tekrarlar: 1 gün, 1 hafta, 1 ay, ...)
- Başarı yüzdesi ve kategori bazlı analiz raporu
- Wordle benzeri tahmin oyunu (ezberlenen kelimelerle)
- Ayarlardan günlük soru sayısı belirleme

---

## Kullanılan Teknolojiler

- **Backend**: Python, Flask
- **Veritabanı**: MSSQL (SQL Server)
- **Frontend**: HTML, CSS, Bootstrap 5
- **Oturum Yönetimi**: Flask-Login
- **Formlar**: Flask-WTF
- **Şifreleme**: Werkzeug
- **Token İşlemleri**: itsdangerous
- **PDF Raporlama**: ReportLab

---

##  Kurulum ve Çalıştırma

### 1. Gerekli bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
