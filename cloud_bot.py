import os
import time
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ==============================================================================
# CHANGE YOUR DETAILS HERE (REMOVE THE EXAMPLE VALUES AND PUT YOUR OWN)
# ==============================================================================
STUDENT_NAME = "Labib 711268"  # PUT YOUR INDEX NUMBER & NAME HERE

SCHEDULES = [
    {
        "topic": "Morning Class",
        "days": "sat,mon,wed",
        "time": "07:30",
        "meeting_id": "7506012370",       # PUT YOUR MORNING MEETING ID HERE
        "passcode": "nova",         # PUT YOUR MORNING PASSCODE HERE
        "duration_minutes": 60             # STAY TIME (60 MINS)
    },
    {
        "topic": "Evening Class",
        "days": "sun,tue,thu",
        "time": "19:30",
        "meeting_id": "7506012370",       # PUT YOUR EVENING MEETING ID HERE
        "passcode": "nova",         # PUT YOUR EVENING PASSCODE HERE
        "duration_minutes": 60             # STAY TIME (60 MINS)
    }
]
# ==============================================================================

async def join_zoom_meeting(meeting_id, passcode, student_name, duration_min, topic):
    print(f"\n[{datetime.now()}] Joining: {topic}")
    clean_id = str(meeting_id).replace(" ", "").replace("-", "")
    zoom_web_url = f"https://zoom.us/wc/{clean_id}/join?pwd={passcode}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--use-fake-ui-for-media-stream", "--no-sandbox"]
        )
        context = await browser.new_context(permissions=["microphone", "camera"])
        page = await context.new_page()

        try:
            await page.goto(zoom_web_url, wait_until="networkidle", timeout=60000)
            name_input = page.locator("input[id='input-for-name']")
            await name_input.wait_for(state="visible", timeout=30000)
            await name_input.fill(student_name)
            
            join_button = page.locator("button.preview-join-button")
            await join_button.click()
            print(f"Joined as '{student_name}'!")
            
            await asyncio.sleep(duration_min * 60)
            print(f"Time finished. Leaving: {topic}")

        except Exception as e:
            print(f"Error joining meeting: {str(e)}")
        finally:
            await browser.close()

def start_scheduler():
    scheduler = AsyncIOScheduler()
    for s in SCHEDULES:
        hour, minute = s["time"].split(":")
        scheduler.add_job(
            join_zoom_meeting,
            trigger="cron",
            day_of_week=s["days"],
            hour=int(hour),
            minute=int(minute),
            args=[s["meeting_id"], s["passcode"], STUDENT_NAME, s["duration_minutes"], s["topic"]]
        )
        print(f"Scheduled: {s['topic']} ({s['days']}) at {s['time']}")
    scheduler.start()

if __name__ == "__main__":
    print("Bot is starting...")
    start_scheduler()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
