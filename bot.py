from telegram.ext import Updater, CommandHandler


def start(update, context):
    
    
    update.message.reply_text('Hola Fran, todo funciona ok')


if __name__ == '__main__':
    var_token = '1713890847:AAFMyn7tUKocgypCZRYiLRUvUzZSgaFsTrw'
    var_chatid = 'xxxx'
    updater = Updater(token=var_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))

    # Comandos de prueba

    updater.start_polling()
    updater.idle()
