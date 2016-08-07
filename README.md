# ScarcellaBot_CCTV

Si tratta di un semplice gestore per un **[BOT di Telegram](https://core.telegram.org/bots)** che interagisce con le camere IP (ad esempio quelle di un sistema di videosorveglianza casalingo) e preleva le loro immagini _.jpg_ da una cartella sul file system locale inviandole quindi ad uno o più account Telegram.
Le immagini vengono spedite in chat man mano che vengono create sul file system: il modulo `whatchdog` è infatti in ascolto su una cartella locale. Mentre il modulo `telepot` si occupa di gestire il BOT.
In questo modo è possibile farsi spedire le immagini di una camera, magari acquisita a valle di un movimento o di un rumore, direttamente su una chat dedicata su Telegram.

Potete scaricare l'ultima release dello script [da qui](https://github.com/alexscarcella/ScarcellaBot_CCTV/releases).

![un esempio di architettura per l'utilizzo dello script](https://github.com/alexscarcella/ScarcellaBot_CCTV/blob/master/resources/ScarcellaBot_CCTV.png?raw=true "un esempio di architettura per l'utilizzo dello script" {width=40px height=400px})

In questo modo è possibile farsi spedire le immagini di una camera, magari acquisita a valle di un movimento o di un rumore, direttamente su una chat dedicata su Telegram.

## Comandi del bot

- `/help`: elenco comandi (questo!)
- `/jpg`: ti invio le immagini JPG di tutte le camere
- `/motion`: imposto il motion detection
- `/night`: imposto la modalita' nottuna (infrarosso)
- `/status`: ti dico come sto

![alt text](https://github.com/alexscarcella/ScarcellaBot_CCTV/blob/master/resources/ScarcellaBOT%20-%20screeshot%20-%2000002.PNG?raw=true)
![alt text](https://github.com/alexscarcella/ScarcellaBot_CCTV/blob/master/resources/ScarcellaBOT%20-%20screeshot%20-%2000003.PNG?raw=true)
![alt text](https://github.com/alexscarcella/ScarcellaBot_CCTV/blob/master/resources/ScarcellaBOT%20-%20screeshot%20-%2000004.PNG?raw=true)


## Dipendenze

Per far funzionare correttamente lo script del [bot](https://core.telegram.org/bots) è necessario installare alcuni moduli Python aggiuntivi:
- [telepot](https://github.com/nickoala/telepot): Python framework for Telegram Bot API
- [watchdog](https://pypi.python.org/pypi/watchdog): Filesystem events monitoring. Python API and shell utilities to monitor file system events.
- [requests](http://requests.readthedocs.io/en/master/): Non-GMO HTTP library for Python, safe for human consumption.
Potete installare i moduli usando [pip](https://pypi.python.org/pypi/pip).

`$ sudo pip install watchdog`

`$ sudo pip install telepot`

`$ sudo pip install requests`

Per maggiori informazioni visitate il blog [CCWorld.it](http://www.ccworld.it/).

## ScarcellaBot_config.py

E' necessario creare il file di configurazione `ScarcellaBot_config.py` da mettere nella stessa cartella dello script python. Potete editare e rinominare il file di esempio `ScarcellaBot_config.example`:
si tratta ancora di un files di configurazione grossolano (di fatto è un file python, quindi attenti alla sintassi).

Il file è diviso in tre differenti sezioni:
- **BASIC CONFIGURATION**: qui ci sono i valori di configurazione base dello script. Tra cui il Token segreto di Telegram, o la cartella sul file system locale da cui prelevare le immagini.
- **CHAT USER**: qui vengono definiti gli utenti con cui il Bot è abilitato ad interagire. Al momento, e vista la natura dell'applicazione, non è prevista una procedura di sottoscrizione.
- **CAMERE CONFIGURATION**: qui sono definite le camere con i loro parametri per al raggiungibilità nella rete locale. La cosa importante è conoscere le URL di configurazione di ogni vostro modello di camera. In genere tutte le camere IP prevedono delle API va HTTP (oppure sniffate il traccifo, come ho fatto io, e ricavate i parametri in POST).

Sia gli utenti che le camere sono definiti attraverso un Dictionary di Python: ricordatevi quindi di aggiungerli rispettivamente alle variabili `users` e `camere`.
Ad esempio:

```python
# fil#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# ------------------- BASIC CONFIGURATION -------------------------------------
# -----------------------------------------------------------------------------

# inserite qui il Token segreto del BOT Telegram
TELEGRAM_BOT_TOKEN = "fffffffffffffffffffffffffffffffffff"

# path completo della cartella contenente le immagini (un esempio:)
IMAGES_PATH = "/Volumes/images/cctv"

# l'intervallo di tempo minimo (in secondi) che deve trascorrere da un messagio ed il successivo
SEND_SECONDS = 5

# tempo necessario all'invio delle immagini di tutte le camere prima del time-out
SEND_ONDEMAND_TIMOUT = 8

# -----------------------------------------------------------------------------
# ------------------- CHAT USERS ----------------------------------------------
# -----------------------------------------------------------------------------

# user 01
user01 = dict()
user01['name'] = 'Mario'
user01['telegram_id'] = '111111111'
user01['push'] = True

# user 02
user02 = dict()
user02['name'] = 'Alice'
user02['telegram_id'] = '22222222'
user02['push'] = False

users = (user01, user02)

# -----------------------------------------------------------------------------
# ------------------- CAMERE CONFIGURATION ------------------------------------
# -----------------------------------------------------------------------------

# camera 01
camera01 = dict()
camera01['id'] = 'ingresso'
camera01['model'] = 'D-Link DCS-932LB'
camera01['ip'] = '127.0.0.2'
camera01['port'] = '80'
camera01['user'] = 'user'
camera01['pwd'] = 'pwd'
camera01['url_send_jpg_to_folder'] = '/setTestFTP?ReplySuccessPage=replyu.htm&FTPServerTest=+Test+'
camera01['url_motion_detection_off'] = '/setSystemMotion?﻿ReplySuccessPage=motion.htm&ReplyErrorPage=motion.htm&MotionDetectionEnable=0&MotionDetectionScheduleDay=62&ConfigSystemMotion=Save'
camera01['url_motion_detection_on'] = '/setSystemMotion?﻿ReplySuccessPage=motion.htm&ReplyErrorPage=motion.htm&MotionDetectionEnable=1&MotionDetectionScheduleDay=62&MotionDetectionScheduleMode=0&MotionDetectionSensitivity=65&ConfigSystemMotion=Save'
camera01['url_night_mode_auto'] = '/setDayNightMode?ReplySuccessPage=night.htm&ReplyErrorPage=errrnght.htm&LightSensorControl=3&DayNightMode=0&ConfigDayNightMode=Save'
camera01['url_night_mode_off'] = '/setDayNightMode?ReplySuccessPage=night.htm&ReplyErrorPage=errrnght.htm&LightSensorControl=3&DayNightMode=2&ConfigDayNightMode=Save'
camera01['url_night_mode_on'] = '/setDayNightMode?ReplySuccessPage=night.htm&ReplyErrorPage=errrnght.htm&LightSensorControl=3&DayNightMode=3&ConfigDayNightMode=Save'

# camera 02
camera02 = dict()
camera02['id'] = 'sala'
camera02['model'] = 'D-Link DCS-932LB'
camera02['ip'] = '127.0.0.3'
camera02['port'] = '80'
camera02['user'] = 'user'
camera02['pwd'] = 'pwd'
camera02['url_send_jpg_to_folder'] = '/setTestFTP?ReplySuccessPage=replyu.htm&FTPServerTest=+Test+'
camera02['url_motion_detection_off'] = '/setSystemMotion?﻿ReplySuccessPage=motion.htm&ReplyErrorPage=motion.htm&MotionDetectionEnable=0&MotionDetectionScheduleDay=62&ConfigSystemMotion=Save'
camera02['url_motion_detection_on'] =  '/setSystemMotion?﻿ReplySuccessPage=motion.htm&ReplyErrorPage=motion.htm&MotionDetectionEnable=1&MotionDetectionScheduleDay=62&MotionDetectionScheduleMode=0&MotionDetectionSensitivity=65&ConfigSystemMotion=Save'
camera02['url_night_mode_auto'] = '/setDayNightMode?ReplySuccessPage=night.htm&ReplyErrorPage=errrnght.htm&LightSensorControl=3&DayNightMode=0&ConfigDayNightMode=Save'
camera02['url_night_mode_off'] = '/setDayNightMode?ReplySuccessPage=night.htm&ReplyErrorPage=errrnght.htm&LightSensorControl=3&DayNightMode=2&ConfigDayNightMode=Save'
camera02['url_night_mode_on'] = '/setDayNightMode?ReplySuccessPage=night.htm&ReplyErrorPage=errrnght.htm&LightSensorControl=3&DayNightMode=3&ConfigDayNightMode=Save'

camere = (camera01, camera02)
```

E' possibile usare come modello il file `ScarcellaBot_config.example` (da editare e rinominare).

## Servizio

Se volete far girare ScarcellaBot_CCTV come un servizio in background potete creare un file UNIT. Seguite le seguenti istruzioni:

Create il nuovo file `ScarcellaBOT_CCTV.service` nella cartella `/lib/systemd/system/` (potete usare l'editor nano)
Inserite le seguenti righe:

```
[Unit]
Description=ScarcellaBot CCTV Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python /home/pi/Documents/ScarcellaBot/ScarcellaBot_CCTV.py # sostituite con il percorso corretto

[Install]
WantedBy=multi-user.target
```

Sostituite il percorso dello script python dell'esempio in alto con il percorso corretto
Salvate il file, chiudete l'editor di testo. Assegnate i necessari diritti di esecuzione al file tramite il comando:

```
sudo chmod 644 /lib/systemd/system/ScarcellaBOT_CCTV.service
```

Per far partire il servizio al boot digitate:

```
sudo systemctl daemon-reload
sudo systemctl enable ScarcellaBOT_CCTV.service
sudo reboot
```