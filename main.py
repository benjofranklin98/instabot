import os
import sys

# Bulut sunucuda kütüphane hatalarını sıfıra indirmek için otomatik yükleme mekanizması
try:
    import telebot
    from instagrapi import Client
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install pyTelegramBotAPI instagrapi requests")
    import telebot
    from instagrapi import Client
    import requests

# --- AYARLAR (BİLGİLERİN SABİT KALACAK) ---
TELEGRAM_BOT_TOKEN = "BURAYA_TELEGRAM_BOT_TOKENINI_YAZ"
MY_INSTAGRAM_USER = "gercek_instagram_kullanici_adin"  # Profilin giydirileceği sabit hesabın
MY_INSTAGRAM_PASS = "gercek_instagram_sifren"          # O sabit hesabın şifresi

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
cl = Client()

def instagram_giris():
    print("🔐 Sabit Instagram hesabına giriş yapılıyor...")
    if os.path.exists("instagram_session.json"):
        try:
            cl.load_settings("instagram_session.json")
        except:
            pass
    try:
        cl.login(MY_INSTAGRAM_USER, MY_INSTAGRAM_PASS)
        cl.dump_settings("instagram_session.json")
        print("✅ Instagram girişi başarılı!")
        return True
    except Exception as e:
        print(f"❌ Instagram giriş hatası: {e}")
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Bot hazır! Bilgilerini kopyalamak (çalmak) istediğin kaynak kullanıcının adını yazıp gönder. Her yeni mesajında o hesabı kopyalayıp senin sabit hesabına giydireceğim.")

@bot.message_handler(func=lambda message: True)
def profil_giydir(message):
    kaynak_hesap = message.text.strip().replace("@", "")
    bot.reply_to(message, f"⏳ @{kaynak_hesap} profil bilgileri çekiliyor ve senin hesabına giydiriliyor... Lütfen bekleyin.")

    try:
        # 1. Bilgileri kopyalayacağımız (kaynak) hesaptan verileri çekiyoruz
        kaynak_info = cl.user_info_by_username(kaynak_hesap)
        bio = kaynak_info.biography if kaynak_info.biography else ""
        isim = kaynak_info.full_name if kaynak_info.full_name else kaynak_hesap
        resim_url = kaynak_info.profile_pic_url

        # Profil fotoğrafını geçici olarak indir
        resim_datasi = requests.get(resim_url).content
        with open("gecici_profil.jpg", "wb") as f:
            f.write(resim_datasi)

        # 2. Çektiğimiz bilgileri SENİN sabit hesabına (MY_INSTAGRAM_USER) giydiriyoruz
        cl.account_edit(full_name=isim, biography=bio)
        cl.account_change_picture("gecici_profil.jpg")

        # Geçici resmi siliyoruz
        if os.path.exists("gecici_profil.jpg"):
            os.remove("gecici_profil.jpg")

        bot.reply_to(message, f"🎉 İşlem Başarılı!\n\nSenin sabit hesabın artık @{kaynak_hesap} gibi görünüyor.\n\n👤 İsim: {isim}\n📝 Bio: {bio}\n\n✨ Yeni bir hesap kopyalamak istersen, sadece kullanıcı adını yazıp göndermen yeterli!")
    except Exception as e:
        bot.reply_to(message, f"❌ Bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    if instagram_giris():
        print("🤖 Telegram Botu aktif...")
        bot.infinity_polling()

