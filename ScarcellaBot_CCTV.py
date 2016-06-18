#!/usr/bin/env python2.7
"""
creare un file di configurazione ScarcellaBot_config
nel quale definire le seguenti variabili

TELEGRAM_BOT_TOKEN
TELEGRAM_USERS_ID
IMAGES_PATH
"""
import ScarcellaBot_config
import ScarcellaBot_camere
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
        if os.path.splitext(event.src_path)[1] == ".jpg" and \
                        (datetime.now()-lastMessage).seconds > ScarcellaBot_config.SEND_SECONDS:
            for user in ScarcellaBot_config.TELEGRAM_USERS_ID:
                try:
                    f = open(event.src_path, 'rb')
                    print 'Invio il messaggio a: ' + user
                    bot.sendPhoto(user, f)
                    lastMessage = datetime.now()
                except:
                    print "Impossibile inviare l'immagine %s a %s" % (sys.exc_info()[0], user)
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
        try:
            for camera in ScarcellaBot_camere.camere:
                try:
                    send_ondemand = True
                    url_complete = 'http://' + camera['ip'] + ":" + camera['port'] + camera['url_send_jpg_to_folder']
                    print camera['id'] + ' --> ' + url_complete
                    r = requests.get(url_complete, auth=HTTPBasicAuth(camera['user'], camera['pwd']))
                    print('HTTP Status: {0}'.format(r.status_code))
                    time.sleep(5)
                except:
                    print "Impossibile inviare una immagine alla cartella: ", sys.exc_info()[0]
        except:
            print "Problemi con la configurazione delle camere: ", sys.exc_info()[0]
        finally:
            send_ondemand = False


if __name__ == "__main__":
    lastMessage = datetime.now()  # datetime dell'ultimo messaggio inviato
    send_ondemand = False
    # ------ TELEGRAM --------------
    helpMessage = 'Ecco i miei comandi:\n'\
                    '/help: elenco comandi\n'\
                    '/jpg: ti invio le immagini delle camere\n'
    try:
        bot = ScarcellaBotCommands(ScarcellaBot_config.TELEGRAM_BOT_TOKEN)
        print("Bot:", bot.getMe())
        for u in ScarcellaBot_config.TELEGRAM_USERS_ID:
            print('Invio il saluto a ', u)
            bot.sendMessage(u, 'Ciao! Adesso sono attivo!\n\n' + helpMessage)
        bot.message_loop()
        print("in ascolto...")
    except:
        print "Impossibile inizializzare il BOT: ", sys.exc_info()[0]
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
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        bot.sendMessage(u, 'Stop!! - ')
    observer.join()
