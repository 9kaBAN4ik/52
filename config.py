from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

# Состояния для FSM
class States:
    WAITING_FOR_TEXT = "waiting_for_text"
    WAITING_FOR_PHOTO = "waiting_for_photo"
    MODERATION = "moderation" 