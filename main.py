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

# --- AYARLAR ---
TELEGRAM_BOT_TOKEN = "BURAYA_TELEGRAM_BOT_TOKENINI_YAZ"
MY_INSTAGRAM_USER = "gercek_instagram_kullanici_adin"
MY_INSTAGRAM_PASS = "gercek_instagram_sifren"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
cl = Client()

def instagram_giris():
    print("🔐 Instagram'a giriş yapılıyor...")
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
    bot.reply_to(message, "👋 Bot hazır! Giydirmek istediğin hedef Instagram kullanıcı adını yazıp gönder.")

@bot.message_handler(func=lambda message: True)
def profil_giydir(message):
    hedef_hesap = message.text.strip().replace("@", "")
    bot.reply_to(message, f"⏳ @{hedef_hesap} profili kopyalanıyor... Lütfen bekleyin.")

    try:
        hedef_info = cl.user_info_by_username(hedef_hesap)
        bio = hedef_info.biography if hedef_info.biography else ""
        isim = hedef_info.full_name if hedef_info.full_name else hedef_hesap
        resim_url = hedef_info.profile_pic_url

        resim_datasi = requests.get(resim_url).content
        with open("hedef_profil.jpg", "wb") as f:
            f.write(resim_datasi)

        cl.account_edit(full_name=isim, biography=bio)
        cl.account_change_picture("hedef_profil.jpg")

        if os.path.exists("hedef_profil.jpg"):
            os.remove("hedef_profil.jpg")

        bot.reply_to(message, f"🎉 Giydirme Başarılı!\n\n👤 İsim: {isim}\n📝 Bio: {bio}")
    except Exception as e:
        bot.reply_to(message, f"❌ Bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    if instagram_giris():
        print("🤖 Telegram Botu aktif...")
        bot.infinity_polling()
