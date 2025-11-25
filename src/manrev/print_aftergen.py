import os
import platform
import subprocess
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QHBoxLayout

class PrinterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Stampante")
        self.setFixedSize(300, 150)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Lista stampanti
        self.printer_combo = QComboBox()
        self.printer_combo.addItems(self.get_printers())
        
        layout.addWidget(QLabel("Seleziona stampante:"))
        layout.addWidget(self.printer_combo)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        print_btn = QPushButton("Stampa")
        print_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(print_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_printers(self):
        if platform.system() == "Windows":
            import win32print
            printers = []
            for printer in win32print.EnumPrinters(2):
                printers.append(printer[2])
            return printers
        elif platform.system() == "Darwin":  # macOS
            try:
                output = subprocess.check_output(['lpstat', '-p'], universal_newlines=True)
                printers = []
                for line in output.split('\n'):
                    if line.startswith('printer'):
                        printers.append(line.split(' ')[1])
                return printers or ["Stampante Predefinita"]
            except:
                return ["Stampante Predefinita"]
        return ["Stampante Predefinita"]
    
    def selected_printer(self):
        return self.printer_combo.currentText()

class PrintManager:
    def __init__(self):
        self.word_app = None
        
    def print_document(self, file_path, parent=None):
        """Stampa un documento Word"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File non trovato: {file_path}")
            
            # Mostra dialog selezione stampante
            printer_dialog = PrinterDialog(parent)
            if printer_dialog.exec_() != QDialog.Accepted:
                return False
                
            selected_printer = printer_dialog.selected_printer()
            
            if platform.system() == "Windows":
                return self._print_windows(file_path, selected_printer)
            elif platform.system() == "Darwin":
                return self._print_macos(file_path, selected_printer)
            else:
                raise NotImplementedError("Sistema operativo non supportato")
                
        except Exception as e:
            QMessageBox.critical(
                parent,
                "Errore di stampa",
                f"Errore durante la stampa: {str(e)}"
            )
            return False
            
        finally:
            if self.word_app:
                try:
                    self.word_app.Quit()
                except:
                    pass
                self.word_app = None
                
    def _print_windows(self, file_path, printer):
        """Gestisce la stampa su Windows"""
        import win32com.client
        
        self.word_app = win32com.client.Dispatch("Word.Application")
        self.word_app.Visible = False
        
        doc = self.word_app.Documents.Open(os.path.abspath(file_path))
        self.word_app.ActivePrinter = printer
        doc.PrintOut(Background=False)
        doc.Close()
        
        return True
        
    def _print_macos(self, file_path, printer):
        """Gestisce la stampa su macOS"""
        try:
            if printer != "Stampante Predefinita":
                cmd = ['lp', '-d', printer, file_path]
            else:
                cmd = ['lp', file_path]
                
            subprocess.run(cmd, check=True)
            return True
        except:
            return False

# Istanza singleton del gestore stampe
print_manager = PrintManager()

def print_after_generation(file_path, parent=None):
    """Funzione wrapper per la stampa dopo la generazione"""
    return print_manager.print_document(file_path, parent) 