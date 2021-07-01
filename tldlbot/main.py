import logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, callbackcontext, CommandHandler
from telegram.constants import CHATACTION_TYPING
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from tldlbot.mysecrets import watson_secrets, telegram_secrets

STT = None

def start(update: Update, context: callbackcontext.CallbackContext):
    user = update.effective_user
    update.message.reply_text(
        f"""Hi.
        Sende mir einfach eine Sprachnachricht und ich transkribiere sie für dich."""
    )


def setup_transcription() -> SpeechToTextV1:
    authenticator = IAMAuthenticator(watson_secrets["apikey"])

    speech_to_text = SpeechToTextV1(
        authenticator=authenticator
    )

    speech_to_text.set_service_url(watson_secrets["base_url"])

    speech_to_text.set_disable_ssl_verification(True)

    return speech_to_text


def transcribe_message(update: Update, context):
    update.message.reply_text("Alright, habe deine Nachricht bekommen. Höre zu... das dauert vielleicht ein bisschen!")
    update.message.reply_chat_action(CHATACTION_TYPING)
    
    voice_file = update.message.voice.get_file().download()
    logging.info(voice_file)
    with open(voice_file, 'rb') as audio_file:
        results = STT.recognize(
            audio=audio_file,
            model="de-DE_NarrowbandModel"    
        ).get_result()
    logging.info(results)
    for result in results["results"]:
        update.message.reply_text(result['alternatives'][0]['transcript'], quote=True)


def main():
    updater = Updater(telegram_secrets["token"])

    STT = setup_transcription()

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.voice, transcribe_message))

    updater.start_polling()

if __name__ == "__main__":
    main()