import os
import logging
from io import BytesIO, StringIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from typing import Optional
from main import plot_current_db_statistics, update_database
import matplotlib.pyplot as plt
from Constants import DEFAULT_CSV_DELIMITER, GROUPED_CATEGORIES_CSV_PATH
from ReportParsers import Bank

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! Send a UTF-8 text file (.txt or .csv). I'll print its content to my console."
    )


def _is_supported_text_file(file_name: str, mime: Optional[str]) -> bool:
    name_ok = file_name.lower().endswith((".txt", ".csv"))
    mime_ok = bool(mime) and mime.startswith("text/")
    return name_ok and mime_ok


async def report_current_db_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    img_buf = BytesIO()
    fig = plot_current_db_statistics(GROUPED_CATEGORIES_CSV_PATH, DEFAULT_CSV_DELIMITER)
    fig.savefig(img_buf, format="png")
    plt.close(fig)
    img_buf.seek(0)
    
    await context.bot.send_photo(
    chat_id=update.effective_chat.id,
    photo=img_buf)
    
def _bank_keyboard() -> InlineKeyboardMarkup:
    prefix = lambda x: "bank:" + x
    buttons = [
        [
            InlineKeyboardButton(text="ABN AMRO", callback_data=prefix(Bank.ABN_AMRO.value)),
            InlineKeyboardButton(text="ING", callback_data=prefix(Bank.ING.value)),
            InlineKeyboardButton(text="Revolut", callback_data=prefix(Bank.REVOLUT.value)),
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.document:
        return

    doc = update.message.document

    if not _is_supported_text_file(doc.file_name or "", doc.mime_type):
        await update.message.reply_text(
            "Unsupported file. Please send a UTF-8 text file with extension .txt or .csv."
        )
        return

    tg_file = await doc.get_file()
    raw_bytes = await tg_file.download_as_bytearray()
    try:
        report = StringIO(raw_bytes.decode("utf-8", errors="strict"))
    except UnicodeDecodeError:
        await update.message.reply_text("Encoding error. Please send the file encoded as UTF-8.")
        return

    context.user_data["pending_report"] = report
    await update.message.reply_text("Which bank is this statement from?", reply_markup=_bank_keyboard())
    
    
async def on_bank_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data or not query.data.startswith("bank:"):
        return

    await query.answer()  # acknowledge button press

    bank_name = query.data.split(":", 1)[1]
    try:
        bank = Bank(bank_name)
    except KeyError:
        await query.message.reply_text("Unknown bank choice. Please resend the file.")
        context.user_data.pop("pending_report", None)
        return

    logger.info(f"Selected bank {bank}")

    report = context.user_data.pop("pending_report", None)
    if report is None:
        await query.message.reply_text("No pending file found. Please resend the document.")
        return
    
    sender = str(update.effective_user.first_name)

    logger.info(f"Sender: {sender}")
    
    update_database(GROUPED_CATEGORIES_CSV_PATH, DEFAULT_CSV_DELIMITER, report, bank, sender)
    await report_current_db_statistics(update, context)
       
    
    
    
def main() -> None:
    token = os.environ.get("EXPENSE_TRACKER_TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing EXPENSE_TRACKER_TELEGRAM_BOT_TOKEN in environment.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(on_bank_chosen, pattern=r"^bank:"))

    logger.info("Bot starting with polling...")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
