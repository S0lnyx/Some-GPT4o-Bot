from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Updater
import azure_module
import os
from dotenv import load_dotenv
import configparser

load_dotenv()
config = configparser.ConfigParser()

#Variables initialization
TOKEN = os.getenv("TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
MODEL = os.getenv("MODEL_NAME")
config.read('config.ini')

#Bot responses
cmd_help_text = config['Responses']['Help_command_response']
cmd_test_promt = config['Responses']['Test_command_promt']
cmd_start_text = config['Responses']['Start_command_response']

#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(cmd_start_text)
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(cmd_help_text)

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(azure_module.response_request(cmd_test_promt))

#Handlers
def response_handler(text: str) -> str:
    response = azure_module.response_request(text)
    return response

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'[LOG] User ({update.message.chat.id}:{update.message.chat.full_name}) ({message_type}): "{text}"')

    if message_type == 'group' or message_type == 'supergroup':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = response_handler(new_text)
        else:
            return
    else:
        response: str = response_handler(text)

    print(f'[LOG] {MODEL}: {response}')
    await update.message.reply_text(f'{response}')

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'[ERROR] Update {update}: {context.error}')

#MAIN
if __name__ == '__main__':
    print("[INFO] Bot initialized...")
    app = Application.builder().token(TOKEN).build()
    print("[INFO] Application.build: SUCCESS")

    #Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('test', test_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, message_handler))

    #Errors handler
    app.add_error_handler(error)

    print("[INFO] Bot polling started...")
    app.run_polling(poll_interval=1)