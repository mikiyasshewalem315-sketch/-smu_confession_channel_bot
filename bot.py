)
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

confession_number = 1
pending_messages = {}


@bot.message_handler(func=lambda message: message.chat.type == "private")
def receive_confession(message):
    if message.from_user.id == ADMIN_ID:
        return

    pending_messages[message.message_id] = message.text

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            "✅ Approve",
            callback_data=f"approve:{message.message_id}"
        ),
        InlineKeyboardButton(
            "❌ Reject",
            callback_data=f"reject:{message.message_id}"
        )
    )

    bot.send_message(
        ADMIN_ID,
        f"New confession:\n\n{message.text}",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global confession_number

    action, message_id = call.data.split(":")
    message_id = int(message_id)

    if message_id not in pending_messages:
        bot.answer_callback_query(call.id, "Message not found.")
        return

    if action == "approve":
        text = f"#{confession_number}\n\n{pending_messages[message_id]}"
        bot.send_message(CHANNEL_ID, text)
        confession_number += 1

        bot.edit_message_text(
            "✅ Approved",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

    else:
        bot.edit_message_text(
            "❌ Rejected",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

    del pending_messages[message_id]
    bot.answer_callback_query(call.id)


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
