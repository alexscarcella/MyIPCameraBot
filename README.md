# ScarcellaBot_CCTV

Si tratta di un semplice gestore per un **[BOT di Telegram](https://core.telegram.org/bots)** che preleva immagini _.jpg_ da una cartella sul file system locale e le invia ad uno o più account Telegram.
Le immagini vengono spedite in chat man mano che vengono create sul file system: il modulo `whatchdog` sta infatti in ascolto su una cartella locale. Mentre il modulo `telepot` si occupa di gestire il BOT ed i messaggi.

Personalmente uso questo semplice script con il sistema di videosorveglianza casalingo: ogni camera IP è in grado di inviare snapshot _.jpg_ su un server FTP o su una cartella condivisa nella rete locale. In questo modo è possibile farsi spedire le immagini di una camera, magari acquisita a valle di un movimento o di un romore, direttamente su una chat dedicata su Telegram.


## Comandi del bot

`/help`: elenco comandi (questo!)
`/jpg`: ti invio le immagini JPG di tutte le camere

TODO:
con il tempo mi piacerebbe implementare un set completo di comandi per spegnere ed accendere le camere, inviarmi immagini o spezzoni video a richiesta o cambiare alcuni parametri di funzionamento.


## ScarcellaBot_config.py

E' necessario creare il file di configurazione '`ScarcellaBot_config.py` da mettere nella stessa cartella dello script python.
Il file definisce i valori di alcuni parametri (alcuni dei quali è meglio tenere segreti).
Ad esempio:

```
# fil#!/usr/bin/env python2.7

# inserite qui il Token segreto del BOT Telegram
TELEGRAM_BOT_TOKEN = "fffffffffffffffffffffffffffffffffff"

# inserite qui gli ID degli utenti Telegram a cui volete spedire le immagini (lista separata da virgola)
# Meglio tenere questi dati riservati
TELEGRAM_USERS_ID = ["0000000000", "11111111111"]

# path completo della cartella contenente le immagini (un esempio:)
IMAGES_PATH = "/Volumes/images/cctv"

# l'intervallo di tempo minimo (in secondi) che deve trascorrere da un messagio ed il successivo
SEND_SECONDS = 60

# tempo necessario all'invio delle immagini di tutte le camere prima del time-out
SEND_ONDEMAND_TIMOUT = 18
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
