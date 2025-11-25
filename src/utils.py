import os
import sys
import platform
from paths import path_manager

def get_asset_path(filename):
    """
    Ottiene il percorso corretto per un file nella cartella assets,
    sia in sviluppo che nell'eseguibile
    """
    try:
        # PyInstaller crea una cartella temporanea e memorizza il percorso in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se non siamo in un eseguibile, usa il percorso normale
        base_path = os.path.abspath(".")

    return os.path.join(base_path, 'src', 'assets', filename)

def get_data_path(filename):
    """
    Ottiene il percorso per un file di dati di ManRev
    """
    return os.path.join(path_manager.manrev_dir, filename)

def get_config_path():
    """
    Ottiene il percorso del file di configurazione di ManRev
    """
    return path_manager.get_config_path("manrev") 