# manrevX

![Logo ManRev]

L'idea di ManRevX nasce da un precedente progetto che comprendeva una suite di app (nome in code "Abe") da me creato lo scorso anno. Poiché il modulo dell'app che usavo di più era ManRev, ho deciso di esportarlo e creare un'apposita repo per quest'app.
L'applicazione permette ad associazioni ed enti locali di **generare, archiviare e stampare mandati di pagamento e reversali di esazione** in formato Word, mantenendo un flusso identico all'originale: scelta del tipo documento, inserimento dati contabili, gestione firme digitalizzate e invio alla stampa.

## Caratteristiche

- Interfaccia PyQt5.
- Generazione di documenti `.docx` usando `python-docx` con intestazioni, tabelle dati, importo in lettere e firme grafiche configurabili.
- Gestione dei capitoli di bilancio, dei firmatari e dell'immagine della sede attraverso la finestra **Impostazioni**.
- Salvataggio automatico dello stato del form (tutti i campi tranne la descrizione) in `~/Documents/Abe/ManRev/manrev_form_state.json` per riproporre i dati alla riapertura.
- Stampa opzionale post-generazione: su Windows tramite `pywin32` (Word Automation), su macOS tramite il comando `lp`.

## Requisiti

- Python 3.10+
- Pip/venv (consigliato)
- Librerie elencate in `requirements.txt`
  - `pywin32` viene installato solo su Windows; su macOS non è necessario

Alla prima esecuzione vengono create le cartelle dati in `~/Documents/Abe/ManRev`. Le impostazioni locali sono salvate in `data/config/manrev_config.json`, mentre i file prodotti finiscono per default in `~/Documents/Abe/ManRev`.

## Creazione del pacchetto macOS (.dmg)

Lo script `create_dmg.sh` genera la versione macOS completa:

```bash
chmod +x create_dmg.sh
./create_dmg.sh
```

Il comando:
1. Esegue PyInstaller (con `--paths src`) per produrre `dist/ManRevX.app`.
2. Allestisce la cartella di staging con l'alias `/Applications`.
3. Crea e comprime il DMG (`ManRevX.dmg`).

## Note su macOS

- Per la stampa è necessario avere almeno una stampante configurata (`lpstat -p`).

## Licenza

Il codice è distribuito con la licenza proprietaria descritta in `LICENSE.md`, mentre le librerie di terze parti mantengono le rispettive licenze open source.
