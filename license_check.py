"""
License Check - GitHub Tabanlı Uygulama Kontrolü
Uygulama her başlatıldığında GitHub'daki lisans dosyasını kontrol eder.
"""
import urllib.request
import urllib.error
import ssl
import json
import tkinter as tk
from tkinter import messagebox
import sys
import hashlib
import datetime


class LicenseChecker:
    """GitHub tabanlı lisans kontrolü"""
    
    # GitHub Raw URL - Bu URL'yi kendi repo'nuza göre değiştirin
    # Format: https://raw.githubusercontent.com/KULLANICI/REPO/BRANCH/license_status.json
    LICENSE_URL = "https://raw.githubusercontent.com/KULLANICI_ADI/REPO_ADI/main/license_status.json"
    
    # Yedek URL (Gist kullanımı için)
    BACKUP_URL = None
    
    # Timeout süresi (saniye)
    TIMEOUT = 10
    
    # Offline mod izni (True ise internet yoksa da çalışır - güvenlik düşük)
    ALLOW_OFFLINE = False
    
    @classmethod
    def set_license_url(cls, url):
        """Lisans URL'sini ayarlar"""
        cls.LICENSE_URL = url
    
    @classmethod
    def check_license(cls):
        """
        Lisans kontrolü yapar.
        Returns: (bool, str) - (geçerli mi, mesaj)
        """
        try:
            # SSL context oluştur
            context = ssl.create_default_context()
            
            # GitHub'dan lisans dosyasını oku
            request = urllib.request.Request(
                cls.LICENSE_URL,
                headers={
                    'User-Agent': 'KalemStokApp/1.0',
                    'Cache-Control': 'no-cache'
                }
            )
            
            with urllib.request.urlopen(request, timeout=cls.TIMEOUT, context=context) as response:
                content = response.read().decode('utf-8')
                
                # JSON parse
                try:
                    data = json.loads(content)
                    
                    # Status kontrolü
                    status = data.get('status', '').upper()
                    message = data.get('message', '')
                    
                    # Tarih kontrolü (opsiyonel)
                    expiry_date = data.get('expiry_date')
                    if expiry_date:
                        expiry = datetime.datetime.strptime(expiry_date, '%Y-%m-%d')
                        if datetime.datetime.now() > expiry:
                            return False, "Lisans süresi dolmuş!"
                    
                    if status == 'ACTIVE':
                        return True, message or "Lisans geçerli"
                    elif status == 'DISABLED':
                        return False, message or "Uygulama devre dışı bırakıldı!"
                    elif status == 'MAINTENANCE':
                        return False, message or "Uygulama bakımda!"
                    else:
                        return False, message or "Geçersiz lisans durumu!"
                        
                except json.JSONDecodeError:
                    # Basit text kontrolü (sadece "ACTIVE" yazıyorsa)
                    if content.strip().upper() == 'ACTIVE':
                        return True, "Lisans geçerli"
                    else:
                        return False, "Lisans geçersiz!"
                        
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False, "Lisans dosyası bulunamadı! Repo kaldırılmış olabilir."
            elif e.code == 403:
                return False, "Lisans erişimi engellendi!"
            else:
                return False, f"Lisans kontrolü başarısız! HTTP {e.code}"
                
        except urllib.error.URLError as e:
            if cls.ALLOW_OFFLINE:
                return True, "Offline mod - İnternet bağlantısı yok"
            return False, f"İnternet bağlantısı yok veya sunucuya ulaşılamıyor!"
            
        except Exception as e:
            if cls.ALLOW_OFFLINE:
                return True, "Offline mod - Kontrol başarısız"
            return False, f"Lisans kontrolü hatası: {str(e)}"
    
    # Geliştirici bilgileri
    DEVELOPER_NAME = "Enes EREN"
    DEVELOPER_WEBSITE = "https://eneseren.com"  # Web sitenizi buraya yazın
    
    @classmethod
    def open_website(cls):
        """Geliştirici web sitesini açar"""
        import webbrowser
        webbrowser.open(cls.DEVELOPER_WEBSITE)
    
    @classmethod
    def show_error_and_exit(cls, message):
        """Hata mesajı göster ve uygulamayı kapat"""
        root = tk.Tk()
        root.withdraw()  # Ana pencereyi gizle
        
        # Özel hata penceresi
        error_window = tk.Toplevel(root)
        error_window.title("Uygulama Başlatılamadı")
        error_window.geometry("400x220")
        error_window.resizable(False, False)
        error_window.configure(bg='#051c2c')
        
        # Pencereyi ortala
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() - 400) // 2
        y = (error_window.winfo_screenheight() - 220) // 2
        error_window.geometry(f"+{x}+{y}")
        
        # İkon (varsa)
        try:
            error_window.iconbitmap('favicon.ico')
        except:
            pass
        
        # Ana frame
        main_frame = tk.Frame(error_window, bg='#051c2c')
        main_frame.pack(expand=True, fill='both')
        
        # İçerik frame
        content_frame = tk.Frame(main_frame, bg='#051c2c')
        content_frame.pack(expand=True, fill='both', padx=30, pady=15)
        
        icon_label = tk.Label(
            content_frame, 
            text="⚠️", 
            font=('Segoe UI Emoji', 36),
            bg='#051c2c',
            fg='#ff4444'
        )
        icon_label.pack(pady=(0, 8))
        
        title_label = tk.Label(
            content_frame,
            text="Uygulama Başlatılamıyor",
            font=('Segoe UI', 14, 'bold'),
            bg='#051c2c',
            fg='#ffffff'
        )
        title_label.pack(pady=(0, 15))
        
        # Kapat butonu
        close_btn = tk.Button(
            content_frame,
            text="Kapat",
            font=('Segoe UI', 10),
            bg='#ff4444',
            fg='white',
            activebackground='#cc0000',
            activeforeground='white',
            relief='flat',
            padx=30,
            pady=5,
            cursor='hand2',
            command=lambda: sys.exit(1)
        )
        close_btn.pack(pady=(0, 10))
        
        # Geliştirici linki - küçük ve en altta
        developer_link = tk.Label(
            error_window,
            text=cls.DEVELOPER_NAME,
            font=('Segoe UI', 8),
            bg='#051c2c',
            fg='#555555',
            cursor='hand2'
        )
        developer_link.pack(side='bottom', pady=(0, 8))
        developer_link.bind("<Button-1>", lambda e: cls.open_website())
        developer_link.bind("<Enter>", lambda e: developer_link.config(fg='#79d84b'))
        developer_link.bind("<Leave>", lambda e: developer_link.config(fg='#555555'))
        
        # Pencere kapatma işlemi
        error_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(1))
        
        # Modal yap
        error_window.grab_set()
        error_window.focus_set()
        
        root.mainloop()
        sys.exit(1)
    
    @classmethod
    def verify_and_run(cls, app_starter_func):
        """
        Lisansı doğrula ve uygulamayı başlat.
        
        Args:
            app_starter_func: Lisans geçerliyse çalıştırılacak fonksiyon
        """
        is_valid, message = cls.check_license()
        
        if is_valid:
            print(f"✓ Lisans kontrolü başarılı: {message}")
            app_starter_func()
        else:
            print(f"✗ Lisans kontrolü başarısız: {message}")
            cls.show_error_and_exit(message)


def check_and_run(app_func, license_url=None):
    """
    Kolay kullanım için wrapper fonksiyon.
    
    Args:
        app_func: Uygulamayı başlatan fonksiyon
        license_url: GitHub raw URL (opsiyonel)
    """
    if license_url:
        LicenseChecker.set_license_url(license_url)
    
    LicenseChecker.verify_and_run(app_func)


# Test için
if __name__ == "__main__":
    def test_app():
        print("Uygulama başlatıldı!")
        root = tk.Tk()
        root.title("Test App")
        tk.Label(root, text="Uygulama çalışıyor!").pack(padx=50, pady=50)
        root.mainloop()
    
    # Test (bu URL'yi değiştirin)
    check_and_run(test_app)

