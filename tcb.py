from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
load_dotenv() 
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'cache-control': 'max-age=0',
    'pragma': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
}

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def get_most_recent_chapter():
    response = requests.get('https://tcbonepiecechapters.com/mangas/5/one-piece', headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    chapter = soup.select_one('a.block.border.border-border.bg-card.mb-3.p-3.rounded')
    if not chapter:
        raise ValueError("Could not find the most recent chapter element")
    return chapter

def send_discord_notification(chapter):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title_div = chapter.find('div', class_='text-lg font-bold')
    subtitle_div = chapter.find('div', class_='text-gray-500')

    title = title_div.text.strip() if title_div else chapter.text.strip()
    description = subtitle_div.text.strip() if subtitle_div else ""
    href = chapter.get('href', '')
    if href and not href.startswith('http'):
        href = 'https://tcbonepiecechapters.com' + href

    embed = {
        "title": f"\n{title}",
        "description": f"||{description}||\n" + f"\n{now}",
        "url": href,
        "color": 1833499
    }

    payload = {
        "embeds": [embed]
    }

    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def is_posting_day():
    # Thursday (3) to Sunday (6)
    return datetime.now().weekday() in {3, 4, 5, 6}

def send_error_notification(message):
    data = {
        "content": f"Error: {message}"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=data)

def print_timestamped(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")

while True:
    if not DISCORD_WEBHOOK_URL:
        break
    if is_posting_day():
        try:
            recent_chapter = get_most_recent_chapter()
            print_timestamped(f"checked recent {recent_chapter.text.strip()}")
            print_timestamped("waiting 60 seconds to recheck...")
            time.sleep(60)
            print_timestamped("rechecking...")
            new_chapter = get_most_recent_chapter()
            print_timestamped(f"rechecked recent {new_chapter.text.strip()}")
            if recent_chapter != new_chapter:
                send_discord_notification(new_chapter)
        except Exception as e:
            send_error_notification(str(e))
            time.sleep(15 * 60)
    else:
        print("not a posting day. sleeping for 6 hours.")
        time.sleep(6 * 60 * 60) 

