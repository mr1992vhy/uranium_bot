import requests
import schedule
import time
from datetime import datetime

# خواندن همه توکن‌ها از فایل tokens.txt
def load_tokens():
    try:
        with open('tokens.txt', 'r') as file:
            tokens = [line.strip() for line in file if line.strip()]
            if not tokens:
                raise ValueError("No tokens found in tokens.txt")
            return tokens
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error loading tokens: {e}")
        return []

# هدرهای درخواست برای هر توکن
def get_headers(token):
    return {
        "Cookie": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.geturanium.io/refinery",  # ممکنه نیاز به تنظیم داشته باشه
        "Origin": "https://www.geturanium.io",          # ممکنه نیاز به تنظیم داشته باشه
        # هدرهای دیگه اگه نیازه اضافه کن
    }

# URL درخواست Refine (باید با DevTools پیدا کنی)
REFINE_URL = "https://www.geturanium.io/api/refinery/refine"  # این URL رو باید خودت پیدا کنی

# تابع برای فرمت کردن زمان به ساعت:دقیقه:ثانیه
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# تابع برای Refine هر اکانت
def refine_for_account(token):
    headers = get_headers(token)
    token_display = token[:10] + "..."  # برای نمایش کوتاه‌تر توکن تو لاگ
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Attempting to refine for account with token: {token_display}")
    try:
        # ارسال درخواست POST برای Refine
        response = requests.post(REFINE_URL, headers=headers)
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Refine successfully executed for account with token: {token_display}")
            print(f"Response: {response.json()}")
        elif response.status_code in [401, 403]:  # تشخیص انقضای توکن
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WARNING: Token expired for account with token: {token_display}")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to refine for account with token: {token_display}. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error for account with token {token_display}: {e}")

# تابع اصلی برای پردازش همه اکانت‌ها
def refine_all_accounts():
    tokens = load_tokens()
    if not tokens:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No accounts to process.")
        return

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing {len(tokens)} accounts...")
    for token in tokens:
        refine_for_account(token)

# تابع برای نمایش تایمر شمارش معکوس
def countdown_timer(seconds):
    while seconds > 0:
        formatted_time = format_time(seconds)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Next refine in: {formatted_time}", end="\r")
        time.sleep(1)
        seconds -= 1

# زمان‌بندی برای اجرا هر 8 ساعت
schedule.every(8).hours.do(refine_all_accounts)

# اجرای اولیه برای تست
refine_all_accounts()

# حلقه برای اجرای مداوم با تایمر
while True:
    schedule.run_pending()
    # تایمر شمارش معکوس تا اجرای بعدی (8 ساعت = 28800 ثانیه)
    countdown_timer(8 * 60 * 60)
