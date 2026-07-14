import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = "YOUR_CHANNEL_ID"
ADMIN_ID = 123456789

count = 0
pending = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም 👋\n"
        "ሚስጥራዊ መልዕክትህን ላክ።"
    )

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global count

    user_message = update.message.text
    user_id = update.message.from_user.id

    pending[user_id] = user_message

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"አዲስ መልዕክት:\n\n{user_message}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
        "መልዕክትህ ተቀብሏል። ማረጋገጫ እየጠበቀ ነው።"
    )async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global count

    query = update.callback_query
    await query.answer()

    data = query.data

    action, user_id = data.split("_")
    user_id = int(user_id)

    if action == "approve":
        count += 1

        message = pending.get(user_id)

        if message:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"#{count}\n\n{message}"
            )

            del pending[user_id]

            await query.edit_message_text(
                "✅ Approved እና ወደ Channel ተለጠፈ።"
            )

    elif action == "reject":
        if user_id in pending:
            del pending[user_id]

        await query.edit_message_text(
            "❌ Rejected። አልተለጠፈም።"
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message)
    )
    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_error_handler(error_handler)

    print("SMU Confession Bot Started")

    app.run_polling()


if __name__ == "__main__":
    main()
