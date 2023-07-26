import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from eng_replies import eng_keyboard
from ru_replies import ru_keyboard
from videos_collector import get_random_podcast_link

LANGUAGE, ALL = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about language preferences."""
    language_keyboard = [["RUS \U0001F1F7\U0001F1FA"], ["ENG \U0001F1EC\U0001F1E7"]]

    await update.message.reply_text(
        "Привет! Пожалуйста, выбери язык общения со мной: RUS | ENG\n\n"
        "Hi! Please choose the language of communication with me: RUS | ENG",
        reply_markup=ReplyKeyboardMarkup(
            language_keyboard,
            resize_keyboard=False,
            one_time_keyboard=False,
            input_field_placeholder="RUS or ENG?",
        ),
    )

    return LANGUAGE


async def pick_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.match[0].split()[0] if context.match else "RUS"
    commands = {"RUS": ru_keyboard, "ENG": eng_keyboard}[lang]
    await update.message.reply_text(
        "I see! Please send me a photo of yourself, "
        "so I know what you look like, or send /skip if you don't want to.",
        reply_markup=ReplyKeyboardMarkup(
            commands,
            resize_keyboard=False,
            one_time_keyboard=False,
            input_field_placeholder="RUS or ENG?",
        ),
    )

    return ALL


async def repick_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language_keyboard = [["RUS \U0001F1F7\U0001F1FA"], ["ENG \U0001F1EC\U0001F1E7"]]

    await update.message.reply_text(
        "Пожалуйста, выбери язык общения со мной: RUS | ENG\n\n"
        "Please choose the language of communication with me: RUS | ENG",
        reply_markup=ReplyKeyboardMarkup(
            language_keyboard,
            resize_keyboard=False,
            one_time_keyboard=False,
            input_field_placeholder="RUS or ENG?",
        ),
    )

    return LANGUAGE


async def get_random_podcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    podcast = get_random_podcast_link("PLuI-wNAaqFUBIMnOe9eOB-g2MF_Ai6-Zn")
    await update.message.reply_text(
        podcast,
    )

    return ALL


async def get_website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "https://academymarathon.ru",
    )

    return ALL


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    application = ApplicationBuilder().token("TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [
                MessageHandler(
                    filters.Regex(
                        "^(RUS|ENG|RUS \U0001F1F7\U0001F1FA|ENG \U0001F1EC\U0001F1E7)$"
                    ),
                    pick_language,
                ),
                MessageHandler(
                    filters.Regex("^(Stop|stop|Стоп|стоп)$"),
                    cancel,
                ),
            ],
            ALL: [
                MessageHandler(
                    filters.Regex("^(Random podcast|Случайный подкаст)$"),
                    get_random_podcast,
                ),
                MessageHandler(
                    filters.Regex(
                        "^(Webpage|webpage|Сайт|сайт|Веб-сайт \U0001F30F|Webpage \U0001F30F)$$"
                    ),
                    get_website,
                ),
                MessageHandler(
                    filters.Regex(
                        "^(Язык|язык|Language|language|Change language \U0001F1F7\U0001F1FA \U0001F1EC\U0001F1E7|"
                        + "Сменить язык \U0001F1F7\U0001F1FA \U0001F1EC\U0001F1E7)$$"
                    ),
                    repick_language,
                ),
                MessageHandler(
                    filters.Regex("^(Stop|stop|Стоп|стоп)$"),
                    cancel,
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()
