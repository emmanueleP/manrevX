import os
import platform
import sys
from datetime import datetime

class PathManager:
    def __init__(self):
        self.system = platform.system()
        self.setup_base_paths()
        
    def setup_base_paths(self):
        """Configura i percorsi base per l'applicazione"""
        if self.system == "Windows":
            self.documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
        elif self.system == "Darwin":  # macOS
            self.documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
        else:  # Linux/Unix
            self.documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
            
        # Directory principale dell'applicazione
        self.app_dir = os.path.join(self.documents_dir, "Abe")
        
        # Directory ManRev (unica applicazione supportata)
        self.manrev_dir = os.path.join(self.app_dir, "ManRev")
        
        # Directory per i dati dell'applicazione
        if self.system == "Windows":
            self.app_data_dir = os.path.join(os.getenv('APPDATA'), "Abe")
        elif self.system == "Darwin":
            self.app_data_dir = os.path.join(
                os.path.expanduser("~"),
                "Library/Application Support/Abe"
            )
        else:
            self.app_data_dir = os.path.join(
                os.path.expanduser("~"),
                ".config/abe"
            )
            
        # Crea le directory se non esistono
        self.ensure_directories()
    
    def ensure_directories(self):
        """Crea tutte le directory necessarie"""
        directories = [
            self.app_dir,
            self.manrev_dir,
            self.app_data_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_config_path(self, app_name):
        """Ottiene il percorso del file di configurazione per un'app"""
        return os.path.join(self.app_data_dir, f"{app_name}_config.json")
    
    def get_year_dir(self, base_dir, year=None):
        """Ottiene la directory per un anno specifico"""
        if year is None:
            year = str(datetime.now().year)
        year_dir = os.path.join(base_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)
        return year_dir
    
    def get_temp_dir(self):
        """Ottiene la directory temporanea dell'applicazione"""
        temp_dir = os.path.join(self.app_data_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    def get_logs_dir(self):
        """Ottiene la directory per i log"""
        logs_dir = os.path.join(self.app_data_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir

# Istanza singleton del gestore percorsi
path_manager = PathManager() 