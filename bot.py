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


# Esta funcion es la quqe de la el inicio al Bot
def start(update, context):

    update.message.reply_text(
        "Este es un Bot que permite controlar y comprobar ciertos aspectos del Servidor de Procesos. Para conocer los comandos implementados consulta la /ayuda")


def ip(update, CallbackContext):
    ip = llamadaSistema("hostname -I")  # Llamada al sistema
    ip = ip[:-1]
    update.message.reply_text(ip)  # Respondemos al comando con el mensaje


def pwd(update, CallbackContext):
    _pwd = llamadaSistema("pwd")  # Llamada al sistema
    # Respondemos al comando con el mensaje
    update.message.reply_text(_pwd)


def red_conectada(update, CallbackContext):
    ssidred = llamadaSistema("ifconfig")  # Llamada al sistema
    # Respondemos al comando con el mensaje
    update.message.reply_text(ssidred)


def ls(update, CallbackContext,):
    _ls = llamadaSistema("ls ")  # Llamada al sistema
    update.message.reply_text(_ls)  # Respondemos al comando con el mensaje


def cd(update, CallbackContext, args):
    if len(args) == 1:  # Comprobar si el comando presenta argumento o no
        directorio = args[0]
        os.chdir(directorio)
        # Respondemos al comando con el mensaje
        update.message.reply_text("Cambiando al directorio " + directorio)
    else:
        # Respondemos al comando con el mensaje
        update.message.reply_text(
            "Se debe especificar el directorio al que acceder.\n\nEjemplo:\n/cd /home/usuario")


def cat(update, CallbackContext, args):

    if len(args) == 1:  # Comprobar si el comando presenta argumento o no
        _cat = llamadaSistema("cat " + args[0])  # Llamada al sistema
        # Determinamos el numero de caracteres que tiene el archivo
        num_caracteres_fichero = len(_cat)
        if num_caracteres_fichero < 4096:  # Si el numero de caracteres es menor a 4096 se envia un unico mensaje con todo el contenido
            # Respondemos al comando con el mensaje
            update.message.reply_text(_cat)
        else:  # Si el numero de caracteres es superior a 4096, se divide el contenido del archivo en diversos fragmentos de texto que se enviaran en varios mensajes
            # Se determina el numero de mensajes a enviar
            num_mensajes = num_caracteres_fichero/float(4095)
            # Si no es un numero entero (es decimal)
            if isinstance(num_mensajes, numbers.Integral) != True:
                # Se aumenta el numero de mensajes en 1
                num_mensajes = int(num_mensajes) + 1
            fragmento = 0
            # Se van enviando cada fragmento de texto en diversos mensajes
            for i in range(0, num_mensajes):
                # Creamos un mensaje correspondiente al fragmento de texto actual
                mensaje = _cat[fragmento:fragmento +
                               4095].decode('utf-8', 'ignore')
                # Respondemos al comando con el mensaje
                update.message.reply_text(mensaje)
                # Aumentamos el fragmento de texto (cursor de caracteres)
                fragmento = fragmento + 4095
    else:
        # Respondemos al comando con el mensaje
        update.message.reply_text(
            "Especifica un archivo.\n\nEjemplo:\n/cat /home/user/archivo.txt")


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler("ip", ip))
    dp.add_handler(CommandHandler("red_conectada", red_conectada))
    dp.add_handler(CommandHandler("pwd", pwd))
    dp.add_handler(CommandHandler("cd", cd, pass_args=True))
    dp.add_handler(CommandHandler("ls", ls, pass_args=True))
    dp.add_handler(CommandHandler("cat", cat, pass_args=True))

    # Comandos de prueba

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
