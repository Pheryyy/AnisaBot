import json
import requests
from flask import Flask, request
import telegram

# Load information from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

TOKEN = config["telegram_bot_token"]
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    handle_update(update)  # Function to handle incoming messages
    return 'ok'

def handle_update(update):
    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text
        bot.sendMessage(chat_id=chat_id, text=f"Your message: {message}")

if __name__ == '__main__':
    app.run(port=5000)
