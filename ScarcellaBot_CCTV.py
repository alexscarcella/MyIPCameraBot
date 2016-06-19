#!/usr/bin/env python2.7
"""
Devi editare il file di configurazione ScarcellaBot_config.py
Puoi fare riferimento al file di esempio ScarcellaBot_config.example
-
You must edit the configuration file ScarcellaBot_config.py
You may refer to the sample files ScarcellaBot_config.example
"""
import ScarcellaBot_config
import sys
import time
import os
import glob
import telepot
import requests
from requests.auth import HTTPBasicAuth
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime


class WatchdogHandler(FileSystemEventHandler):
    def on_created(self, event):
        print "New file: " + event.src_path
        global lastMessage
        if os.path.splitext(event.src_path)[1] != ".jpg":
            print("The file is not a .jpg")
            return None  # no image .jpg
        for u in ScarcellaBot_config.users:
            if (u['push'] is True and (datetime.now()-lastMessage).seconds > ScarcellaBot_config.SEND_SECONDS):
                try:
                    f = open(event.src_path, 'rb')
                    print('Sending the message to ', u)
                    bot.sendPhoto(u['telegram_id'], f)
                    lastMessage = datetime.now()
                except:
                    print "Unable to send message %s to %s" % (sys.exc_info()[0], u['name'])
                finally:
                    f.close()
            else:
                print("Message not sent. The user may be configured without sending push. "
                      "Or not sent to time-out. "
                      "They must spend at least {0} seconds after the last transmission ({1})".format(ScarcellaBot_config.SEND_SECONDS,
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
                self.__Comm_help(chat_id)
            elif msg['text'] == '/jpg':
                self.__Comm_jpg(chat_id)
            elif msg['text'] == '/status':
                self.__Comm_status(chat_id)
            else:
                bot.sendMessage(u, 'Non capisco...')
        else:
            raise telepot.BadFlavor(msg)


    def __Comm_help(self, toUser):
        try:
            bot.sendMessage(toUser, helpMessage)
        except:
            print "Unable to send help message: ", sys.exc_info()[0]


    def __Comm_jpg(self, toUser):
        try:
            for camera in ScarcellaBot_config.camere:
                try:
                    url_complete = 'http://' + camera['ip'] + ":" + camera['port'] + camera['url_send_jpg_to_folder']
                    print camera['id'] + ' --> ' + url_complete
                    r = requests.get(url_complete, auth=HTTPBasicAuth(camera['user'], camera['pwd']))
                    print('HTTP Status: {0}'.format(r.status_code))
                    time.sleep(3)
                    last_jpg = max(glob.iglob(ScarcellaBot_config.IMAGES_PATH + '/*.jpg'), key=os.path.getctime)
                    try:
                        f = open(last_jpg, 'rb')
                        print('Sending the message to ', toUser)
                        bot.sendPhoto(toUser, f)
                    except:
                        print "Unable to send message %s to %s" % (sys.exc_info()[0], u['name'])
                    finally:
                        f.close()
                except:
                    print "Impossibile inviare una immagine alla cartella: ", sys.exc_info()[0]
        except:
            print "Problemi con la configurazione delle camere: ", sys.exc_info()[0]


    def __Comm_status(self, toUser):
        try:
            statusMinutes = ((((datetime.now()-startTime).seconds) % 3600) // 60)
            bot.sendMessage(toUser, "Tutto ok. Sono in allerta da {0} minuti!".format(statusMinutes))
        except:
            print "Unable to send status message: ", sys.exc_info()[0]


if __name__ == "__main__":
    startTime = datetime.now()
    lastMessage = datetime.now()  # datetime dell'ultimo messaggio inviato
    # ------ TELEGRAM --------------
    helpMessage = 'Ecco i miei comandi:\n'\
                    '/help: elenco comandi (questo!)\n'\
                    '/jpg: ti invio le immagini JPG di tutte le tue camere\n'\
                    '/status: ti dico come sto\n'
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
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        bot.sendMessage(u, 'Stop!! - ')
    observer.join()
