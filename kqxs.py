import telebot
import requests
import random
import os
from flask import Flask
from threading import Thread

# --- Telegram Bot Setup ---
TOKEN = "7688401027:AAHiC-Zhbtk0ckVi7goLXtBWO2_Qv-DDCf4"  # Dùng token từ kqxs.py
bot = telebot.TeleBot(TOKEN)

session = requests.Session()  # Dùng cho /gaitt
API_TT = "https://gaitiktok.onrender.com/random?apikey=randomtnt"

# --- /kqxs command ---
@bot.message_handler(commands=['kqxs'])
def sxmb(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f"Không thể xoá lệnh: {e}")

    api_url = 'https://nguyenmanh.name.vn/api/xsmb?apikey=OUEaxPOl'
    try:
        response = requests.get(api_url)
        data = response.json()
        if data.get('status') == 200:
            bot.send_message(message.chat.id, f"<b>{data['result']}</b>", parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'Lỗi khi lấy kết quả xổ số.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Đã xảy ra lỗi: {e}')

# --- /quaythu command ---
@bot.message_handler(commands=['quaythu'])
def quaythu(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    def rand_number(length):
        return ''.join(random.choices('0123456789', k=length))

    result = f"""<b>KẾT QUẢ QUAY THỬ XỔ SỐ MIỀN BẮC</b>
ĐB: {rand_number(5)}
1: {rand_number(5)}
2: {rand_number(5)} - {rand_number(5)}
3: {rand_number(5)} - {rand_number(5)} - {rand_number(5)} - {rand_number(5)} - {rand_number(5)} - {rand_number(5)}
4: {rand_number(4)} - {rand_number(4)} - {rand_number(4)} - {rand_number(4)}
5: {rand_number(4)} - {rand_number(4)} - {rand_number(4)} - {rand_number(4)} - {rand_number(4)} - {rand_number(4)}
6: {rand_number(3)} - {rand_number(3)} - {rand_number(3)}
7: {rand_number(2)} - {rand_number(2)} - {rand_number(2)} - {rand_number(2)}"""

    bot.send_message(message.chat.id, result, parse_mode='HTML')

# --- /gaitt command ---
def get_flag(region):
    """Chuyển mã quốc gia thành biểu tượng cờ (Unicode)"""
    if not region:
        return "🌍"
    return "".join(chr(127397 + ord(c)) for c in region.upper())

def download_video(url, path='tkvd.mp4', timeout=10, max_retries=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(max_retries):
        try:
            response = session.get(url, stream=True, timeout=timeout, headers=headers)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(4096):
                        f.write(chunk)
                return path
        except requests.RequestException as e:
            print(f"Lỗi tải video (lần {attempt + 1}): {e}")
    return None

@bot.message_handler(commands=['gaitt'])
def handle_gaitt(message):
    waiting = bot.reply_to(message, "🔎 Đang lấy dữ liệu...")

    try:
        response = session.get(API_TT, timeout=5)
        if response.status_code != 200:
            raise Exception("⚠️ API không phản hồi!")

        data = response.json().get("data")
        if not data:
            raise Exception("⚠️ API không trả về dữ liệu!")

        video_url = data.get("play")
        if not video_url or not video_url.startswith("http"):
            raise Exception("⚠️ Không tìm thấy video hợp lệ!")

        video_path = download_video(video_url)
        if not video_path:
            raise Exception("⚠️ Không thể tải video!")

        author = data.get('author', {})
        region = data.get('region', 'N/A')
        flag = get_flag(region)

        caption = f"""
🎬 <b>{data.get('title', 'Không có tiêu đề')}</b>
━━━━━━━━━━━━━━━━━━
👤 <b>Tác giả:</b> {author.get('nickname', 'N/A')}  
🆔 <b>UID:</b> <code>{author.get('id', 'N/A')}</code>  
🔗 <b>Username:</b> @{author.get('unique_id', 'N/A')}  
📍 <b>Quốc gia:</b> {flag} {region}  
━━━━━━━━━━━━━━━━━━
❤️ <b>Thích:</b> {data.get('digg_count', 0)}  
💬 <b>Bình luận:</b> {data.get('comment_count', 0)}  
👀 <b>Lượt xem:</b> {data.get('play_count', 0)}  
🔄 <b>Chia sẻ:</b> {data.get('share_count', 0)}  
⬇️ <b>Tải xuống:</b> {data.get('download_count', 0)}  
⏱ <b>Thời lượng:</b> {data.get('duration', 0)} giây  
📸 <b>Ảnh đại diện:</b> <a href="{author.get('avatar', '#')}">Xem ngay</a>  
━━━━━━━━━━━━━━━━━━"""

        bot.delete_message(message.chat.id, waiting.message_id)
        bot.send_chat_action(message.chat.id, 'upload_video')

        with open(video_path, 'rb') as video:
            bot.send_video(
                message.chat.id, video=video, caption=caption,
                reply_to_message_id=message.message_id,
                supports_streaming=True, parse_mode='HTML'
            )
            bot.delete_message(message.chat.id, message.message_id)

    except Exception as e:
        bot.edit_message_text(str(e), message.chat.id, waiting.message_id)
    finally:
        if os.path.exists("tkvd.mp4"):
            os.remove("tkvd.mp4")

# --- Flask server để giữ bot luôn chạy ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# --- Start bot and server ---
def start():
    Thread(target=run_flask).start()
    bot.polling()

start()
