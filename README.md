# ScarcellaBot_CCTV

Si tratta di un semplice gestore per un **[BOT di Telegram](https://core.telegram.org/bots)** che preleva immagini _.jpg_ da una cartella sul file system locale e le invia ad uno o più account Telegram.
Le immagini vengono spedite in chat man mano che vengono create sul file system: il modulo `whatchdog` è infatti in ascolto su una cartella locale. Mentre il modulo `telepot` si occupa di gestire il BOT.

Potete scaricare l'ultima release dello script [da qui](https://github.com/alexscarcella/ScarcellaBot_CCTV/releases).

![alt text](https://github.com/alexscarcella/ScarcellaBot_CCTV/blob/master/resources/ScarcellaBot_CCTV.png?raw=true "un esempio di utilizzo"){: style="float:right"}

Personalmente uso questo semplice script con il sistema di videosorveglianza casalingo: ogni camera IP è in grado di inviare snapshot _.jpg_ su un server FTP o su una cartella condivisa nella rete locale. In questo modo è possibile farsi spedire le immagini di una camera, magari acquisita a valle di un movimento o di un romore, direttamente su una chat dedicata su Telegram.


## Comandi del bot

`/help`: elenco comandi (questo!)
`/jpg`: ti invio le immagini JPG di tutte le camere
`/status`: ti dico come sto

TODO:
con il tempo mi piacerebbe implementare un set completo di comandi per spegnere ed accendere le camere, inviarmi immagini o spezzoni video a richiesta o cambiare alcuni parametri di funzionamento.


## ScarcellaBot_config.py

E' necessario creare il file di configurazione `ScarcellaBot_config.py` da mettere nella stessa cartella dello script python. Potete editare e rinominare il file di esempio `ScarcellaBot_config.example`:
si tratta ancora di un files di configurazione grossolano (di fatto è un file python, quindi attenti alla sintassi).

Il file definisce i valori di alcuni parametri (alcuni dei quali è meglio tenere segreti!).
Ad esempio:

```
# fil#!/usr/bin/env python2.7

# -----------------------------------------------------------------------------
# ------------------- BASIC CONFIGURATION -------------------------------------
# -----------------------------------------------------------------------------

# inserite qui il Token segreto del BOT Telegram
TELEGRAM_BOT_TOKEN = "fffffffffffffffffffffffffffffffffff"

# path completo della cartella contenente le immagini (un esempio:)
IMAGES_PATH = "/Volumes/images/cctv"

# l'intervallo di tempo minimo (in secondi) che deve trascorrere da un messagio ed il successivo
SEND_SECONDS = 60

# tempo necessario all'invio delle immagini di tutte le camere prima del time-out
SEND_ONDEMAND_TIMOUT = 18

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

# camera 02
camera02 = dict()
camera02['id'] = 'sala'
camera02['model'] = 'D-Link DCS-932LB'
camera02['ip'] = '127.0.0.3'
camera02['port'] = '80'
camera02['user'] = 'user'
camera02['pwd'] = 'pwd'
camera02['url_send_jpg_to_folder'] = '/setTestFTP?ReplySuccessPage=replyu.htm&FTPServerTest=+Test+'

camere = (camera01, camera02)
```

E' possibile usare come modello il file `ScarcellaBot_config.example` (da editare e rinominare).

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
