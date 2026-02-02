"""
Ana pencere bileşeni
"""
import tkinter as tk
import webbrowser
import ctypes
from .theme import ModernTheme
from .components import ModernLabel
from .panels import LeftPanel, RightPanel
from .dialogs import ToastNotification, FilterDialog


class MainWindow:
    """Modern ana pencere"""
    
    def __init__(self, arama_sistemi):
        self.arama_sistemi = arama_sistemi
        self.colors = ModernTheme.COLORS
        self.fonts = ModernTheme.FONTS
        
        # Ana pencere
        self.root = tk.Tk()
        self.root.title("Kalem Stok Arama")
        self.root.geometry("1200x850")
        self.root.minsize(1000, 700)
        self.root.configure(bg=self.colors['bg_primary'], highlightthickness=0, bd=0)
        
        # Windows'ta koyu başlık çubuğu
        self._set_dark_title_bar()
        
        # Tema stillerini uygula
        ModernTheme.apply_styles(self.root)
        
        # Değişkenler
        self.sonuc_df = None
        self.original_df = None
        self.sutun_filtreleri = {}
        
        # Arayüzü oluştur
        self._create_ui()
    
    def _set_dark_title_bar(self):
        """Windows'ta pencere başlık çubuğunu koyu yapar"""
        try:
            # Windows 10/11 için koyu mod
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value),
                ctypes.sizeof(value)
            )
            
            # Pencere başlık çubuğu rengini ayarla (Windows 11)
            # DWMWA_CAPTION_COLOR = 35
            DWMWA_CAPTION_COLOR = 35
            # #051c2c rengi BGR formatında: 0x2C1C05
            color = 0x2C1C05
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_CAPTION_COLOR,
                ctypes.byref(ctypes.c_int(color)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception as e:
            print(f"Title bar ayarlanamadı: {e}")
    
    def _create_ui(self):
        """Ana arayüzü oluştur"""
        # Ana container
        main = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Başlık
        self._create_header(main)
        
        # İçerik alanı
        content = tk.Frame(main, bg=self.colors['bg_primary'])
        content.pack(fill=tk.BOTH, expand=True, pady=(16, 0))
        
        # Callback'ler
        callbacks = {
            'datakalem_sec': self.datakalem_sec,
            'veri_sec': self.veri_sec,
            'arama_yap': self.arama_yap,
            'panoya_kopyala': self.panoya_kopyala,
            'temizle': self.temizle,
            'external_id': self.external_id_kopyala,
            'filtre_uygula': self.filtre_uygula,
            'filtreleri_temizle': self.filtreleri_temizle
        }
        
        # Sol panel
        self.left_panel = LeftPanel(content, callbacks)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16))
        
        # Sağ panel
        self.right_panel = RightPanel(content, self.sutun_filtresi_goster)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Durum çubuğu
        self._create_status_bar(main)
    
    def _create_header(self, parent):
        """Başlık bölümü"""
        header = tk.Frame(parent, bg=self.colors['bg_primary'])
        header.pack(fill=tk.X)
        
        # Sol taraf - Logo ve başlık
        left = tk.Frame(header, bg=self.colors['bg_primary'])
        left.pack(side=tk.LEFT)
        
        # İkon
        tk.Label(
            left,
            text="📦",
            font=('Segoe UI Emoji', 32),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_primary']
        ).pack(side=tk.LEFT, padx=(0, 12))
        
        # Başlıklar
        title_frame = tk.Frame(left, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT)
        
        ModernLabel(
            title_frame,
            text="Kalem Stok Arama",
            style="title",
            bg=self.colors['bg_primary']
        ).pack(anchor=tk.W)
        
        ModernLabel(
            title_frame,
            text="Hızlı ve kolay stok sorgulama sistemi",
            style="muted",
            bg=self.colors['bg_primary']
        ).pack(anchor=tk.W)
    
    def _create_status_bar(self, parent):
        """Durum çubuğu"""
        status = tk.Frame(
            parent,
            bg=self.colors['bg_secondary'],
            height=50,
            highlightthickness=0,
            bd=0
        )
        status.pack(fill=tk.X, pady=(16, 0))
        status.pack_propagate(False)
        
        content = tk.Frame(status, bg=self.colors['bg_secondary'])
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)
        
        # Sol - Durum
        left = tk.Frame(content, bg=self.colors['bg_secondary'])
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_icon = tk.Label(
            left,
            text="●",
            font=('Segoe UI', 12),
            fg=self.colors['success'],
            bg=self.colors['bg_secondary']
        )
        self.status_icon.pack(side=tk.LEFT, padx=(0, 8))
        
        self.status_label = tk.Label(
            left,
            text="Hazır",
            font=self.fonts['body'],
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Sağ - Credit
        credit = tk.Label(
            content,
            text="by ENES EREN",
            font=('Segoe UI', 9, 'underline'),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_secondary'],
            cursor='hand2'
        )
        credit.pack(side=tk.RIGHT)
        credit.bind("<Button-1>", lambda e: webbrowser.open("https://eneseren.com"))
        credit.bind("<Enter>", lambda e: credit.config(fg=self.colors['accent_secondary']))
        credit.bind("<Leave>", lambda e: credit.config(fg=self.colors['accent_primary']))
    
    def update_status(self, text, status="success"):
        """Durum çubuğunu güncelle"""
        colors = {
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['error'],
            'info': self.colors['info']
        }
        self.status_icon.config(fg=colors.get(status, colors['info']))
        self.status_label.config(text=text)
    
    def show_toast(self, message, title="Bilgi", style="success"):
        """Toast bildirimi göster"""
        ToastNotification(self.root, message, title, style)
    
    # ===== Dosya İşlemleri =====
    
    def datakalem_sec(self):
        """DataKalem dosyası seç"""
        from tkinter import filedialog
        import os
        
        dosya = filedialog.askopenfilename(
            title="Kalem Stok Dosyasını Seçin",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if dosya:
            self.arama_sistemi.datakalem_excel_path = dosya
            boyut = os.path.getsize(dosya)
            boyut_str = f"{boyut/(1024*1024):.1f} MB" if boyut >= 1024*1024 else f"{boyut/1024:.1f} KB"
            
            self.left_panel.update_datakalem_label(
                f"✓ {os.path.basename(dosya)[:18]}... ({boyut_str})", True
            )
            self.update_status("Kalem stok dosyası seçildi", "success")
    
    def veri_sec(self):
        """Veri dosyası seç"""
        from tkinter import filedialog
        import os
        
        dosya = filedialog.askopenfilename(
            title="Veri Dosyasını Seçin",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if dosya:
            self.arama_sistemi.veri_excel_path = dosya
            boyut = os.path.getsize(dosya)
            boyut_str = f"{boyut/(1024*1024):.1f} MB" if boyut >= 1024*1024 else f"{boyut/1024:.1f} KB"
            
            self.left_panel.update_veri_label(
                f"✓ {os.path.basename(dosya)[:18]}... ({boyut_str})", True
            )
            self.update_status("Veri dosyası seçildi", "success")
    
    # ===== Arama İşlemleri =====
    
    def arama_yap(self):
        """Arama işlemi başlat"""
        from tkinter import messagebox
        import threading
        
        if not self.arama_sistemi.datakalem_excel_path or not self.arama_sistemi.veri_excel_path:
            messagebox.showwarning("Uyarı", "Önce her iki dosyayı da seçin!")
            return
        
        self.update_status("Dosyalar yükleniyor...", "warning")
        self.root.update()
        
        def yukle_ve_ara():
            try:
                self.root.after(0, lambda: self.update_status("DataKalem yükleniyor...", "warning"))
                
                if not self.arama_sistemi.datakalem_excel_yukle_with_progress(
                    self.arama_sistemi.datakalem_excel_path
                ):
                    self.root.after(0, lambda: self.update_status("DataKalem yüklenemedi!", "error"))
                    return
                
                self.root.after(0, lambda: self.update_status("Veri dosyası yükleniyor...", "warning"))
                
                if not self.arama_sistemi.veri_excel_yukle_with_progress(
                    self.arama_sistemi.veri_excel_path
                ):
                    self.root.after(0, lambda: self.update_status("Veri dosyası yüklenemedi!", "error"))
                    return
                
                self.root.after(0, lambda: self.update_status("Arama yapılıyor...", "warning"))
                
                sonuc = self.arama_sistemi.sonuc_tablosu_olustur()
                self.root.after(0, lambda: self._arama_tamamlandi(sonuc))
                
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Hata: {str(e)}", "error"))
        
        threading.Thread(target=yukle_ve_ara, daemon=True).start()
    
    def _arama_tamamlandi(self, sonuc_df):
        """Arama tamamlandığında çağrılır"""
        if sonuc_df is not None:
            self.sonuc_df = sonuc_df
            self.original_df = sonuc_df.copy()
            self.sutun_filtreleri = {}
            self.right_panel.show_data(sonuc_df)
            
            bulunan = len(sonuc_df[sonuc_df['KALEM'] != 'BULUNAMADI'])
            self.update_status(f"Arama tamamlandı: {bulunan} eşleşme bulundu", "success")
        else:
            self.update_status("Arama yapılamadı", "error")
    
    # ===== Kopyalama ve Temizleme =====
    
    def panoya_kopyala(self):
        """Tabloyu panoya kopyala"""
        from tkinter import messagebox
        import pandas as pd
        
        if self.sonuc_df is None or self.sonuc_df.empty:
            messagebox.showwarning("Uyarı", "Önce arama yapın!")
            return
        
        try:
            headers = list(self.sonuc_df.columns)
            header_line = '\t'.join(headers)
            
            data_lines = []
            for _, row in self.sonuc_df.iterrows():
                row_data = [str(row[col]) if pd.notna(row[col]) else "" for col in headers]
                data_lines.append('\t'.join(row_data))
            
            clipboard_text = '\n'.join([header_line] + data_lines)
            
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)
            self.root.update()
            
            self.update_status(f"Panoya kopyalandı ({len(self.sonuc_df)} satır)", "success")
            self.show_toast(f"{len(self.sonuc_df)} satır kopyalandı", "Panoya Kopyalandı", "success")
            
        except Exception as e:
            self.update_status("Kopyalama hatası!", "error")
    
    def temizle(self):
        """Tüm verileri temizle"""
        self.right_panel.clear()
        self.left_panel.clear_filter()
        self.left_panel.reset_labels()
        
        from excel_seri_arama import ExcelSeriArama
        self.arama_sistemi = ExcelSeriArama()
        self.sonuc_df = None
        self.original_df = None
        self.sutun_filtreleri = {}
        
        self.update_status("Temizlendi - Yeni arama için hazır", "success")
        self.show_toast("Tüm veriler temizlendi", "Temizlendi", "success")
    
    def external_id_kopyala(self):
        """ExternalID kopyala"""
        import datetime
        
        simdi = datetime.datetime.now()
        external_id = simdi.strftime("%Y%m%d%H%M")
        
        self.root.clipboard_clear()
        self.root.clipboard_append(external_id)
        self.root.update()
        
        formatted = simdi.strftime("%d.%m.%Y %H:%M")
        self.update_status(f"ExternalID kopyalandı: {external_id}", "success")
        self.show_toast(f"ExternalID: {external_id}\n({formatted})", "Kopyalandı", "success")
    
    # ===== Filtreleme =====
    
    def filtre_uygula(self, event=None):
        """Genel filtreyi uygula"""
        self._tum_filtreleri_uygula()
    
    def filtreleri_temizle(self):
        """Tüm filtreleri temizle"""
        self.left_panel.clear_filter()
        self.sutun_filtreleri = {}
        
        if self.original_df is not None:
            self.sonuc_df = self.original_df.copy()
            self.right_panel.show_data(self.sonuc_df)
            self.update_status(f"Filtreler temizlendi: {len(self.sonuc_df)} sonuç", "success")
    
    def sutun_filtresi_goster(self, sutun_adi):
        """Sütun filtresini göster"""
        if self.original_df is None:
            return
        
        degerler = self.original_df[sutun_adi].astype(str).unique()
        degerler = sorted([d for d in degerler if d != 'nan'])
        
        secili = self.sutun_filtreleri.get(sutun_adi)
        
        def on_apply(selected):
            if selected:
                self.sutun_filtreleri[sutun_adi] = selected
            elif sutun_adi in self.sutun_filtreleri:
                del self.sutun_filtreleri[sutun_adi]
            self._tum_filtreleri_uygula()
        
        FilterDialog(self.root, sutun_adi, degerler, secili, on_apply)
    
    def _tum_filtreleri_uygula(self):
        """Tüm filtreleri uygula"""
        if self.original_df is None:
            return
        
        filtered = self.original_df.copy()
        
        # Sütun filtreleri
        for sutun, degerler in self.sutun_filtreleri.items():
            filtered = filtered[filtered[sutun].astype(str).isin(degerler)]
        
        # Genel filtre
        genel = self.left_panel.get_filter_text().lower()
        if genel:
            filtered = filtered[
                filtered.astype(str).apply(
                    lambda row: any(genel in str(cell).lower() for cell in row), axis=1
                )
            ]
        
        self.sonuc_df = filtered
        self.right_panel.show_data(filtered)
        
        filtre_sayisi = len(self.sutun_filtreleri)
        if filtre_sayisi > 0 or genel:
            self.update_status(f"Filtre uygulandı: {len(filtered)} sonuç", "info")
        else:
            self.update_status(f"Toplam: {len(filtered)} sonuç", "success")
    
    def run(self):
        """Uygulamayı başlat"""
        self.root.mainloop()

