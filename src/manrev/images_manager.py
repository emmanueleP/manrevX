import os
from PIL import Image
from io import BytesIO
import base64
from .settings import manrev_settings

class ImagesManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.images_dir = os.path.join(self.base_dir, 'data', 'images', 'manrev')
        self.ensure_directories()
        
    def ensure_directories(self):
        """Assicura che esistano le directory necessarie"""
        directories = [
            os.path.join(self.images_dir, 'firme'),
            os.path.join(self.images_dir, 'timbri'),
            os.path.join(self.images_dir, 'loghi')
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_signature_path(self, signature_type):
        """Ottiene il percorso dell'immagine della firma"""
        signatures = {
            'tesoriere': manrev_settings.current_settings['firme']['tesoriere_firma'],
            'presidente': manrev_settings.current_settings['firme']['presidente_firma'],
            'addetto': manrev_settings.current_settings['firme']['addetto_firma']
        }
        
        signature_path = signatures.get(signature_type)
        if signature_path and os.path.exists(signature_path):
            return signature_path
        return None
    
    def get_stamp_path(self):
        """Ottiene il percorso del timbro"""
        stamp_path = os.path.join(self.images_dir, 'timbri', 'timbro.png')
        if os.path.exists(stamp_path):
            return stamp_path
        return None
    
    def get_logo_path(self):
        """Ottiene il percorso del logo"""
        logo_path = os.path.join(self.images_dir, 'loghi', 'logo.png')
        if os.path.exists(logo_path):
            return logo_path
        return None
    
    def save_signature(self, signature_type, image_path):
        """Salva una nuova firma"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File non trovato: {image_path}")
            
        # Crea il nome del file
        filename = f"firma_{signature_type}.png"
        destination = os.path.join(self.images_dir, 'firme', filename)
        
        # Copia e ottimizza l'immagine
        self._optimize_and_save_image(image_path, destination)
        
        # Aggiorna le impostazioni
        manrev_settings.current_settings['firme'][f'{signature_type}_firma'] = destination
        manrev_settings.save_settings()
        
        return destination
    
    def save_stamp(self, image_path):
        """Salva un nuovo timbro"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File non trovato: {image_path}")
            
        destination = os.path.join(self.images_dir, 'timbri', 'timbro.png')
        self._optimize_and_save_image(image_path, destination)
        return destination
    
    def save_logo(self, image_path):
        """Salva un nuovo logo"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File non trovato: {image_path}")
            
        destination = os.path.join(self.images_dir, 'loghi', 'logo.png')
        self._optimize_and_save_image(image_path, destination)
        return destination
    
    def _optimize_and_save_image(self, source_path, destination_path):
        """Ottimizza e salva l'immagine"""
        try:
            with Image.open(source_path) as img:
                # Converti in RGBA se necessario
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Ridimensiona se troppo grande
                max_size = (800, 800)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Salva con ottimizzazione
                img.save(destination_path, 'PNG', optimize=True)
        except Exception as e:
            raise Exception(f"Errore nel processare l'immagine: {str(e)}")
    
    def get_all_signatures(self):
        """Restituisce tutte le firme configurate"""
        signatures = {}
        for sig_type in ['tesoriere', 'presidente', 'addetto']:
            path = self.get_signature_path(sig_type)
            if path:
                signatures[sig_type] = path
        return signatures
    
    def encode_image_base64(self, image_path):
        """Converte un'immagine in base64"""
        if not image_path or not os.path.exists(image_path):
            return None
            
        try:
            with open(image_path, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return None
    
    def decode_image_base64(self, base64_string):
        """Converte una stringa base64 in immagine"""
        try:
            image_data = base64.b64decode(base64_string)
            return BytesIO(image_data)
        except Exception:
            return None
    
    def clear_all_images(self):
        """Rimuove tutte le immagini salvate"""
        try:
            for directory in ['firme', 'timbri', 'loghi']:
                dir_path = os.path.join(self.images_dir, directory)
                for file in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            
            # Reset delle impostazioni delle firme
            manrev_settings.current_settings['firme'] = {
                'tesoriere_firma': '',
                'presidente_firma': '',
                'addetto_firma': ''
            }
            manrev_settings.save_settings()
            
            return True
        except Exception:
            return False

# Istanza singleton del gestore immagini
images_manager = ImagesManager() 