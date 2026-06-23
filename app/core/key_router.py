import os

class APIKeyRouter:
    def __init__(self, keys_string):
        """
        Inisialisasi Key Router.
        keys_string: String berisi daftar API key dipisahkan dengan koma.
        """
        self.keys = []
        if keys_string:
            # Bersihkan spasi kosong
            self.keys = [k.strip() for k in keys_string.split(',') if k.strip()]
            
        self.current_index = 0
        self.dead_keys = set()
        
    def get_key(self):
        """
        Mengambil kunci aktif yang masih berfungsi.
        """
        if not self.keys:
            return None
            
        # Cari kunci yang belum mati, mulai dari index saat ini
        start_index = self.current_index
        while True:
            key = self.keys[self.current_index]
            if key not in self.dead_keys:
                return key
                
            self.current_index = (self.current_index + 1) % len(self.keys)
            if self.current_index == start_index:
                # Semua kunci sudah dicoba dan mati
                return None
                
    def mark_dead(self, key):
        """
        Menandai sebuah kunci sebagai mati (misal karena Error 429 atau kuota habis).
        """
        print(f"⚠️ [Key Router] API Key mati/limit ditandai: ...{key[-4:] if key else 'None'}")
        self.dead_keys.add(key)
        # Otomatis geser ke kunci berikutnya
        if self.keys:
            self.current_index = (self.current_index + 1) % len(self.keys)
            
    def has_active_keys(self):
        return len(self.dead_keys) < len(self.keys)
