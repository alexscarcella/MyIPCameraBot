#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
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
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply

# ------ GESTORE DEI COMANDI DEL BOT
class BotCommandsHandler(telepot.Bot):
    # definisco il gestore che deve essere invocato nel loop del bot
    def handle(self, msg):
        print (msg)
        flavor = telepot.flavor(msg)
        if flavor == 'chat':
            content_type, chat_type, chat_id = telepot.glance(msg)
            print ("Chat message: ", content_type, chat_type, chat_id, msg['text'])
            # verifico se l'utente da cui ho ricevuto il comando è censito
            user_exist = False
            for u in ScarcellaBot_config.users:
                if u is None:
                    break
                if u['telegram_id'] == str(chat_id):
                    user_exist = True
                    print ("User exist...")
            # se l'utente non è censito, abortisco
            # questo controllo è per evitare che le risposte dei messaggi
            # vadano a richiedenti non abilitati
            if user_exist == False:
                print ("User NOT exist!!!")
                return None
            # seleziono il tipo di comando da elaborare
            if msg['text'] == '/help':
                self.__comm_help(chat_id)
            elif msg['text'] == '/start':
                self.__comm_help(chat_id)
            elif msg['text'] == '/jpg':
                self.__comm_jpg(chat_id)
            elif msg['text'] == '/status':
                self.__comm_status(chat_id)
            elif msg['text'] == '/motion':
                self.__comm_motion(chat_id)
            elif msg['text'] == 'Motion Detection OFF':
                self.__comm_motion_detection_off(chat_id)
            elif msg['text'] == 'Motion Detection ON':
                self.__comm_motion_detection_on(chat_id)
            elif msg['text'] == '/night':
                self.__comm_night(chat_id)
            elif msg['text'] == 'IR Automatico':
                self.__comm_night_IR_auto(chat_id)
            elif msg['text'] == 'IR On':
                self.__comm_night_IR_On(chat_id)
            elif msg['text'] == 'IR Off':
                self.__comm_night_IR_Off(chat_id)
            else:
                self.__comm_nonCapisco(chat_id)
        else:
            raise telepot.BadFlavor(msg)

    def __comm_help(self, toUser):
        try:
            bot.sendMessage(toUser, helpMessage)
            print('Message sent!')
        except:
            print "Unable to send help message: ", sys.exc_info()[0]

    def __comm_jpg(self, toUser):
        try:
            for camera in ScarcellaBot_config.camere:
                try:
                    url_complete = 'http://' + camera['ip'] + ":" + camera['port'] + camera['url_send_jpg_to_folder']
                    headers = {'Referer': 'http://' + camera['ip'] + ":" + camera['port']}
                    print camera['id'] + ' --> ' + url_complete
                    r = requests.get(url_complete, headers=headers, auth=HTTPBasicAuth(camera['user'], camera['pwd']))
                    print(str(datetime.now()), 'HTTP Status: {0}'.format(r.status_code))
                    if r.status_code == 200:
                        time.sleep(6)
                        last_jpg = max(glob.iglob(ScarcellaBot_config.IMAGES_PATH + '/*.jpg'), key=os.path.getctime)
                        try:
                            last_timestamp = os.path.getatime(last_jpg)
                            bot.sendMessage(toUser, datetime.fromtimestamp(last_timestamp).strftime('%d-%m %H:%M:%S'))
                            f = open(last_jpg, 'rb')
                            print(str(datetime.now()),'Sending the message to ', toUser)
                            bot.sendPhoto(toUser, f)
                        except:
                            print str(datetime.now()), "Unable to send message %s to %s" % (sys.exc_info()[0], u['name'])
                        finally:
                            f.close()
                    else:
                        bot.sendMessage(toUser, 'oops! Camera ' + camera['id'] + ': unable to get image!')
                except:
                    print "Unable to get image: ", sys.exc_info()[0]
        except:
            print "Cameras configuration error: ", sys.exc_info()[0]
        finally:
            time.sleep(6)

    def __comm_status(self, toUser):
        try:
            user = self.__getUser(toUser)
            if user['push'] is True:
                notifiche="ACCESE"
            else:
                notifiche= "SPENTE"
            statusMinutes = ((datetime.now()-startTime).total_seconds()) / 60 / 60
            bot.sendMessage(toUser, "Ciao {2}. Tutto ok.\n"
                                    "Sono in allerta da {0:0,.1f} ore!\n"
                                    "Le tue notifiche push sono {1}!".format(statusMinutes, notifiche, user['name']))
            print('Message sent!')
        except:
            print "Unable to send status message: ", sys.exc_info()[0]

    def __comm_motion(self, toUser):
        try:
            show_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Motion Detection ON'),
                                                           KeyboardButton(text='Motion Detection OFF')],
                                                          ])
            bot.sendMessage(toUser, "Imposta il motion detection:", reply_markup=show_keyboard)
        except:
            print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

    def __comm_motion_detection_off(self, toUser):
        try:
            hide_keyboard = ReplyKeyboardHide()
            bot.sendMessage(toUser, 'Un attimo...', reply_markup=hide_keyboard)
            for camera in ScarcellaBot_config.camere:
                try:
                    url_complete = 'http://' + camera['ip'] + ":" + camera['port'] + camera['url_motion_detection_off']
                    headers = {'Referer': 'http://' + camera['ip'] + ":" + camera['port']}
                    print camera['id'] + ' --> ' + url_complete
                    r = requests.get(url_complete, headers=headers, auth=HTTPBasicAuth(camera['user'], camera['pwd']))
                    # if r.status_code == 200:
                    bot.sendMessage(toUser, 'Camera: {0} -- Motion detection OFF'.format(camera['id']))
                except:
                    print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)
        except:
            print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

    def __comm_motion_detection_on(self, toUser):
        try:
            hide_keyboard = ReplyKeyboardHide()
            bot.sendMessage(toUser, 'Un attimo...', reply_markup=hide_keyboard)
            for camera in ScarcellaBot_config.camere:
                try:
                    url_complete = 'http://' + camera['ip'] + ":" + camera['port'] + camera['url_motion_detection_on']
                    headers = {'Referer': 'http://' + camera['ip'] + ":" + camera['port']}
                    print camera['id'] + ' --> ' + url_complete
                    r = requests.get(url_complete, headers=headers, auth=HTTPBasicAuth(camera['user'], camera['pwd']))
                    # if r.status_code == 200:
                    bot.sendMessage(toUser, 'Camera: {0} -- Motion detection ON'.format(camera['id']))
                except:
                    print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)
        except:
            print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

    def __comm_night(self, toUser):
        try:
            show_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='IR Automatico')],
                                                          [KeyboardButton(text='IR On'), KeyboardButton(text='IR Off')],
                                                          ])
            bot.sendMessage(toUser, "Scegli la modalita' notturna:", reply_markup=show_keyboard)
        except:
            print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

    def __comm_night_IR_auto(self, toUser):
        try:
            hide_keyboard = ReplyKeyboardHide()
            bot.sendMessage(toUser, 'Un attimo...', reply_markup=hide_keyboard)
            for camera in ScarcellaBot_config.camere:
                try:
                    url_complete = 'http://' + camera['ip'] + ":" + camera['port'] + camera['url_night_mode_auto']
                    headers = {'Referer': 'http://' + camera['ip'] + ":" + camera['port']}
                    print camera['id'] + ' --> ' + url_complete
                    r = requests.get(url_complete, headers=headers, auth=HTTPBasicAuth(camera['user'], camera['pwd']))
                    if r.status_code == 200:
                        bot.sendMessage(toUser, 'Camera: {0} -- Infrared AUTO'.format(camera['id']))
                    else:
                        bot.sendMessage(toUser, 'Camera: {0} -- non riesco a comunicare con la camera!!'.format(camera['id']))
                except:
                    print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)
            self.__comm_jpg(toUser)
        except:
            print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

    def __comm_night_IR_On(self, toUser):
        try:
            hide_keyboard = ReplyKeyboardHide()
            bot.sendMessage(toUser, 'Un attimo...', reply_markup=hide_keyboard)
            for camera in ScarcellaBot_config.camere:
                try:
                    url_complete = 'http://' + camera['ip'] + ":" + camera['port'] + camera['url_night_mode_on']
                    headers = {'Referer': 'http://' + camera['ip'] + ":" + camera['port']}
                    print camera['id'] + ' --> ' + url_complete
                    r = requests.get(url_complete, headers=headers, auth=HTTPBasicAuth(camera['user'], camera['pwd']))
                    if r.status_code == 200:
                        bot.sendMessage(toUser, 'Camera: {0} -- Infrared ON'.format(camera['id']))
                    else:
                        bot.sendMessage(toUser, 'Camera: {0} -- non riesco a comunicare con la camera!!'.format(camera['id']))
                except:
                    print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

        except:
            print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

    def __comm_night_IR_Off(self, toUser):
        try:
            hide_keyboard = ReplyKeyboardHide()
            bot.sendMessage(toUser, 'Un attimo...', reply_markup=hide_keyboard)
            for camera in ScarcellaBot_config.camere:
                try:
                    url_complete = 'http://' + camera['ip'] + ":" + camera['port'] + camera['url_night_mode_off']
                    headers = {'Referer': 'http://' + camera['ip'] + ":" + camera['port']}
                    print camera['id'] + ' --> ' + url_complete
                    r = requests.get(url_complete, headers=headers, auth=HTTPBasicAuth(camera['user'], camera['pwd']))
                    if r.status_code == 200:
                        bot.sendMessage(toUser, 'Camera: {0} -- Infrared OFF'.format(camera['id']))
                    else:
                        bot.sendMessage(toUser, 'Camera: {0} -- non riesco a comunicare con la camera!!'.format(camera['id']))
                except:
                    print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

        except:
            print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

    def __comm_nonCapisco(self, toUser):
        try:
            bot.sendMessage(toUser, "Non capisco...")
        except:
            print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)

    def __getUser(self, userID):
        for usr in ScarcellaBot_config.users:
            if usr['telegram_id'] == str(userID):
                return usr
        return None

# ------ GESTORE DEL WATCHDOG
class WatchdogHandler(FileSystemEventHandler):
    def on_created(self, event):
        print "New file: " + event.src_path
        global lastMessage
        # controllo che i nuovi files siano immagini con estensione .jpg
        if os.path.splitext(event.src_path)[1] != ".jpg":
            print("The file is not a .jpg")
            return None  # no image .jpg
        # ciclo tra gli utenti in configurazione
        for u in ScarcellaBot_config.users:
            # verifico che gli utenti abbiano le notifiche PUSH abilitate e che sia già
            # trascorso il tempo minimo tra due invii successivi
            if u['push'] is True and (datetime.now()-lastMessage).seconds > ScarcellaBot_config.SEND_SECONDS:
                try:
                    f = open(event.src_path, 'rb')
                    print(str(datetime.now()), 'Sending the message to ', u)
                    bot.sendPhoto(u['telegram_id'], f)
                    lastMessage = datetime.now() # aggiorno il dateTime di ultima notifica
                except:
                    print str(datetime.now()), "Unable to send message %s to %s" % (sys.exc_info()[0], u['name'])
                finally:
                    f.close()
            else:
                print(str(datetime.now()), "Message not sent. The user may be configured without sending push. "
                      "They must spend at least {0} seconds"
                      "after the last transmission ({1})".format(ScarcellaBot_config.SEND_SECONDS, lastMessage))

if __name__ == "__main__":
    # memorizzo il datetime dell'avvio dell'applicazione.
    # lo uso per dare il messaggio di status, che contiene
    # le ore di attività del server
    startTime = datetime.now()
    # datetime dell'ultimo messaggio inviato:
    # E' possibile infatti impostare che tra un messaggio ed il successivo
    # debbano trascorrere almeno un TOT di secondi
    lastMessage = datetime.now()
    # ------ TELEGRAM --------------
    # inizializzo il BOT usando il TOKEN segreto dal file di configurazione
    # ed utilizzando la classe gestore
    try:
        bot = BotCommandsHandler(ScarcellaBot_config.TELEGRAM_BOT_TOKEN)
        print("Bot:", bot.getMe())
    except:
        print "Impossibile inizializzare il BOT: ", sys.exc_info()[0]
        exit()
    # invio un messaggio di benvenuto agli utenti censiti nel file di configurazione
    try:
        helpMessage = 'Ecco i miei comandi:\n' \
                      '/help: elenco comandi (questo!)\n' \
                      '/jpg: ti invio le immagini JPG di tutte le tue camere\n' \
                      '/motion: imposto il motion detection\n' \
                      "/night: imposto la modalita' nottuna (infrarosso)\n" \
                      '/status: ti dico come sto\n'
        for u in ScarcellaBot_config.users:
            if u is None:
                break
            print('Welcome...', u)
            welcome = 'Adesso sono attivo!\n\n' \
                      'Posso inviarti le immagini delle camere quando rilevo un movimento. ' \
                      'Oppure potrai chedermele tu quando vuoi.\n\n'
            bot.sendMessage(u['telegram_id'], 'Ciao {0}! '.format(u['name']) + welcome + helpMessage)
        bot.message_loop()
        print("in ascolto...")
    except:
        print "Problemi nella configuazione degli utenti: ", sys.exc_info()[0]
    # ------ WATCHDOG --------------
    try:
        # leggo il path su cui abilitare il watchDog dal file di configurazione,
        # altrimenti imposto di default il percorso in cui risiede lo script python
        watchDogPath = ScarcellaBot_config.IMAGES_PATH if ScarcellaBot_config.IMAGES_PATH > 1 else '.'
        # associo la classe che gestisce la logica del watchDog, gli passo il percorso
        # sul fil system locale e spengo la recursione delle cartelle
        observer = Observer()
        observer.schedule(WatchdogHandler(), watchDogPath, recursive=False)
        # avvio il watchdog
        observer.start()
    except:
        print "Errore del watchdog: ", sys.exc_info()[0]
    # tengo in vita il processo fino a che
    # qualcuno non lo interrompe da tastiera
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()






