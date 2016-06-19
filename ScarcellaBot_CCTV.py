#!/usr/bin/env python2.7
"""
creare un file di configurazione ScarcellaBot_config
nel quale definire le seguenti variabili

TELEGRAM_BOT_TOKEN
TELEGRAM_USERS_ID
IMAGES_PATH
"""
import ScarcellaBot_config
import sys
import time
import os
import telepot
import requests # TODO inserire la dipendeza nel readme
from requests.auth import HTTPBasicAuth
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pprint import pprint
from datetime import datetime


class WatchdogHandler(FileSystemEventHandler):
    def on_created(self, event):
        print "New file: " + event.src_path
        global lastMessage
        if os.path.splitext(event.src_path)[1] != ".jpg":
            print("Il file non e' un .jpg")
            return None
        if (send_ondemand is True) or \
                (send_ondemand is False and (datetime.now()-lastMessage).seconds > ScarcellaBot_config.SEND_SECONDS):
            for u in ScarcellaBot_config.users:
                try:
                    f = open(event.src_path, 'rb')
                    print('Invio il messaggio a: ', u)
                    bot.sendPhoto(u['telegram_id'], f)
                    lastMessage = datetime.now()
                except:
                    print "Impossibile inviare l'immagine %s a %s" % (sys.exc_info()[0], u['name'])
                finally:
                    f.close()
        else:
            print("Non invio il messaggio. Devono passare almeno {0} secondi dall'ultimo invio ({1})".format(ScarcellaBot_config.SEND_SECONDS,
                                                                                                             lastMessage))


class ScarcellaBotCommands(telepot.Bot):
    # definisco il gestore che deve essere invocato nel loop del bot
    def handle(self, msg):
        # pprint(msg)
        flavor = telepot.flavor(msg)
        # Do your stuff according to `content_type` ...
        if flavor == 'chat':
            content_type, chat_type, chat_id = telepot.glance(msg)
            print ("Chat message: ", content_type, chat_type, chat_id, msg['text'])
            if msg['text'] == '/help':
                self.__Comm_help()
            elif msg['text'] == '/jpg':
                self.__Comm_jpg()
            else:
                bot.sendMessage(u, 'Non capisco...')
        else:
            raise telepot.BadFlavor(msg)


    def __Comm_help(self):
        try:
            bot.sendMessage(u, helpMessage)
        except:
            print "Impossibile inviare il messaggio di help: ", sys.exc_info()[0]


    def __Comm_jpg(self):
        global send_ondemand
        send_ondemand = True
        try:
            for camera in ScarcellaBot_config.camere:
                try:
                    url_complete = 'http://' + camera['ip'] + ":" + camera['port'] + camera['url_send_jpg_to_folder']
                    print camera['id'] + ' --> ' + url_complete
                    r = requests.get(url_complete, auth=HTTPBasicAuth(camera['user'], camera['pwd']))
                    print('HTTP Status: {0}'.format(r.status_code))
                    time.sleep(5)
                except:
                    print "Impossibile inviare una immagine alla cartella: ", sys.exc_info()[0]
        except:
            print "Problemi con la configurazione delle camere: ", sys.exc_info()[0]


if __name__ == "__main__":
    lastMessage = datetime.now()  # datetime dell'ultimo messaggio inviato
    send_ondemand = False
    send_ondemand_timer=0
    # ------ TELEGRAM --------------
    helpMessage = 'Ecco i miei comandi:\n'\
                    '/help: elenco comandi (questo!)\n'\
                    '/jpg: ti invio le immagini JPG di tutte le tue camere\n'
    try:
        bot = ScarcellaBotCommands(ScarcellaBot_config.TELEGRAM_BOT_TOKEN)
        print("Bot:", bot.getMe())
    except:
        print "Impossibile inizializzare il BOT: ", sys.exc_info()[0]
        exit()
    try:
        for u in ScarcellaBot_config.users:
            print('Welcome...', u)
            welcome = 'Adesso sono attivo!\n\nPosso inviarti le immagini delle camere quando rilevo un movimento. Oppure potrai chedermele tu quando vuoi.\n\n'
            bot.sendMessage(u['telegram_id'], 'Ciao {0}! '.format(u['name']) + welcome + helpMessage)
        bot.message_loop()
        print("in ascolto...")
    except:
        print "Problemi nella configuazione degli utenti: ", sys.exc_info()[0]
    # ------ WATCHDOG --------------
    try:
        path = ScarcellaBot_config.IMAGES_PATH if ScarcellaBot_config.IMAGES_PATH > 1 else '.'
        event_handler = WatchdogHandler()
        observer = Observer()
        observer.schedule(event_handler, path, recursive=False)
        observer.start()
    except:
        print "Errore del watchdog: ", sys.exc_info()[0]
    # ------ Processo --------------
    # tengo in vita il processo fino a che
    # qualcuno non lo interrompe da tastiera
    try:
        while 1:
            if send_ondemand is True:
                send_ondemand_timer += 1
            if send_ondemand_timer > ScarcellaBot_config.SEND_ONDEMAND_TIMOUT:
                send_ondemand_timer = 0
                send_ondemand = False
            # print("send: {0} - timer: {1}".format(send_ondemand, send_ondemand_timer))
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        bot.sendMessage(u, 'Stop!! - ')
    observer.join()
