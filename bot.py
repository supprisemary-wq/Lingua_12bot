import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deep-translator import GoogleTranslator

# Retrieve token from Render Environment Settings
TOKEN = os.getenv("TOKEN", "YOUR_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome instruction message."""
    welcome_text = (
        "🌐 **Welcome to TranslateBot!** 🌐\n\n"
        "I am an always-on background translator. I will automatically detect your input language and translate it into English!\n\n"
        "👉 **How to use:** Just send or forward me *any* foreign text, and I will translate it instantly.\n\n"
        "✨ _To translate to a specific language instead, use:_ `/to lang code text` \n"
        "_(Example: `/to es Hello friend` converts it to Spanish)_"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def translate_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatically detect text language and translate it to English."""
    user_text = update.message.text

    # Skip processing if it's an empty message or a command
    if not user_text or user_text.startswith('/'):
        return

    status_message = await update.message.reply_text("🔄 Detecting and translating...")

    try:
        # Use deep-translator to auto-detect source language and output English
        translated = GoogleTranslator(source='auto', target='en').translate(user_text)
        
        response_text = (
            "🎯 **TRANSLATION (EN)** 🎯\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{translated}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✨ _Language auto-detected_"
        )
        await status_message.edit_text(response_text, parse_mode="Markdown")

    except Exception as e:
        print(f"Translation Error: {str(e)}")
        await status_message.edit_text("❌ Sorry, I couldn't translate that text. Please try again.")

async def translate_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate text to a custom language specified by the user using /to [lang] [text]"""
    # Check if there are enough arguments inside the command
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ **Format incorrect!**\nUse: `/to [language_code] [your text]`\n"
            "Example: `/to fr Good morning` (Translates to French)",
            parse_mode="Markdown"
        )
        return

    target_lang = context.args[0].lower() # e.g. 'es', 'fr', 'ar', 'zh-cn'
    text_to_translate = " ".join(context.args[1:])

    status_message = await update.message.reply_text(f"🔄 Translating to '{target_lang.upper()}'...")

    try:
        # Translate to the user's specific chosen language code
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text_to_translate)
        
        response_text = (
            f"🎯 **TRANSLATION ({target_lang.upper()})** 🎯\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{translated}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await status_message.edit_text(response_text, parse_mode="Markdown")

    except Exception as e:
        print(f"Custom Translation Error: {str(e)}")
        await status_message.edit_text(
            f"❌ Failed to translate. Make sure you used a valid 2-letter language code "
            f"(like `es` for Spanish, `fr` for French, `ar` for Arabic)."
        )

def main():
    """Start the bot engine loop."""
    application = Application.builder().token(TOKEN).build()

    # Register Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("to", translate_custom))
    # This handler catches all normal incoming text messages and sends them to the auto-translator
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_auto))

    # Run polling loop
    print("✅ TranslateBot is running actively as a Background Worker...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
