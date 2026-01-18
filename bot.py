import random
import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- Flask Server Setup (Render Free Plan အတွက်) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_web_server():
    # Render ပေးတဲ့ Port ကို သုံးဖို့ဖြစ်ပါတယ်။
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Settings ---
API_TOKEN = '8584313182:AAEzQDI1Ir5zruVNrs5sS41vL4ZwoeGp_cc'
bot = telebot.TeleBot(API_TOKEN)

# --- CC Generation Logic ---
def luhn_checksum(card_number):
    digits = [int(x) for x in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum([int(x) for x in str(d * 2)])
    return checksum % 10 == 0

def generate_cc(bin_number):
    cc = str(bin_number)
    if cc.startswith(('34', '37')):
        target_len = 15
    elif cc.startswith(('300', '301', '302', '303', '304', '305', '36', '38')):
        target_len = 14
    else:
        target_len = 16

    while len(cc) < (target_len - 1):
        cc += str(random.randint(0, 9))

    for i in range(10):
        if luhn_checksum(cc + str(i)):
            return cc + str(i)
    return cc + "0"

def get_cc_list(bin_num, user_tag, month=None, year=None, amount=10):
        amount = int(args[4]) if len(args) >= 5 and args[4].isdigit() else 10

        if amount > 50:
            amount = 50 

        user_tag = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
        final_res = get_cc_list(bin_num, user_tag, month, year, amount)
        bot.send_message(message.chat.id, final_res, parse_mode="HTML", reply_markup=gen_markup(bin_num, month, year, amount))
    except Exception as e:
        bot.reply_to(message, f"⚠️ <b>System Error:</b> <code>{str(e)}</code>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "delete_msg":
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data.startswith("regen_"):
        try:
            d = call.data.split("_")
            b_val = d[1]
            m_val = int(d[2]) if d[2] != "R" else None
            y_val = int(d[3]) if d[3] != "R" else None
            a_val = int(d[4])
            user_tag = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
            new_res = get_cc_list(b_val, user_tag, m_val, y_val, a_val)
            bot.edit_message_text(new_res, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=gen_markup(b_val, m_val, y_val, a_val))
        except Exception as e:
            bot.answer_callback_query(call.id, f"Error: {str(e)}")

if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" SYSTEM STATUS: ONLINE ✅")
    print(" BOT NAME: CC GEN PRO")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    bot.infinity_polling()
