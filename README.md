# ScarcellaBot_CCTV

Si tratta di un gestore base per un **BOT di Telegram** che preleva immagini da una cartella sul file system locale (ad esempio le immagini prodotte da un sistema di videosorveglianza, magari scaricate via FTP) e le invia ad uno o più account Telegram.
Le immagini vengono spedite in chat man mano che vengono create sul file system: il modulo `whatchdog` sta infatti in ascolto su una cartella locale. Mentre il modulo `telepot` si occupa di gestire il BOT ed i messaggi.

_Lo script è in fase di redazione_

Per maggiori informazioni visitate il blog [CCWorld.it](http://www.ccworld.it/).

E' necessario creare il file di configurazione `ScarcellaBot_config.py` da mettere nella stessa cartella dello script python.
Il file definisce i valori di due parametri che è meglio tenere segreti:
- `TELEGRAM_BOT_TOKEN`: il token segreto del Bot di telegram
- `TELEGRAM_USER_ID`: l'ID dell'utente a cui volete spedire le immagini

Ad esempio:

```
## fil#!/usr/bin/env python2.7
##
# inserite qui il Token segreto del BOT Telegram
TELEGRAM_BOT_TOKEN="fffffffffffffffffffffffffffffffffff"

# inserite qui l'ID dell'utente Telegram a cui volete spedire le immagini
TELEGRAM_USER_ID="0000000"
```