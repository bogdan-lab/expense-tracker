import os
import logging
from io import BytesIO

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from typing import Optional

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
    buffer = BytesIO()
    await tg_file.download_to_memory(out=buffer)
    buffer.seek(0)
    raw = buffer.read()

    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        await update.message.reply_text(
            "Encoding error. Please send the file encoded as UTF-8."
        )
        return

    logger.info(
        "---- Received file ----\n"
        f"From: @{update.effective_user.username or update.effective_user.id}\n"
        f"Name: {doc.file_name}\n"
        f"MIME: {doc.mime_type}\n"
        f"Size: {doc.file_size} bytes\n"
        "----- File content start -----\n"
        f"{text}\n"
        "----- File content end -------"
    )

    await update.message.reply_text(
        f"Got it: {doc.file_name} ({doc.file_size} bytes). Printed to console ✅"
    )


def main() -> None:
    token = os.environ.get("EXPENSE_TRACKER_TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing EXPENSE_TRACKER_TELEGRAM_BOT_TOKEN in environment.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("Bot starting with polling...")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
