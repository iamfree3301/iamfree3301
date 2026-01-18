import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Settings ---
# သတိပေးချက်- Token ကို လုံခြုံအောင် သိမ်းဆည်းပါ။
API_TOKEN = '8584313182:AAEzQDI1Ir5zruVNrs5sS41vL4ZwoeGp_cc'
bot = telebot.TeleBot(API_TOKEN)

# --- CC Generation Logic ---
def luhn_checksum(card_number):
    """Luhn Algorithm သုံးပြီး card number မှန်မမှန် စစ်ဆေးခြင်း"""
    digits = [int(x) for x in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum([int(x) for x in str(d * 2)])
    return checksum % 10 == 0

def generate_cc(bin_number):
    """BIN ပေါ်မူတည်ပြီး Card Length သတ်မှတ်ကာ Card နံပါတ် ထုတ်ပေးခြင်း"""
    cc = str(bin_number)
    # Card length logic
    if cc.startswith(('34', '37')):
        target_len = 15 # AMEX
    elif cc.startswith(('300', '301', '302', '303', '304', '305', '36', '38')):
        target_len = 14 # Diners Club
    else:
        target_len = 16 # Visa, Master, Discover

    while len(cc) < (target_len - 1):
        cc += str(random.randint(0, 9))

    # Luhn digit ကို နောက်ဆုံးမှာ ပေါင်းထည့်ခြင်း
    for i in range(10):
        if luhn_checksum(cc + str(i)):
            return cc + str(i)
    return cc + "0"

def get_cc_list(bin_num, user_tag, month=None, year=None, amount=10):
    is_amex = bin_num.startswith(('34', '37'))
    cvv_range = (1000, 9999) if is_amex else (100, 999)
    result = "<b>CARDS GENERATED SUCCESSFULLY</b> ✅\n"
    result += f"<b>BIN</b> ⇾ <code>{bin_num}</code>\n"
    result += f"<b>AMOUNT</b> ⇾ <code>{amount}</code>\n\n"
    for _ in range(amount):
        cc_num = generate_cc(bin_num)
        final_m = month if month else random.randint(1, 12)
        final_y = year if year else random.randint(2026, 2033)
        cvv = random.randint(*cvv_range)
        result += f"<code>{cc_num}|{final_m:02d}|{final_y}|{cvv}</code>\n"
    return result

def gen_markup(b, m, y, a):
    m_val = m if m else "R"
    y_val = y if y else "R"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔄 Regenerate", callback_data=f"regen_{b}_{m_val}_{y_val}_{a}"),
        InlineKeyboardButton("❌ Close", callback_data="delete_msg")
    )
    return markup

# --- Bot Handlers ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "<b>Bot: Online ✅</b>\n\n"
        f"👋 <b>Hello {message.from_user.first_name}!</b>\n\n"
        "📖 <b>Usage Guide:</b>\n"
        "➥ <code>/gen BIN</code>\n"
        "➥ <code>/gen BIN MM YYYY Amount</code>\n\n"
        "💡 <b>Example:</b> <code>/gen 559888 12 2028 10</code>"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.message_handler(commands=['gen'])
def handle_gen(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ <b>Usage:</b> <code>/gen BIN</code>", parse_mode="HTML")
            return
        
        bin_num = args[1]
        if not bin_num.isdigit():
            bot.reply_to(message, "⚠️ <b>Error:</b> BIN must be numeric!", parse_mode="HTML")
            return

        month = int(args[2]) if len(args) >= 3 and args[2].isdigit() else None
        year = int(args[3]) if len(args) >= 4 and args[3].isdigit() else None
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
