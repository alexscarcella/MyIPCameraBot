#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Devi editare il file di configurazione MyIPCameraBot_config.py
Puoi fare riferimento al file di esempio MyIPCameraBot_config.example
-
You must edit the configuration file MyIPCameraBot_config.py
You may refer to the sample files MyIPCameraBot_config.example
"""
import MyIPCameraBot_config
import sys
import time
import os
import glob
import telepot
import requests
import socket
import logging
import logging.handlers
import io
from datetime import datetime
from PIL import Image
from requests.auth import HTTPBasicAuth
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from base64 import b64encode

# pip install Pillow


# ------ GESTORE DEI COMANDI DEL BOT
class BotCommandsHandler(telepot.Bot):

    # definisco il gestore che deve essere invocato nel loop del bot
    def handle(self, msg):
        try:
            my_logger.debug("COMMAND: " + str(msg))
            flavor = telepot.flavor(msg)
            if flavor == 'chat':
                content_type, chat_type, chat_id = telepot.glance(msg)
                my_logger.info("Chat message: " + content_type + " - Type: " + chat_type + " - ID: " + str(chat_id) + " - Command: " + msg['text'])
                # verifico se l'utente da cui ho ricevuto il comando è censito
                user_exist = False
                for u in MyIPCameraBot_config.users:
                    if u is None:
                        break
                    if u['telegram_id'] == str(chat_id):
                        user_exist = True
                        my_logger.debug("Check userID " + u['telegram_id'] + ": user exist...")
                # se l'utente non è censito, abortisco
                # questo controllo è per evitare che le risposte dei messaggi
                # vadano a richiedenti non abilitati
                if user_exist == False:
                    my_logger.info("User NOT exist!!!")
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
                    self.__comm_motion_detection(chat_id, msg["from"]["first_name"], 0)
                elif msg['text'] == 'Motion Detection ON':
                    self.__comm_motion_detection(chat_id, msg["from"]["first_name"], 1)
                elif msg['text'] == '/night':
                    self.__comm_night(chat_id)
                elif msg['text'] == 'IR Automatic':
                    self.__comm_night_IR(chat_id, 0)
                elif msg['text'] == 'IR On':
                    self.__comm_night_IR(chat_id, 2)
                elif msg['text'] == 'IR Off':
                    self.__comm_night_IR(chat_id, 3)
                else:
                    self.__comm_nonCapisco(chat_id)
            else:
                raise telepot.BadFlavor(msg)
        except:
            my_logger.exception("Unable to parse command: " + str(sys.exc_info()[0]))

    # ------------------------------------
    # CameraName = DCS - 932LB
    # Model = DCS - 932LB1
    # HardwareVersion = B
    # CGIVersion=2.1.8
    # ------------------------------------
    # /motion.cgi?MotionDetectionEnable=0&ConfigReboot=no
    # /daynight.cgi?DayNightMode=0&ConfigReboot=0
    # ------------------------------------
    def __call_camera(selfself, cam, type_url):
        try:
            url_complete = 'http://' + cam['ip'] + ":" + cam['port'] + type_url
            my_logger.debug("CALL: " + cam['id'] + ' --> ' + url_complete)
            headers = {'Referer': 'http://' + cam['ip'] + ":" + cam['port'] + ' HTTP/1.0',
                     'Authorization': 'Basic ' + b64encode("{0}:{1}".format(cam['user'], cam['pwd']))}
            my_logger.debug("Headers: " + str(headers))
            r = requests.get(url_complete, headers=headers, auth=HTTPBasicAuth(cam['user'], cam['pwd']))
            my_logger.info(cam['id'] + ' --> ' + "HTTP Status: {0}".format(r.status_code))
            if r.status_code != 200:
                my_logger.debug("Unable to contact camera!")
            return r
        except:
            my_logger.exception("Unable to call camera! " + str(sys.exc_info()[0]))

    def __comm_help(self, toUser):
        try:
            bot.sendMessage(toUser, helpMessage)
            my_logger.info('HELP message sent to user ' + str(toUser))
        except:
            my_logger.exception("Unable to send help message: " + str(sys.exc_info()[0]))

    def __comm_jpg(self, toUser):
        try:
            for camera in MyIPCameraBot_config.camere:
                r = self.__call_camera(camera, camera['url_jpg'])
                if r.status_code == 200:
                    try:
                        my_logger.debug("JPG data available")
                        f = io.BytesIO(r.content)
                        img = Image.open(f)
                        now = datetime.now()
                        jpg_filename = MyIPCameraBot_config.IMAGES_PATH + '/{0}{1}.jpg'.format(camera['id'], now.strftime("%Y%m%d%H%M%S"))
                        img.save(jpg_filename, 'JPEG')
                        my_logger.info("Create JPEG: " + jpg_filename)
                    except:
                        my_logger.exception("Unable to create image file.")
                    finally:
                        f.close()
                        img.close()
                    send_bot_image(toUser, jpg_filename)
                else:
                    bot.sendMessage(toUser, 'oops! Unable to contact camera ' + camera['id'])
        except:
            my_logger.exception("Unable to get image: " + str(sys.exc_info()))
        finally:
            time.sleep(3)

    def __comm_status(self, toUser):
        try:
            hostname=socket.gethostname()
            user = self.__getUser(toUser)
            if user['push'] is True:
                notifiche="ON"
            else:
                notifiche= "OFF"
            statusMinutes = ((datetime.now()-startTime).total_seconds()) / 60 / 60
            bot.sendMessage(toUser, "Hi {0}. I run on {1} and it's all ok!\n"
                                    "I am alert from {2:0,.1f} hours!\n"
                                    "Your push notifications are {3}!\n\n"
                                    "more info at www.ccworld.it\n".format(user['name'], hostname, statusMinutes, notifiche))
            my_logger.info("STATUS sent to user " + str(toUser))
        except:
            my_logger.exception("Command failed! " + str(sys.exc_info()[0]))

    def __comm_motion(self, toUser):
        try:
            show_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Motion Detection ON'),
                                                           KeyboardButton(text='Motion Detection OFF')],
                                                          ])
            my_logger.debug("Reply keyboard showed.")
            bot.sendMessage(toUser, "Set motion detection: ", reply_markup=show_keyboard)
            my_logger.info("MOTION message sent to user " + str(toUser))
        except:
            my_logger.exception("Command failed! " + str(sys.exc_info()[0]))

    def __comm_motion_detection(self, toUser, first_name, enabled):
        try:
            hide_keyboard = ReplyKeyboardRemove()
            my_logger.debug("Keyboard hided")
            bot.sendMessage(toUser, 'wait...', reply_markup=hide_keyboard)
            for camera in MyIPCameraBot_config.camere:
                try:
                    r = self.__call_camera(camera, camera['url_motion_detection'].format(enabled))
                    if r.status_code == 200:
                        for u in MyIPCameraBot_config.users:
                            if u is None:
                                continue
                            if u['push'] is True:
                                bot.sendMessage(u['telegram_id'], 'Camera: {0} - Motion detection:{1} ' 
                                                                  'by {2}'.format(camera['id'], enabled, u['name']))
                                my_logger.info("MOTION command sent to user " + u['name'])
                    else:
                        bot.sendMessage(toUser, 'oops! Unable to contact camera ' + camera['id'])
                except:
                    print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)
        except:
            my_logger.exception("Command failed! " + str(sys.exc_info()[0]))

    def __comm_night(self, toUser):
        try:
            show_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='IR Automatic')],
                                                          [KeyboardButton(text='IR On'), KeyboardButton(text='IR Off')],
                                                          ])
            bot.sendMessage(toUser, "Select a night mode:", reply_markup=show_keyboard)
            my_logger.info("NIGHT message sent to user " + str(toUser))
        except:
            my_logger.exception("Command failed! " + str(sys.exc_info()[0]))

    def __comm_night_IR(self, toUser, enabled):
        try:
            hide_keyboard = ReplyKeyboardRemove()
            my_logger.debug("Keyboard hided")
            bot.sendMessage(toUser, 'wait...', reply_markup=hide_keyboard)
            for camera in MyIPCameraBot_config.camere:
                try:
                    r = self.__call_camera(camera, camera['url_motion_detection'].format(enabled))
                    if r.status_code == 200:
                        bot.sendMessage(toUser, 'Camera: {0} -- Infrared: {1}'.format(camera['id'], enabled))
                        my_logger.info("IR AUTO message sent to user " + str(toUser))
                    else:
                        bot.sendMessage(toUser, 'oops! Unable to contact camera ' + camera['id'])
                except:
                    print(str(datetime.now()), 'Command failed! ', sys.exc_info()[0], toUser)
        except:
            my_logger.exception("Command failed! " + str(sys.exc_info()[0]))

    def __comm_nonCapisco(self, toUser):
        try:
            bot.sendMessage(toUser, "sorry I do not understand...")
            my_logger.info("NOT UNDERSTAND message sent to user " + str(toUser))
        except:
            my_logger.exception("Command failed! " + str(sys.exc_info()[0]))

    def __getUser(self, userID):
        for usr in MyIPCameraBot_config.users:
            if usr['telegram_id'] == str(userID):
                return usr
        return None


def create_logger():
    try:
        # create logger
        global my_logger
        my_logger = logging.getLogger('MyLogger')
        my_logger.setLevel(logging.DEBUG)

        # create rotating file handler and set level
        fl = logging.handlers.RotatingFileHandler(
            MyIPCameraBot_config.LOG_FILENAME, maxBytes=500000, backupCount=5)
        fl.setLevel(logging.INFO)

        # create console handler and set level to debug
        cns = logging.StreamHandler(sys.stdout)
        cns.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatters
        fl.setFormatter(formatter)
        cns.setFormatter(formatter)

        # add ch to logger
        my_logger.addHandler(fl)
        my_logger.addHandler(cns)

        my_logger.debug("Rotating File logger created")
    except:
        print(str(sys.exc_info()))
        my_logger.exception("Unable to create logger")


def send_bot_image(toUser, filename):
    try:
        my_logger.info("New ondemand JPG: " + filename)
        f = open(filename, 'rb')
        bot.sendPhoto(toUser, f)
        my_logger.debug('Image message sent to ' + str(toUser))
        lastMessage = datetime.now()  # aggiorno il dateTime di ultima notifica
        my_logger.debug("Last message dateTime set @: " + str(lastMessage))
    except:
        my_logger.exception("Unable to send image message to user")
    finally:
        f.close()


# ------ GESTORE DEL WATCHDOG
class WatchdogHandler(FileSystemEventHandler):

    def on_created(self, event):
        my_logger.debug("Auto discover new JPG: " + event.src_path)

        # controllo che i nuovi files siano immagini con estensione .jpg
        if os.path.splitext(event.src_path)[1] != ".jpg":
            my_logger.debug("The new file is not a .jpg")
            return None  # no image .jpg
        if (datetime.now() - lastMessage).seconds < MyIPCameraBot_config.SEND_SECONDS:
            my_logger.info("Too many transmissions. Passed only {0}/{1} seconds.".format((datetime.now() - lastMessage).seconds, MyIPCameraBot_config.SEND_SECONDS))
            return None  # no image .jpg
        # ciclo tra gli utenti in configurazione
        for u in MyIPCameraBot_config.users:
            if u is None:
                continue
            # verifico che gli utenti abbiano le notifiche PUSH abilitate e che sia già
            # trascorso il tempo minimo tra due invii successivi
            if u['push'] is True:  # and (datetime.now()-lastMessage).seconds > MyIPCameraBot_config.SEND_SECONDS:
                send_bot_image(u['telegram_id'], event.src_path)
            else:
                my_logger.info("Message not sent. The user may be configured without sending push. "
                      "They must spend at least {0} seconds"
                      "after the last transmission ({1})".format(MyIPCameraBot_config.SEND_SECONDS, lastMessage))

if __name__ == "__main__":

    create_logger()

    startTime = datetime.now()
    my_logger.info("--------------------------------------")
    my_logger.info("START @: " + str(startTime))

    # datetime dell'ultimo messaggio inviato:
    # E' possibile infatti impostare che tra un messaggio ed il successivo
    # debbano trascorrere almeno un TOT di secondi
    global lastMessage
    lastMessage = datetime.now()
    my_logger.debug("Last message dateTime set @: " + str(lastMessage))

    # ------ TELEGRAM --------------
    # inizializzo il BOT usando il TOKEN segreto dal file di configurazione
    # ed utilizzando la classe gestore
    try:
        bot = BotCommandsHandler(MyIPCameraBot_config.TELEGRAM_BOT_TOKEN)
        my_logger.info("Bot: " + str(bot.getMe()))
    except:
        my_logger.exception("Unable to init BOT!")
        my_logger.exception("Unable to init BOT: EXIT!! " + str(sys.exc_info()[0]))
        exit()
    # invio un messaggio di benvenuto agli utenti censiti nel file di configurazione
    try:
        helpMessage = 'My commands:\n' \
                      '/help: commands list\n' \
                      '/jpg: I send you all JPG camera snapshot\n' \
                      '/motion: set motion detection\n' \
                      "/night: set night mode (infrared)\n" \
                      '/status: my status\n\n' \
                      '  more info at www.ccworld.it\n'
        for u in MyIPCameraBot_config.users:
            if u is None:
                break
            my_logger.info('Welcome to Telegram user: ' + str(u))
            welcome = "I'm active now!!\n\n" \
                      "I can send you camera's images when I detect a movement. " \
                      "Or you can ask for them whenever you want.\n\n"
            bot.sendMessage(u['telegram_id'], 'Hi {0}! '.format(u['name']) + welcome + helpMessage)
        bot.message_loop()
        my_logger.info("Listen...")
    except:
        my_logger.exception("Problemi nella configuazione degli utenti: " + str(sys.exc_info()[0]))
    # ------ WATCHDOG --------------
    try:
        # leggo il path su cui abilitare il watchDog dal file di configurazione,
        # altrimenti imposto di default il percorso in cui risiede lo script python
        # watchDogPath = MyIPCameraBot_config.IMAGES_PATH if MyIPCameraBot_config.IMAGES_PATH > 1 else '.'
        watchDogPath = MyIPCameraBot_config.IMAGES_PATH
        # associo la classe che gestisce la logica del watchDog, gli passo il percorso
        # sul fil system locale e spengo la recursione delle cartelle
        observer = Observer()
        observer.schedule(WatchdogHandler(), watchDogPath, recursive=False)
        # avvio il watchdog
        observer.start()
        my_logger.debug("Watchdog started")
    except:
        my_logger.exception("Watchdog error")
    # tengo in vita il processo fino a che
    # qualcuno non lo interrompe da tastiera
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()






