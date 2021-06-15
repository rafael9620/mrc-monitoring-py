# Importando librerias necesarias.
import os
import sys
import time
import numbers
import subprocess



# Importando desde la libreria de Telegram
from telegram.ext import Updater, CommandHandler

# A establecer por el usuario (consultar mediante @BotFather)
TOKEN = "1713890847:AAFMyn7tUKocgypCZRYiLRUvUzZSgaFsTrw"
ID = 1268569363

def llamadaSistema(entrada):
    salida = ""  # Creamos variable vacia
    f = os.popen(entrada)  # Llamada al sistema
    for i in f.readlines():  # Leemos caracter a caracter sobre la linea devuelta por la llamada al sistema
        salida += i  # Insertamos cada uno de los caracteres en nuestra variable
    salida = salida[:-1]  # Truncamos el caracter fin de linea '\n'

    return salida  # Devolvemos la respuesta al comando ejecutado




#Esta funcion es la quqe de la el inicio al Bot
def start(update, context):

    update.message.reply_text("Este es un Bot que permite controlar y comprobar ciertos aspectos del Servidor de Procesos. Para conocer los comandos implementados consulta la /ayuda")


def ip(update, CallbackContext):
    ip = llamadaSistema("hostname -I")  # Llamada al sistema
    ip = ip[:-1]  
    update.message.reply_text(ip)  # Respondemos al comando con el mensaje





def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler("ip", ip))
    
    
    

    # Comandos de prueba

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

    
