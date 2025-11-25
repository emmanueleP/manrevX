from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from .settings import manrev_settings
from .layout_man_rev import DocumentLayout

def number_to_words_it(number):
    """Converte un numero in parole in italiano"""
    
    # Dizionari di conversione
    unita = {
        0: "", 1: "uno", 2: "due", 3: "tre", 4: "quattro", 5: "cinque",
        6: "sei", 7: "sette", 8: "otto", 9: "nove", 10: "dieci",
        11: "undici", 12: "dodici", 13: "tredici", 14: "quattordici",
        15: "quindici", 16: "sedici", 17: "diciassette", 18: "diciotto",
        19: "diciannove"
    }
    
    decine = {
        2: "venti", 3: "trenta", 4: "quaranta", 5: "cinquanta",
        6: "sessanta", 7: "settanta", 8: "ottanta", 9: "novanta"
    }
    
    def converti_decine(n):
        if n <= 19:
            return unita.get(n, str(n))
        
        d = n // 10
        u = n % 10
        
        if d not in decine:
            return str(n)
        
        if u == 0:
            return decine[d]
        elif u == 1 or u == 8:
            return decine[d][:-1] + unita[u]
        else:
            return decine[d] + unita[u]
    
    def converti_centinaia(n):
        c = n // 100
        r = n % 100
        
        if c == 0:
            return converti_decine(r)
        elif c == 1:
            return "cento" + converti_decine(r)
        else:
            return unita[c] + "cento" + converti_decine(r)
    
    def converti_migliaia(n):
        k = n // 1000
        r = n % 1000
        
        if k == 0:
            return converti_centinaia(r)
        elif k == 1:
            return "mille" + converti_centinaia(r)
        else:
            return converti_decine(k) + "mila" + converti_centinaia(r)
    
    try:
        # Gestione input non valido
        try:
            number = float(str(number).replace(',', '.').strip())
        except:
            return f"{number} euro"
        
        # Separazione parte intera e decimale
        int_part = int(abs(number))
        dec_part = int(round((abs(number) - int_part) * 100))
        
        # Caso zero
        if int_part == 0 and dec_part == 0:
            return "zero euro"
        
        result = []
        
        # Parte intera
        if int_part > 0:
            if int_part > 99999:
                result.append(str(int_part))
            else:
                result.append(converti_migliaia(int_part))
            result.append("euro")
        
        # Decimali
        if dec_part > 0:
            if result:
                result.append("e")
            if dec_part < 10:
                result.append("zero")
            result.append(str(dec_part))
            result.append("centesimi")
        
        return " ".join(result)
        
    except Exception as e:
        print(f"Errore nella conversione del numero {number}: {str(e)}")
        return f"{number} euro"

def generate_documents(data, output_file, print_after=False):
    """Genera il documento mandato/reversale"""
    try:
        # Crea il documento
        doc = Document()
        layout = DocumentLayout(doc)
        
        # Imposta layout base
        layout.set_margins()
        
        # Aggiungi intestazione
        layout.add_header(data['Tipo'], data['anno'], data['Numero'])
        
        # Aggiungi dettagli
        details = {
            'Capitolo': data['Capitolo'],
            'Importo': data['Importo in €'],
            'Descrizione': data['Descrizione del pagamento']
        }
        layout.add_details_table(details)
        
        # Converti e aggiungi importo in lettere
        importo_str = str(data['Importo in €'])
        importo_numerico = float(importo_str.replace(',', '.'))
        importo_in_lettere = number_to_words_it(importo_numerico)
        layout.add_amount_text(importo_in_lettere)
        
        # Aggiungi firme
        signatures = {
            'Il Tesoriere': data['Il Tesoriere'],
            'Il Presidente': data['Il Presidente'],
            "L'Addetto Contabile": data["L'Addetto Contabile"]
        }
        layout.add_signatures(signatures)
        
        # Aggiungi piè di pagina
        layout.add_footer(data['Luogo'], data['Data'])
        
        # Crea la directory se non esiste
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Salva il documento
        doc.save(output_file)
        
        return output_file
        
    except Exception as e:
        raise Exception(f"Errore nella generazione del documento: {str(e)}")

def prepare_document_data(gui):
    """Prepara i dati dal form per la generazione del documento"""
    try:
        data = {
            "Tipo": gui.doc_type.currentText(),
            "Numero": gui.number_input.text(),
            "Capitolo": gui.chapter_input.currentText(),
            "Importo in €": gui.amount_input.text(),
            "Descrizione del pagamento": gui.description_input.toPlainText(),
            "Data": gui.date_input.date().toString("dd/MM/yyyy"),
            "anno": gui.date_input.date().toString("yyyy"),
            "Luogo": gui.place_input.text(),
            "Il Tesoriere": gui.treasurer_input.text(),
            "Il Presidente": gui.president_input.text(),
            "L'Addetto Contabile": gui.accountant_input.text()
        }
        
        # Validazione
        required_fields = ["Numero", "Capitolo", "Importo in €", "Descrizione del pagamento"]
        if not all(data[field] for field in required_fields):
            raise ValueError("Tutti i campi obbligatori devono essere compilati")
            
        return data
        
    except Exception as e:
        raise ValueError(f"Errore nella preparazione dei dati: {str(e)}")

def generate_document(gui):
    """Gestisce il processo di generazione del documento"""
    try:
        # Prepara i dati
        data = prepare_document_data(gui)
        
        # Genera il nome del file
        default_name = f"{data['Tipo']}_{data['Numero']}_{data['Data'].replace('/', '-')}.docx"
        
        # Richiedi il percorso di salvataggio
        file_path, _ = QFileDialog.getSaveFileName(
            gui,
            "Salva Documento",
            os.path.join(manrev_settings.current_settings.get("last_directory", ""), default_name),
            "Documenti Word (*.docx)"
        )
        
        if file_path:
            # Aggiorna last_directory
            manrev_settings.current_settings["last_directory"] = os.path.dirname(file_path)
            manrev_settings.save_settings()
            
            # Genera il documento
            generate_documents(data, file_path, print_after=gui.print_check.isChecked())
            
            QMessageBox.information(
                gui,
                "Successo",
                "Documento generato con successo!"
            )
            
    except ValueError as e:
        QMessageBox.warning(
            gui,
            "Attenzione",
            str(e)
        )
    except Exception as e:
        QMessageBox.critical(
            gui,
            "Errore",
            f"Errore nella generazione del documento: {str(e)}"
        )