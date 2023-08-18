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

from helpers.consts import FIRST_MATCH, LANGUAGE_CODE, WELCOME_STRING_INDEX
from helpers.regular_expressions import (
    RE_LANGUAGE,
    RE_RANDOM_PODCAST,
    RE_REPICK_LANGUAGE,
    RE_STOP,
    RE_TEAM,
    RE_WEBPAGE,
)
from helpers.texts import language_keyboard, welcome
from helpers.videos_collector import get_random_podcast_link
from localization.eng_replies import (
    eng_answer,
    eng_cancel_answer,
    eng_keyboard,
    eng_team_info,
)
from localization.ru_replies import (
    ru_answer,
    ru_cancel_answer,
    ru_keyboard,
    ru_team_info,
)

LANGUAGE, ALL = range(2)
lang = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about language preferences."""
    await update.message.reply_text(
        welcome[WELCOME_STRING_INDEX],
        reply_markup=ReplyKeyboardMarkup(
            language_keyboard,
            resize_keyboard=False,
            one_time_keyboard=False,
            input_field_placeholder="RUS or ENG?",
        ),
    )

    return LANGUAGE


async def set_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sets commands for specific language."""
    global lang
    lang = context.match[FIRST_MATCH].split()[LANGUAGE_CODE] if context.match else "RUS"
    commands = {"RUS": ru_keyboard, "ENG": eng_keyboard}[lang]
    answer = {"RUS": ru_answer, "ENG": eng_answer}[lang]
    await update.message.reply_text(
        answer,
        reply_markup=ReplyKeyboardMarkup(
            commands,
            resize_keyboard=False,
            one_time_keyboard=False,
        ),
    )

    return ALL


async def repick_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Writes language options for the user to pick."""
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
    """Gets random podcast and sends link to the user."""
    podcast = get_random_podcast_link("PLuI-wNAaqFUBIMnOe9eOB-g2MF_Ai6-Zn")
    await update.message.reply_text(
        podcast,
    )

    return ALL


async def get_website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends link of the website to the user."""
    await update.message.reply_text(
        "https://academymarathon.ru",
    )

    return ALL


async def get_team_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends info about team to the user."""
    global lang
    team_info = {"RUS": ru_team_info, "ENG": eng_team_info}[lang]
    await update.message.reply_photo(photo=open("academy_marathon_team.png", "rb"))
    await update.message.reply_text(
        text=team_info, parse_mode="HTML", disable_web_page_preview=True
    )

    return ALL


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stops conversation with the user."""
    cancel_answer = {"RUS": ru_cancel_answer, "ENG": eng_cancel_answer}[lang]
    await update.message.reply_text(cancel_answer, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    application = ApplicationBuilder().token("Telegram API Bot Token").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [
                MessageHandler(
                    filters.Regex(RE_LANGUAGE),
                    set_commands,
                ),
                MessageHandler(
                    filters.Regex(RE_STOP),
                    cancel,
                ),
                CommandHandler("start", start),
            ],
            ALL: [
                MessageHandler(
                    filters.Regex(RE_RANDOM_PODCAST),
                    get_random_podcast,
                ),
                MessageHandler(
                    filters.Regex(RE_WEBPAGE),
                    get_website,
                ),
                MessageHandler(
                    filters.Regex(RE_REPICK_LANGUAGE),
                    repick_language,
                ),
                MessageHandler(
                    filters.Regex(RE_TEAM),
                    get_team_info,
                ),
                MessageHandler(
                    filters.Regex(RE_STOP),
                    cancel,
                ),
                CommandHandler("start", start),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()
