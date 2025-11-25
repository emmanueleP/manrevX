import json
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QAction, QHBoxLayout, QGroupBox,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QCheckBox, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QIcon
from .settings import manrev_settings
from .generator import generate_documents
from .about_dialog import AboutDialog
from utils import get_asset_path, get_data_path
from .print_aftergen import print_manager
import os
from datetime import datetime

class ManRevGUI(QMainWindow):
    closed = pyqtSignal()
    STATE_FILENAME = "manrev_form_state.json"
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("ManRev - Gestione Mandati e Reversali")
        self.setGeometry(200, 200, 800, 600)
        self.setup_menu()
        self.setup_ui()
        self.state_path = get_data_path(self.STATE_FILENAME)
        self.load_form_state()
        
        if self.app:
            self.apply_theme()
        # Imposta l'icona
        self.setWindowIcon(QIcon(get_asset_path('logo_manrev.png')))

    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        generate_action = QAction('Genera Documento...', self)
        generate_action.triggered.connect(self.generate_document)
        generate_action.setShortcut('Ctrl+G')
        file_menu.addAction(generate_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Esci', self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(exit_action)
        
        # Menu Impostazioni
        settings_menu = menubar.addMenu('Impostazioni')
        settings_action = QAction('Configura...', self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)
        
        # Menu Help
        help_menu = menubar.addMenu('Help')
        about_action = QAction('Informazioni...', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Gruppo Tipo Documento
        doc_group = QGroupBox("Tipo Documento")
        doc_layout = QHBoxLayout()
        
        self.doc_type = QComboBox()
        self.doc_type.addItems(["Mandato di Pagamento", "Reversale di Esazione"])
        doc_layout.addWidget(self.doc_type)
        
        doc_group.setLayout(doc_layout)
        layout.addWidget(doc_group)
        
        # Gruppo Informazioni Documento
        info_group = QGroupBox("Informazioni Documento")
        info_layout = QVBoxLayout()
        
        # Numero
        num_row = QHBoxLayout()
        num_row.addWidget(QLabel("Numero:"))
        self.number_input = QLineEdit()
        num_row.addWidget(self.number_input)
        info_layout.addLayout(num_row)
        
        # Capitolo
        cap_row = QHBoxLayout()
        cap_row.addWidget(QLabel("Capitolo:"))
        self.chapter_input = QComboBox()
        self.chapter_input.setEditable(True)
        self.chapter_input.addItems(manrev_settings.current_settings.get("capitoli", []))
        self.chapter_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        cap_row.addWidget(self.chapter_input)
        info_layout.addLayout(cap_row)
        
        # Importo
        amount_row = QHBoxLayout()
        amount_row.addWidget(QLabel("Importo €:"))
        self.amount_input = QLineEdit()
        amount_row.addWidget(self.amount_input)
        info_layout.addLayout(amount_row)
        
        # Descrizione
        desc_row = QHBoxLayout()
        desc_row.addWidget(QLabel("Descrizione:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        desc_row.addWidget(self.description_input)
        info_layout.addLayout(desc_row)
        
        # Data e Luogo
        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Data:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        date_row.addWidget(self.date_input)
        
        date_row.addWidget(QLabel("Luogo:"))
        self.place_input = QLineEdit()
        self.place_input.setText(manrev_settings.current_settings.get("default_place", ""))
        date_row.addWidget(self.place_input)
        info_layout.addLayout(date_row)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Gruppo Firme
        sign_group = QGroupBox("Firme")
        sign_layout = QVBoxLayout()
        
        # Tesoriere
        tres_row = QHBoxLayout()
        tres_row.addWidget(QLabel("Il Tesoriere:"))
        self.treasurer_input = QLineEdit()
        self.treasurer_input.setText(manrev_settings.current_settings.get("default_treasurer", ""))
        tres_row.addWidget(self.treasurer_input)
        sign_layout.addLayout(tres_row)
        
        # Presidente
        pres_row = QHBoxLayout()
        pres_row.addWidget(QLabel("Il Presidente:"))
        self.president_input = QLineEdit()
        self.president_input.setText(manrev_settings.current_settings.get("default_president", ""))
        pres_row.addWidget(self.president_input)
        sign_layout.addLayout(pres_row)
        
        # Addetto Contabile
        acc_row = QHBoxLayout()
        acc_row.addWidget(QLabel("L'Addetto Contabile:"))
        self.accountant_input = QLineEdit()
        self.accountant_input.setText(manrev_settings.current_settings.get("default_accountant", ""))
        acc_row.addWidget(self.accountant_input)
        sign_layout.addLayout(acc_row)
        
        sign_group.setLayout(sign_layout)
        layout.addWidget(sign_group)
        
        # Opzioni
        options_layout = QHBoxLayout()
        self.print_check = QCheckBox("Stampa dopo la generazione")
        options_layout.addWidget(self.print_check)
        layout.addLayout(options_layout)
        
        # Pulsante genera
        self.generate_button = QPushButton("Genera Documento")
        self.generate_button.clicked.connect(self.generate_document)
        layout.addWidget(self.generate_button)

    def generate_document(self):
        """Genera il documento"""
        try:
            # Crea il dizionario con i dati del documento
            doc_data = {
                'Tipo': self.doc_type.currentText(),
                'Numero': self.number_input.text(),
                'Capitolo': self.chapter_input.currentText(),
                'Importo in €': self.amount_input.text(),
                'Descrizione del pagamento': self.description_input.toPlainText(),
                'Data': self.date_input.date().toString("dd/MM/yyyy"),
                'Luogo': self.place_input.text(),
                'Il Tesoriere': self.treasurer_input.text(),
                'Il Presidente': self.president_input.text(),
                "L'Addetto Contabile": self.accountant_input.text(),
                'anno': datetime.now().strftime("%Y")
            }
            
            # Prepara il percorso del file
            output_dir = manrev_settings.current_settings.get("output_directory", "")
            if not output_dir:
                output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Abe", "ManRev")
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{doc_data['Tipo']}_{doc_data['Numero']}_{datetime.now().strftime('%Y%m%d')}.docx"
            output_file = os.path.join(output_dir, filename)
            
            # Genera il documento
            output_file = generate_documents(doc_data, output_file)
            
            # Stampa solo se il checkbox è selezionato
            if self.print_check.isChecked():
                if print_manager.print_document(output_file, self):
                    QMessageBox.information(
                        self,
                        "Completato",
                        "Il documento è stato generato e stampato con successo."
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Completato",
                        "Il documento è stato generato ma non stampato."
                    )
            else:
                QMessageBox.information(
                    self,
                    "Completato",
                    f"Il documento è stato generato in:\n{output_file}"
                )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore durante la generazione del documento:\n{str(e)}"
            )

    def show_settings(self):
        from .settings import SettingsDialog
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Aggiorna i valori predefiniti
            self.place_input.setText(manrev_settings.current_settings["default_place"])
            self.treasurer_input.setText(manrev_settings.current_settings["default_treasurer"])
            self.president_input.setText(manrev_settings.current_settings["default_president"])
            self.accountant_input.setText(manrev_settings.current_settings["default_accountant"])
            # Aggiorna la lista dei capitoli
            self.chapter_input.clear()
            self.chapter_input.addItems(manrev_settings.current_settings.get("capitoli", []))

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()

    def apply_theme(self):
        if self.app:
            try:
                import importlib
                qt_material = importlib.import_module("qt_material")
                apply_stylesheet = getattr(qt_material, "apply_stylesheet", None)
                if apply_stylesheet:
                    apply_stylesheet(self.app, theme="dark_teal.xml")
            except ImportError:
                # Il tema opzionale richiede qt-material, continua senza tema se non presente
                pass

    def closeEvent(self, event):
        self.save_form_state()
        self.closed.emit()
        event.accept()

    def load_form_state(self):
        """Carica i dati del form da file JSON (esclude descrizione)."""
        if not os.path.exists(self.state_path):
            return
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            return
        doc_type = state.get("doc_type")
        if doc_type:
            idx = self.doc_type.findText(doc_type)
            if idx != -1:
                self.doc_type.setCurrentIndex(idx)
        self.number_input.setText(state.get("number", ""))
        chapter = state.get("chapter", "")
        if chapter:
            if self.chapter_input.findText(chapter) == -1:
                self.chapter_input.addItem(chapter)
            idx = self.chapter_input.findText(chapter)
            if idx != -1:
                self.chapter_input.setCurrentIndex(idx)
        self.amount_input.setText(state.get("amount", ""))
        date_str = state.get("date")
        if date_str:
            parsed = QDate.fromString(date_str, "yyyy-MM-dd")
            if parsed.isValid():
                self.date_input.setDate(parsed)
        self.place_input.setText(state.get("place", self.place_input.text()))
        self.treasurer_input.setText(state.get("treasurer", self.treasurer_input.text()))
        self.president_input.setText(state.get("president", self.president_input.text()))
        self.accountant_input.setText(state.get("accountant", self.accountant_input.text()))
        self.print_check.setChecked(state.get("print_after", False))

    def save_form_state(self):
        """Salva i dati del form su file JSON (esclude descrizione)."""
        state = {
            "doc_type": self.doc_type.currentText(),
            "number": self.number_input.text(),
            "chapter": self.chapter_input.currentText(),
            "amount": self.amount_input.text(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "place": self.place_input.text(),
            "treasurer": self.treasurer_input.text(),
            "president": self.president_input.text(),
            "accountant": self.accountant_input.text(),
            "print_after": self.print_check.isChecked()
        }
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception:
            pass
