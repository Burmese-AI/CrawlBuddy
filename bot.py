import os
import re
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    filters,
)
from Scraper import scrape, toJson
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("APITOKEN")


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Hello! Send me a full wbesite link and I will scrape the headlines and links."
    )


async def check_link(update: Update, context: CallbackContext):
    message_text = update.message.text

    # Define a simple regex pattern for URLs
    url_pattern = re.compile(r"(http|https)://[^\s/$.?#].[^\s]*")

    # Check if the message text matches the URL pattern
    if url_pattern.match(message_text):
        await update.message.reply_text(
            "Please wait a few minutes as we process the file for you..."
        )
        file_path = "data.json"

        # Write JSON data to file
        with open(file_path, "w") as file:
            file.write(toJson(scrape(message_text)))

        # Open the file in binary mode to send it
        with open(file_path, "rb") as file:
            await update.message.reply_document(document=InputFile(file, "data.json"))
        # Clean up the file
        os.remove(file_path)
    else:
        await update.message.reply_text(
            "Please send a full link. (https://www.example.com)"
        )


def main():
    application = Application.builder().token(API_TOKEN).build()

    # Register handlers for commands and messages
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_link))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
