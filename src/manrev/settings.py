import json
import os
import shutil
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox,
    QHBoxLayout, QLineEdit, QFileDialog, QMessageBox,
    QTabWidget, QListWidget, QListWidgetItem, QWidget, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
from paths import path_manager

class ManRevSettings:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = os.path.join(self.base_dir, 'data', 'config')
        self.settings_file = os.path.join(self.config_dir, "manrev_config.json")
        
        self.default_settings = {
            "capitoli": [],
            "default_place": "Decimoputzu",
            "default_treasurer": "",
            "default_president": "",
            "default_accountant": "",
            "sede_image": "",
            "firme": {
                "tesoriere_firma": "",
                "presidente_firma": "",
                "addetto_firma": ""
            },
            "last_mandato": 0,
            "last_reversale": 0,
            "year": datetime.now().year,
            "firma_presidente": "",
            "firma_tesoriere": "",
            "firma_segretario": ""
        }
        self.current_settings = self.load_settings()

    def load_settings(self):
        current = self.default_settings.copy()
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    for key in self.default_settings:
                        if key in saved_settings:
                            current[key] = saved_settings[key]
        except Exception:
            return current
        return current

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=4)
        except Exception as e:
            print(f"Errore nel salvare le impostazioni: {e}")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setMinimumWidth(600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Crea il tab widget
        tab_widget = QTabWidget()
        
        # Tab Generali
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        # Valori predefiniti
        defaults_group = QGroupBox("Valori Predefiniti")
        defaults_layout = QVBoxLayout()
        
        # Anno
        year_layout = QHBoxLayout()
        year_label = QLabel("Anno:")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(manrev_settings.current_settings["year"])
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_spin)
        defaults_layout.addLayout(year_layout)
        
        # Luogo
        place_row = QHBoxLayout()
        place_row.addWidget(QLabel("Luogo:"))
        self.place_input = QLineEdit()
        self.place_input.setText(manrev_settings.current_settings["default_place"])
        place_row.addWidget(self.place_input)
        defaults_layout.addLayout(place_row)
        
        # Tesoriere
        treasurer_row = QHBoxLayout()
        treasurer_row.addWidget(QLabel("Tesoriere:"))
        self.treasurer_input = QLineEdit()
        self.treasurer_input.setText(manrev_settings.current_settings["default_treasurer"])
        treasurer_row.addWidget(self.treasurer_input)
        defaults_layout.addLayout(treasurer_row)
        
        # Presidente
        president_row = QHBoxLayout()
        president_row.addWidget(QLabel("Presidente:"))
        self.president_input = QLineEdit()
        self.president_input.setText(manrev_settings.current_settings["default_president"])
        president_row.addWidget(self.president_input)
        defaults_layout.addLayout(president_row)
        
        # Addetto Contabile
        accountant_row = QHBoxLayout()
        accountant_row.addWidget(QLabel("Addetto Contabile:"))
        self.accountant_input = QLineEdit()
        self.accountant_input.setText(manrev_settings.current_settings["default_accountant"])
        accountant_row.addWidget(self.accountant_input)
        defaults_layout.addLayout(accountant_row)
        
        defaults_group.setLayout(defaults_layout)
        general_layout.addWidget(defaults_group)
        
        
        general_tab.setLayout(general_layout)
        tab_widget.addTab(general_tab, "Generali")
        
        #Tab firme
        signatures_tab = QWidget()
        signatures_layout = QVBoxLayout()
        
        #Firma Tesoriere
        self.treasurer_sign = self.create_signature_row("Firma Tesoriere", "tesoriere_firma")
        signatures_layout.addLayout(self.treasurer_sign)

        # Firma Presidente
        self.president_sign = self.create_signature_row("Firma Presidente", "presidente_firma")
        signatures_layout.addLayout(self.president_sign)
        
        # Firma Addetto
        self.accountant_sign = self.create_signature_row("Firma Addetto", "addetto_firma")
        signatures_layout.addLayout(self.accountant_sign)
        
        signatures_tab.setLayout(signatures_layout)
        tab_widget.addTab(signatures_tab, "Firme")
        
        # Tab Capitoli
        capitoli_tab = QWidget()
        capitoli_layout = QVBoxLayout()
        
        # Lista dei capitoli
        capitoli_group = QGroupBox("Gestione Capitoli")
        capitoli_inner_layout = QVBoxLayout()
        
        # Input per nuovo capitolo
        new_capitolo_layout = QHBoxLayout()
        self.new_capitolo_input = QLineEdit()
        self.new_capitolo_input.setPlaceholderText("Inserisci nuovo capitolo...")
        add_button = QPushButton("Aggiungi")
        add_button.clicked.connect(self.add_capitolo)
        new_capitolo_layout.addWidget(self.new_capitolo_input)
        new_capitolo_layout.addWidget(add_button)
        capitoli_inner_layout.addLayout(new_capitolo_layout)
        
        # Lista dei capitoli esistenti
        self.capitoli_list = QListWidget()
        self.capitoli_list.addItems(manrev_settings.current_settings.get("capitoli", []))
        capitoli_inner_layout.addWidget(self.capitoli_list)
        
        # Pulsante rimuovi
        remove_button = QPushButton("Rimuovi Selezionato")
        remove_button.clicked.connect(self.remove_capitolo)
        capitoli_inner_layout.addWidget(remove_button)
        
        capitoli_group.setLayout(capitoli_inner_layout)
        capitoli_layout.addWidget(capitoli_group)
        
        capitoli_tab.setLayout(capitoli_layout)
        tab_widget.addTab(capitoli_tab, "Capitoli")
        
        # Tab Immagini
        images_tab = QWidget()
        images_layout = QVBoxLayout()
        
        # Gruppo Sede
        sede_group = QGroupBox("Immagine Sede")
        sede_layout = QVBoxLayout()
        
        # Immagine corrente
        self.sede_preview = QLabel()
        self.sede_preview.setMinimumSize(200, 100)
        self.sede_preview.setAlignment(Qt.AlignCenter)
        self.update_sede_preview()  # Inizializza l'anteprima
        sede_layout.addWidget(self.sede_preview)
        
        # Pulsanti
        sede_buttons = QHBoxLayout()
        select_sede_btn = QPushButton("Seleziona Immagine")
        select_sede_btn.clicked.connect(self.browse_sede_image)
        sede_buttons.addWidget(select_sede_btn)
        
        clear_sede_btn = QPushButton("Rimuovi Immagine")
        clear_sede_btn.clicked.connect(self.clear_sede_image)
        sede_buttons.addWidget(clear_sede_btn)
        
        sede_layout.addLayout(sede_buttons)
        sede_group.setLayout(sede_layout)
        images_layout.addWidget(sede_group)
        
        images_tab.setLayout(images_layout)
        tab_widget.addTab(images_tab, "Immagini")
        
        layout.addWidget(tab_widget)
        
        # Pulsante salva
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        self.setLayout(layout)

    def create_signature_row(self, label_text, key):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        
        path_input = QLineEdit()
        path_input.setText(manrev_settings.current_settings["firme"][key])
        row.addWidget(path_input)
        
        browse_btn = QPushButton("Sfoglia")
        browse_btn.clicked.connect(lambda: self.browse_signature(path_input, key))
        row.addWidget(browse_btn)
        
        setattr(self, f"{key}_input", path_input)
        return row

    def browse_signature(self, path_input, signature_type):
        """Gestisce la selezione e il salvataggio della firma"""
        try:
            # Seleziona il file
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Seleziona Firma",
                "",
                "Immagini (*.png *.jpg *.jpeg)"
            )
            
            if file_path:
                # Crea la directory delle firme se non esiste
                docs_path = os.path.join(os.path.expanduser("~"), "Documents")
                signatures_dir = os.path.join(docs_path, "Abe", "ManRev", "firme")
                os.makedirs(signatures_dir, exist_ok=True)
                
                # Crea il nome del file di destinazione
                file_ext = os.path.splitext(file_path)[1]
                dest_filename = f"{signature_type}{file_ext}"
                dest_path = os.path.join(signatures_dir, dest_filename)
                
                # Copia il file nella directory delle firme
                shutil.copy2(file_path, dest_path)
                
                # Aggiorna il percorso nel campo di input e nelle impostazioni
                path_input.setText(dest_path)
                manrev_settings.current_settings["firme"][f"{signature_type}_firma"] = dest_path
                manrev_settings.save_settings()
                
                QMessageBox.information(
                    self,
                    "Successo",
                    f"Firma salvata correttamente in: {dest_path}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel salvare la firma: {str(e)}"
            )

    def add_capitolo(self):
        """Aggiunge un nuovo capitolo alla lista"""
        capitolo = self.new_capitolo_input.text().strip()
        if capitolo:
            if capitolo not in [self.capitoli_list.item(i).text() 
                              for i in range(self.capitoli_list.count())]:
                self.capitoli_list.addItem(capitolo)
                self.new_capitolo_input.clear()
            else:
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    "Questo capitolo esiste già!"
                )

    def remove_capitolo(self):
        """Rimuove il capitolo selezionato"""
        current_item = self.capitoli_list.currentItem()
        if current_item:
            self.capitoli_list.takeItem(self.capitoli_list.row(current_item))

    def save_settings(self):
        try:
            # Salva i capitoli
            capitoli = [self.capitoli_list.item(i).text() 
                       for i in range(self.capitoli_list.count())]
            
            manrev_settings.current_settings.update({
                "capitoli": capitoli,
                "default_place": self.place_input.text(),
                "default_treasurer": self.treasurer_input.text(),
                "default_president": self.president_input.text(),
                "default_accountant": self.accountant_input.text(),
                "firme": {
                    "tesoriere_firma": self.tesoriere_firma_input.text(),
                    "presidente_firma": self.presidente_firma_input.text(),
                    "addetto_firma": self.addetto_firma_input.text()
                },
                "year": self.year_spin.value()
            })
            
            manrev_settings.save_settings()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel salvare le impostazioni: {str(e)}"
            )

    def browse_sede_image(self):
        """Gestisce la selezione dell'immagine della sede"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Seleziona Immagine Sede",
                "",
                "Immagini (*.png *.jpg *.jpeg)"
            )
            
            if file_path:
                # Crea la directory delle immagini se non esiste
                docs_path = os.path.join(os.path.expanduser("~"), "Documents")
                images_dir = os.path.join(docs_path, "Abe", "ManRev", "immagini")
                os.makedirs(images_dir, exist_ok=True)
                
                # Copia l'immagine
                dest_path = os.path.join(images_dir, "sede" + os.path.splitext(file_path)[1])
                shutil.copy2(file_path, dest_path)
                
                # Aggiorna le impostazioni
                manrev_settings.current_settings["sede_image"] = dest_path
                manrev_settings.save_settings()
                
                # Aggiorna l'anteprima
                self.update_sede_preview()
                
                QMessageBox.information(
                    self,
                    "Successo",
                    "Immagine della sede salvata correttamente"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel salvare l'immagine: {str(e)}"
            )

    def clear_sede_image(self):
        """Rimuove l'immagine della sede"""
        try:
            if "sede_image" in manrev_settings.current_settings:
                if os.path.exists(manrev_settings.current_settings["sede_image"]):
                    os.remove(manrev_settings.current_settings["sede_image"])
                manrev_settings.current_settings.pop("sede_image")
                manrev_settings.save_settings()
                self.update_sede_preview()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel rimuovere l'immagine: {str(e)}")

    def update_sede_preview(self):
        """Aggiorna l'anteprima dell'immagine della sede"""
        if "sede_image" in manrev_settings.current_settings:
            path = manrev_settings.current_settings["sede_image"]
            if os.path.exists(path):
                pixmap = QPixmap(path)
                self.sede_preview.setPixmap(pixmap.scaled(200, 100, Qt.KeepAspectRatio))
                return
        self.sede_preview.setText("Nessuna immagine")

# Istanza singleton delle impostazioni
manrev_settings = ManRevSettings() 