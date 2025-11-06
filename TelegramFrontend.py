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
from typing import Optional, Dict
from main import plot_current_db_statistics, update_database
from GroupedTransactions import load_grouped_transactions_from_dbase
import matplotlib.pyplot as plt
from Constants import DEFAULT_CSV_DELIMITER, GROUPED_CATEGORIES_CSV_PATH
from ReportParsers import Bank
from datetime import date

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


ALLOWED_USERNAMES = set(
    u.strip().lower() for u in os.getenv("EXPENSE_TRACKER_ALLOWED_USERS", "").split(",") if u.strip()
)


def guarded(func):
    
    async def check_allowed(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        logger.info(f"Responding to user: {user}")
        if not user.id in ALLOWED_USERNAMES:
            msg = "Sorry, you are not authorized to use this bot."
            await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
            return
        return await func(update, context)
    
    return check_allowed


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        """Hi! Send a transaction report from your bank account (.txt or .csv) and I will update DB with it.
        You can use:
        - /last to see the date of your last submitted transaction
        - /show to see stats from transactions in database
        """
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
       

async def last_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    sender = (user.first_name or "").lower()

    grouped = load_grouped_transactions_from_dbase(GROUPED_CATEGORIES_CSV_PATH, DEFAULT_CSV_DELIMITER)

    latest_by_bank: Dict[Bank, date] = {}
    for cat in grouped.get_categories():
        for tx in cat.get_transactions():
            if tx.sender == sender:
                b = tx.sender_bank
                if b not in latest_by_bank or tx.date > latest_by_bank[b]:
                    latest_by_bank[b] = tx.date

    if not latest_by_bank:
        await update.message.reply_text("No transactions found for your account.")
        return

    name_w = max(len(b.value) for b in Bank)
    date_w = max(len("YYYY-MM-DD"), *(len(d.isoformat()) for d in latest_by_bank.values() if d))
    lines = [
        f"{b.value:<{name_w}} : {latest_by_bank[b].isoformat():>{date_w}}"
        for b in sorted(latest_by_bank)
    ]
    await update.message.reply_text("\n".join(lines))   
    
    
def main() -> None:
    token = os.environ.get("EXPENSE_TRACKER_TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing EXPENSE_TRACKER_TELEGRAM_BOT_TOKEN in environment.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", guarded(start)))
    app.add_handler(CommandHandler("show", guarded(report_current_db_statistics)))
    app.add_handler(CommandHandler("last", guarded(last_date)))
    app.add_handler(MessageHandler(filters.Document.ALL, guarded(handle_document)))
    app.add_handler(CallbackQueryHandler(guarded(on_bank_chosen), pattern=r"^bank:"))

    logger.info("Bot starting with polling...")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
