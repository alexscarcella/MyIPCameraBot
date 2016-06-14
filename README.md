# ScarcellaBot_CCTV

[provvisorio] Si tratta del gestore di un **BOT di Telegram** che preleva immagini da una cartella sul file system locale (ad esempio le immagini prodotte da un sistema di videosorveglianza, magari scaricate via FTP) e le invia ad uno o più account Telegram.
_Lo script è in fase di redazione_

Per maggiori informazioni visitate il blog [CCWorld.it](http://www.ccworld.it/).

E' necessario creare il file di configurazione `ScarcellaBot_config.py` da mettere nella stessa cartella dello script python.

Con il seguente testo:

```
## fil#!/usr/bin/env python2.7
##
# inserite qui il Token segreto del BOT Telegram
TELEGRAM_BOT_TOKEN="fffffffffffffffffffffffffffffffffff"

# inserite qui l'ID dell'utente Telegram a cui volete spedire le immagini
TELEGRAM_USER_ID="0000000"
```