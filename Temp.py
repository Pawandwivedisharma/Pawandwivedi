import requests
import random
import string
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8720127398:AAGUlNh7CYKMZr59cz1MWa3h5TjUssh9snA"

API_BASE = "https://api.mail.tm"

user_data = {}

# Generate random username
def random_string():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

# Create account
def create_email():
    domains = requests.get(f"{API_BASE}/domains").json()["hydra:member"]
    domain = domains[0]["domain"]

    username = random_string()
    email = f"{username}@{domain}"
    password = "12345678"

    # Create account
    requests.post(f"{API_BASE}/accounts", json={
        "address": email,
        "password": password
    })

    # Get token
    token = requests.post(f"{API_BASE}/token", json={
        "address": email,
        "password": password
    }).json()["token"]

    return email, password, token

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Use /newmail to get temp email")

# /newmail
async def newmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email, password, token = create_email()
    user_data[update.effective_user.id] = token

    await update.message.reply_text(
        f"📧 Email: {email}\n🔑 Password: {password}"
    )

# /inbox
async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_data:
        await update.message.reply_text("⚠️ First use /newmail")
        return

    token = user_data[user_id]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    res = requests.get(f"{API_BASE}/messages", headers=headers).json()

    if "hydra:member" not in res or len(res["hydra:member"]) == 0:
        await update.message.reply_text("📭 Inbox empty")
        return

    text = "📬 Inbox:\n"
    for msg in res["hydra:member"]:
        text += f"\nFrom: {msg['from']['address']}\nSubject: {msg['subject']}\n"

    await update.message.reply_text(text)

# Run bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newmail", newmail))
    app.add_handler(CommandHandler("inbox", inbox))

    print("Bot Running...")
    app.run_polling()

if name == "main":
    main()
