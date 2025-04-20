from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = "7745514605:AAHfKFT4PlGVXhi0aMpnMmIQUVRcvpymeeE"
ADMIN_IDS = 2025904026

# Состояния для FSM
class States:
    WAITING_FOR_TEXT = "waiting_for_text"
    WAITING_FOR_PHOTO = "waiting_for_photo"
    MODERATION = "moderation" 
