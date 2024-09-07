import json
import telegram
from flask import Flask, request
import requests  # For Hetzner API requests

# Load the config file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

TOKEN = config["telegram_bot_token"]
ADMIN_USER_ID = config["admin_user_id"]
HETZNER_API_TOKEN = config["hetzner_token"]  # Load Hetzner API token

bot = telegram.Bot(token=TOKEN)

# Initialize the Flask app
app = Flask(__name__)

# A simple in-memory store for users
active_users = set()

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    handle_update(update)
    return 'ok'

def handle_update(update):
    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text

        # Add the user to active users
        active_users.add(chat_id)

        # Check if the message is from the admin
        if str(chat_id) == ADMIN_USER_ID:
            handle_admin_commands(update)
        else:
            # Normal user interaction
            bot.sendMessage(chat_id=chat_id, text=f"Your message: {message}")
            
            # Notify the admin of the user's message
            bot.sendMessage(chat_id=ADMIN_USER_ID, text=f"User {chat_id} sent: {message}")

def handle_admin_commands(update):
    """Handles commands sent by the admin"""
    chat_id = update.message.chat.id
    message = update.message.text

    if message == '/status':
        bot.sendMessage(chat_id=chat_id, text="Bot is running smoothly.")
    elif message == '/stop':
        bot.sendMessage(chat_id=chat_id, text="Stopping the bot...")
        # Add logic to stop the bot safely
    elif message == '/start':
        bot.sendMessage(chat_id=chat_id, text="Bot has started.")
        # Add logic to start services if needed
    elif message == '/users':
        # نمایش تعداد کاربران فعال
        bot.sendMessage(chat_id=chat_id, text=f"Active users: {len(active_users)}")
    elif message.startswith('/remove'):
        # حذف کاربر
        user_id = message.split()[1]
        if int(user_id) in active_users:
            active_users.remove(int(user_id))
            bot.sendMessage(chat_id=chat_id, text=f"User {user_id} removed from active users.")
        else:
            bot.sendMessage(chat_id=chat_id, text=f"User {user_id} not found.")
    elif message == '/messages':
        # مشاهده پیام‌های ورودی کاربران
        bot.sendMessage(chat_id=chat_id, text="Forwarding recent messages from users.")
        # Forward the recent messages to admin (example: last 5 messages)
        # This can be expanded based on how you store messages in your system
    elif message.startswith('/server'):
        # مدیریت سرورها (با استفاده از Hetzner API)
        handle_hetzner_commands(chat_id, message)
    else:
        bot.sendMessage(chat_id=chat_id, text=f"Admin command not recognized: {message}")

def handle_hetzner_commands(chat_id, message):
    """Handles server management commands for Hetzner"""
    if message == '/server list':
        # List all servers from Hetzner API
        url = "https://api.hetzner.cloud/v1/servers"
        headers = {"Authorization": f"Bearer {HETZNER_API_TOKEN}"}
        response = requests.get(url, headers=headers)
        servers = response.json().get('servers', [])
        if servers:
            for server in servers:
                server_info = f"Server ID: {server['id']}, Name: {server['name']}, Status: {server['status']}"
                bot.sendMessage(chat_id=chat_id, text=server_info)
        else:
            bot.sendMessage(chat_id=chat_id, text="No servers found.")
    elif message.startswith('/server delete'):
        # Delete a server by ID
        server_id = message.split()[2]
        url = f"https://api.hetzner.cloud/v1/servers/{server_id}"
        headers = {"Authorization": f"Bearer {HETZNER_API_TOKEN}"}
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            bot.sendMessage(chat_id=chat_id, text=f"Server {server_id} deleted successfully.")
        else:
            bot.sendMessage(chat_id=chat_id, text=f"Failed to delete server {server_id}.")
    else:
        bot.sendMessage(chat_id=chat_id, text="Unknown server command.")

if __name__ == '__main__':
    app.run(port=5000)
