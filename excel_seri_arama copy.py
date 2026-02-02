import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import os
import xml.etree.ElementTree as ET
from lxml import etree
import webbrowser
import threading
import time
import datetime

class ExcelSeriArama:
    def __init__(self):
        self.veri_excel_path = None
        self.datakalem_excel_path = None
        self.veri_df = None
        self.datakalem_df = None
        self.seri_sutun_index = None

    def log_mesaj(self, mesaj):
        """Debug log mesajı yazdırır"""
        zaman = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{zaman}] {mesaj}")

    def veri_temizle(self, deger):
        """Veriyi temizler - ondalık kısmı kaldırır ve string'e çevirir"""
        if pd.isna(deger) or deger is None:
            return ""

        # Sayı ise ondalık kısmı kaldır
        if isinstance(deger, (int, float)):
            if isinstance(deger, float) and deger.is_integer():
                return str(int(deger))
            elif isinstance(deger, float):
                return str(int(deger))  # Ondalık kısmı tamamen kaldır
            else:
                return str(deger)

        # String ise ondalık varsa kaldır
        deger_str = str(deger).strip()
        if '.' in deger_str:
            try:
                # Sayısal string ise ondalık kısmı kaldır
                num = float(deger_str)
                return str(int(num))
            except:
                # Sayısal değilse olduğu gibi döndür
                return deger_str

        return deger_str

    def seri_numara_sutunu_tespit(self, df):
        """Seri numarası sütununu otomatik tespit eder"""
        # Önce tam eşleşmeleri ara (daha spesifik olanlar önce)
        tam_eslesme_isimleri = [
            'SERİ NO', 'SERİ NUMARA', 'SERİ NUMARASI', 'SERIAL NUMBER', 'SERIAL NO', 'SN'
        ]

        # TAM EŞLEŞME: Sütun adı tam olarak bu kelimelerden biri mi?
        for col_index, col_name in enumerate(df.columns):
            col_name_upper = str(col_name).upper().strip()
            if col_name_upper in tam_eslesme_isimleri:
                return col_index

        # BAŞLANGIC EŞLEŞME: Sütun adı bu kelimelerle başlıyor mu?
        baslangic_isimleri = ['SERİ NO', 'SERİ NUMARA', 'SERIAL NUMBER', 'SERIAL NO']
        for col_index, col_name in enumerate(df.columns):
            col_name_upper = str(col_name).upper().strip()
            for baslagic_isim in baslangic_isimleri:
                if col_name_upper.startswith(baslagic_isim):
                    return col_index

        # IÇERIR EŞLEŞME: Sütun adında bu kelimeler geçiyor mu? (En az öncelik)
        icerir_isimleri = ['SERİ', 'SERIAL', 'NUMARA']
        for col_index, col_name in enumerate(df.columns):
            col_name_upper = str(col_name).upper().strip()
            for icerir_isim in icerir_isimleri:
                if icerir_isim in col_name_upper:
                    return col_index

        return None

    def excel_oku(self, dosya_yolu, sheet_name=0):
        """Excel dosyasını okur - tüm formatları destekler"""
        try:
            print(f"Excel dosyası okunuyor: {os.path.basename(dosya_yolu)}")

            # Önce dosyanın formatını kontrol et
            with open(dosya_yolu, 'rb') as f:
                first_bytes = f.read(1000)

            # Excel 2003 XML formatı mı kontrol et
            if b'<?xml' in first_bytes and b'xmlns:ss=' in first_bytes:
                print("Excel 2003 XML formatı tespit edildi, özel XML okuma yapılıyor...")
                return self.excel_xml_oku(dosya_yolu)

            # Standart Excel dosya formatları için deneme sırası
            engines_to_try = []

            if dosya_yolu.lower().endswith('.xlsx'):
                engines_to_try = ['openpyxl', 'xlrd']
            elif dosya_yolu.lower().endswith('.xls'):
                engines_to_try = ['xlrd', 'openpyxl']
            else:
                engines_to_try = ['openpyxl', 'xlrd']

            # Her engine'i sırayla dene
            for engine in engines_to_try:
                try:
                    print(f"{engine} engine deneniyor...")
                    df = pd.read_excel(dosya_yolu, sheet_name=sheet_name, engine=engine)
                    print(f"Başarılı ({engine}): {df.shape}")
                    return df
                except Exception as e:
                    print(f"{engine} engine başarısız: {str(e)}")
                    continue

            # Hiçbiri çalışmazsa engine belirtmeden dene
            try:
                print("Varsayılan engine deneniyor...")
                df = pd.read_excel(dosya_yolu, sheet_name=sheet_name)
                print(f"Varsayılan engine ile başarılı: {df.shape}")
                return df
            except Exception as e:
                print(f"Varsayılan engine de başarısız: {str(e)}")
                return None

        except Exception as e:
            print(f"Dosya okuma hatası: {str(e)}")
            return None

    def excel_xml_oku(self, dosya_yolu):
        """Excel 2003 XML formatını okur"""
        try:
            import xml.etree.ElementTree as ET

            # XML dosyasını parse et
            tree = ET.parse(dosya_yolu)
            root = tree.getroot()

            # Namespace'leri belirle
            namespaces = {
                'ss': 'urn:schemas-microsoft-com:office:spreadsheet'
            }

            # İlk worksheet'i bul
            worksheet = root.find('.//ss:Worksheet', namespaces)
            if worksheet is None:
                print("XML'de worksheet bulunamadı")
                return None

            # Table'ı bul
            table = worksheet.find('.//ss:Table', namespaces)
            if table is None:
                print("XML'de table bulunamadı")
                return None

            # Satırları oku
            rows = table.findall('.//ss:Row', namespaces)
            data = []

            for row in rows:
                row_data = []
                cells = row.findall('.//ss:Cell', namespaces)

                for cell in cells:
                    data_elem = cell.find('.//ss:Data', namespaces)
                    if data_elem is not None:
                        row_data.append(data_elem.text if data_elem.text else "")
                    else:
                        row_data.append("")

                if row_data:  # Boş satırları atla
                    data.append(row_data)

            if not data:
                print("XML'de veri bulunamadı")
                return None

            # DataFrame oluştur
            # İlk satırı header olarak kullan
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
            else:
                df = pd.DataFrame(data)

            print(f"XML başarılı: {df.shape}")
            return df

        except Exception as e:
            print(f"XML okuma hatası: {str(e)}")
            # XML okuma başarısız olursa, dosyayı CSV gibi okumaya çalış
            try:
                print("XML başarısız, CSV formatında deneniyor...")
                df = pd.read_csv(dosya_yolu, sep='\t', encoding='utf-8')
                print(f"CSV formatında başarılı: {df.shape}")
                return df
            except Exception as e2:
                print(f"CSV formatında da başarısız: {str(e2)}")
                return None

    def vlookup_arama_optimized(self, aranan_deger, lookup_dict, donus_sutun_index):
        """Optimized VLOOKUP benzeri arama fonksiyonu"""
        try:
            aranan_deger = self.veri_temizle(aranan_deger)

            if aranan_deger in lookup_dict:
                row_data = lookup_dict[aranan_deger]
                if donus_sutun_index < len(row_data):
                    return self.veri_temizle(row_data[donus_sutun_index])

            return "BULUNAMADI"
        except Exception as e:
            return f"HATA: {str(e)}"

    def datakalem_lookup_dict_olustur(self):
        """DataKalem DataFrame'inden hızlı arama için dictionary oluşturur"""
        if self.datakalem_df is None or self.datakalem_df.empty:
            return {}

        lookup_dict = {}
        lookup_sutun = self.datakalem_df.iloc[:, 1]  # B sütunu

        for index, deger in lookup_sutun.items():
            temiz_deger = self.veri_temizle(deger)
            if temiz_deger:
                lookup_dict[temiz_deger] = list(self.datakalem_df.iloc[index])

        return lookup_dict

    def sonuc_tablosu_olustur(self):
        """Sonuç tablosunu oluşturur"""
        if self.veri_df is None or self.datakalem_df is None:
            print("Hata: Önce Excel dosyalarını yükleyin!")
            return None

        if self.seri_sutun_index is None:
            print("Hata: Seri numarası sütunu bulunamadı!")
            return None

        # Lookup dictionary oluştur
        lookup_dict = self.datakalem_lookup_dict_olustur()

        # Veri Excel'indeki seri numaralarını al
        seri_numaralari = self.veri_df.iloc[:, self.seri_sutun_index].dropna()
        temiz_seri_numaralari = [self.veri_temizle(sn) for sn in seri_numaralari]

        # Sonuç DataFrame'i oluştur
        sonuc_df = pd.DataFrame()
        sonuc_df['SERİ NUMARA'] = temiz_seri_numaralari

        # VLOOKUP işlemleri
        sonuc_df['KALEM'] = [self.vlookup_arama_optimized(x, lookup_dict, 3) for x in temiz_seri_numaralari]
        sonuc_df['MODEL'] = [self.vlookup_arama_optimized(x, lookup_dict, 4) for x in temiz_seri_numaralari]
        sonuc_df['KONUM'] = [self.vlookup_arama_optimized(x, lookup_dict, 6) for x in temiz_seri_numaralari]
        sonuc_df['DURUM'] = [self.vlookup_arama_optimized(x, lookup_dict, 7) for x in temiz_seri_numaralari]

        # BİRLEŞTİR sütunu
        sonuc_df['BİRLEŞTİR'] = sonuc_df['KALEM'].astype(str) + ' ' + sonuc_df['MODEL'].astype(str)

        # KALEM ADETİ sütunu - her kalemin toplam kaç adet olduğu (BULUNAMADI hariç)
        # Sadece bulunan kalemler için adet hesapla
        bulunan_kalemler = sonuc_df[sonuc_df['KALEM'] != 'BULUNAMADI']['KALEM']
        kalem_adetleri = bulunan_kalemler.value_counts().to_dict()
        # BULUNAMADI olanlara "BULUNAMADI" yaz, diğerlerine adet yaz
        sonuc_df['KALEM ADETİ'] = sonuc_df['KALEM'].apply(
            lambda x: 'BULUNAMADI' if x == 'BULUNAMADI' else kalem_adetleri.get(x, 0)
        )

        # KALEM İÇ KİMLİK sütunu (index 12)
        sonuc_df['KALEM İÇ KİMLİK'] = [self.vlookup_arama_optimized(x, lookup_dict, 12) for x in temiz_seri_numaralari]

        return sonuc_df

    def datakalem_excel_yukle_with_progress(self, dosya_yolu, progress_callback=None):
        """DataKalem Excel dosyasını progress ile yükler"""
        self.datakalem_excel_path = dosya_yolu

        # Ana işlem - Excel okuma
        self.datakalem_df = self.excel_oku(dosya_yolu)

        if self.datakalem_df is not None:
            print(f"DataKalem Excel yüklendi: {len(self.datakalem_df)} satır")
            return True
        return False

    def veri_excel_yukle_with_progress(self, dosya_yolu, progress_callback=None, sheet_name=0):
        """Veri Excel dosyasını progress ile yükler"""
        self.veri_excel_path = dosya_yolu

        # Ana işlem - Excel okuma
        self.veri_df = self.excel_oku(dosya_yolu, sheet_name)

        if self.veri_df is not None:
            self.seri_sutun_index = self.seri_numara_sutunu_tespit(self.veri_df)
            print(f"Veri Excel yüklendi: {len(self.veri_df)} satır")

            if self.seri_sutun_index is not None:
                print(f"Seri numarası sütunu: {self.veri_df.columns[self.seri_sutun_index]}")
            else:
                print("Seri numarası sütunu tespit edilemedi!")

            return True
        return False

class ExcelAramaGUI:
    def __init__(self):
        self.arama_sistemi = ExcelSeriArama()
        self.root = tk.Tk()
        self.root.title("Kalem Stok Arama")
        self.root.geometry("900x750")
        self.root.minsize(700, 600)

        # Profesyonel iş uygulaması renkleri
        self.colors = {
            'primary': '#2C3E50',      # Koyu lacivert
            'secondary': '#34495E',     # Orta gri
            'background': '#ECF0F1',    # Açık gri
            'surface': '#FFFFFF',       # Beyaz
            'border': '#BDC3C7',        # Açık gri border
            'success': '#27AE60',       # Yeşil
            'warning': '#F39C12',       # Turuncu
            'error': '#E74C3C',         # Kırmızı
            'text_primary': '#2C3E50',  # Koyu metin
            'text_secondary': '#7F8C8D', # Açık metin
            'button_hover': '#3498DB'   # Mavi hover
        }

        self.fonts = {
            'title': ('Segoe UI', 14, 'bold'),
            'subtitle': ('Segoe UI', 10, 'bold'),
            'body': ('Segoe UI', 9),
            'small': ('Segoe UI', 8)
        }

        self.root.configure(bg=self.colors['background'])
        self.gui_olustur()

    def gui_olustur(self):
        # Ana frame
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Başlık bölümü
        header_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=60)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="Kalem Stok Arama Sistemi",
            font=self.fonts['title'],
            fg='white',
            bg=self.colors['primary']
        )
        title_label.pack(expand=True)

        # Ana içerik alanı - 2 sütun
        content_frame = tk.Frame(main_frame, bg=self.colors['background'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Sol panel - Kontroller
        left_panel = tk.Frame(content_frame, bg=self.colors['surface'], width=320, relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Sağ panel - Sonuçlar
        right_panel = tk.Frame(content_frame, bg=self.colors['surface'], relief=tk.RAISED, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Sol panel içeriği
        self.sol_panel_olustur(left_panel)

        # Sağ panel içeriği
        self.sag_panel_olustur(right_panel)

        # Alt durum çubuğu
        status_frame = tk.Frame(main_frame, bg=self.colors['secondary'], height=35)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        status_frame.pack_propagate(False)

        # Status ve developer credit için ana frame
        status_content_frame = tk.Frame(status_frame, bg=self.colors['secondary'])
        status_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Sol taraf - Status mesajı
        self.status_label = tk.Label(
            status_content_frame,
            text="Hazır",
            fg='white',
            bg=self.colors['secondary'],
            font=self.fonts['body'],
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Sağ taraf - Developer credit
        credit_label = tk.Label(
            status_content_frame,
            text="by ENES EREN",
            font=('Segoe UI', 8, 'underline'),
            fg='#87CEEB',  # Açık mavi
            bg=self.colors['secondary'],
            cursor='hand2',
            anchor='e'
        )
        credit_label.pack(side=tk.RIGHT)
        credit_label.bind("<Button-1>", self.developer_link_ac)

        # Değişkenler
        self.sonuc_df = None
        self.original_df = None
        self.sutun_filtreleri = {}

    def sol_panel_olustur(self, parent):
        # Sol panel başlığı
        panel_title = tk.Label(
            parent,
            text="Kontrol Paneli",
            font=self.fonts['subtitle'],
            fg=self.colors['text_primary'],
            bg=self.colors['surface'],
            pady=10
        )
        panel_title.pack(fill=tk.X)

        # Dosya seçimi grubu
        file_group = tk.LabelFrame(
            parent,
            text="Dosya Seçimi",
            font=self.fonts['body'],
            fg=self.colors['text_primary'],
            bg=self.colors['surface'],
            padx=10,
            pady=10
        )
        file_group.pack(fill=tk.X, padx=10, pady=(0, 15))

        # DataKalem dosyası
        tk.Label(
            file_group,
            text="Kalem Stok Dosyası:",
            font=self.fonts['body'],
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        ).pack(anchor=tk.W, pady=(0, 5))

        datakalem_frame = tk.Frame(file_group, bg=self.colors['surface'])
        datakalem_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            datakalem_frame,
            text="Dosya Seç",
            command=self.datakalem_sec,
            font=self.fonts['body'],
            bg=self.colors['primary'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=3,
            cursor='hand2'
        ).pack(side=tk.LEFT)

        self.datakalem_label = tk.Label(
            datakalem_frame,
            text="Dosya seçilmedi",
            fg=self.colors['text_secondary'],
            bg=self.colors['surface'],
            font=self.fonts['small']
        )
        self.datakalem_label.pack(side=tk.LEFT, padx=(10, 0))

        # Veri dosyası
        tk.Label(
            file_group,
            text="Veri Dosyası:",
            font=self.fonts['body'],
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        ).pack(anchor=tk.W, pady=(0, 5))

        veri_frame = tk.Frame(file_group, bg=self.colors['surface'])
        veri_frame.pack(fill=tk.X)

        tk.Button(
            veri_frame,
            text="Dosya Seç",
            command=self.veri_sec,
            font=self.fonts['body'],
            bg=self.colors['primary'],
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=3,
            cursor='hand2'
        ).pack(side=tk.LEFT)

        self.veri_label = tk.Label(
            veri_frame,
            text="Dosya seçilmedi",
            fg=self.colors['text_secondary'],
            bg=self.colors['surface'],
            font=self.fonts['small']
        )
        self.veri_label.pack(side=tk.LEFT, padx=(10, 0))

        # İşlemler grubu
        action_group = tk.LabelFrame(
            parent,
            text="İşlemler",
            font=self.fonts['body'],
            fg=self.colors['text_primary'],
            bg=self.colors['surface'],
            padx=10,
            pady=10
        )
        action_group.pack(fill=tk.X, padx=10, pady=(0, 10))

        # İşlem butonları
        tk.Button(
            action_group,
            text="Arama Yap",
            command=self.arama_yap,
            font=self.fonts['body'],
            bg=self.colors['success'],
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=6,
            cursor='hand2'
        ).pack(fill=tk.X, pady=(0, 5))

        tk.Button(
            action_group,
            text="Panoya Kopyala",
            command=self.panoya_kopyala,
            font=self.fonts['body'],
            bg='#8E44AD',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=6,
            cursor='hand2'
        ).pack(fill=tk.X, pady=(0, 5))

        tk.Button(
            action_group,
            text="Temizle",
            command=self.temizle,
            font=self.fonts['body'],
            bg=self.colors['text_secondary'],
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=6,
            cursor='hand2'
        ).pack(fill=tk.X, pady=(0, 5))

        tk.Button(
            action_group,
            text="ExternalID",
            command=self.external_id_kopyala,
            font=self.fonts['body'],
            bg='#E67E22',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=6,
            cursor='hand2'
        ).pack(fill=tk.X)

        # Filtreleme grubu
        filter_group = tk.LabelFrame(
            parent,
            text="Filtreleme",
            font=self.fonts['body'],
            fg=self.colors['text_primary'],
            bg=self.colors['surface'],
            padx=10,
            pady=5
        )
        filter_group.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(
            filter_group,
            text="Genel Arama:",
            font=self.fonts['body'],
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        ).pack(anchor=tk.W, pady=(0, 5))

        self.filter_entry = tk.Entry(
            filter_group,
            font=self.fonts['body'],
            relief=tk.SOLID,
            bd=1
        )
        self.filter_entry.pack(fill=tk.X, pady=(0, 5))
        self.filter_entry.bind('<KeyRelease>', self.genel_filtre_uygula)

        tk.Button(
            filter_group,
            text="Filtreleri Temizle",
            command=self.tum_filtreleri_temizle,
            font=self.fonts['small'],
            bg=self.colors['border'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor='hand2'
        ).pack(fill=tk.X)

    def sag_panel_olustur(self, parent):
        # Sağ panel başlığı
        panel_title = tk.Label(
            parent,
            text="Arama Sonuçları",
            font=self.fonts['subtitle'],
            fg=self.colors['text_primary'],
            bg=self.colors['surface'],
            pady=10
        )
        panel_title.pack(fill=tk.X)

        # Tablo frame
        table_frame = tk.Frame(parent, bg=self.colors['surface'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Treeview
        style = ttk.Style()
        style.configure("Business.Treeview", font=self.fonts['body'])
        style.configure("Business.Treeview.Heading", font=self.fonts['subtitle'])

        self.tree = ttk.Treeview(table_frame, show="headings", style="Business.Treeview")

        # Scrollbar'lar
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid yerleşimi
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def developer_link_ac(self, event):
        """Developer link'ini açar"""
        try:
            webbrowser.open("https://eneseren.com")
        except Exception as e:
            print(f"Link açma hatası: {e}")

    def external_id_kopyala(self):
        """Anlık tarih ve saati ExternalID formatında panoya kopyalar (YYYYMMDDHHmm)"""
        try:
            # Şu anki tarih ve saati al
            simdi = datetime.datetime.now()
            # Format: YYYYMMDDHHmm (örn: 202602021220)
            external_id = simdi.strftime("%Y%m%d%H%M")
            
            # Panoya kopyala
            self.root.clipboard_clear()
            self.root.clipboard_append(external_id)
            self.root.update()
            
            # Kullanıcıya bilgi ver
            formatted_time = simdi.strftime("%d.%m.%Y %H:%M")
            self.status_label.config(text=f"ExternalID kopyalandı: {external_id} ({formatted_time})")
            
            # Otomatik kapanan mesaj göster
            self.otomatik_kapanan_mesaj_ozel("ExternalID Kopyalandı", f"ExternalID: {external_id}\n({formatted_time})")
            
        except Exception as e:
            self.status_label.config(text=f"ExternalID kopyalama hatası: {str(e)}")

    def otomatik_kapanan_mesaj(self, baslik, mesaj, sure=2000):
        """Belirli süre sonra otomatik kapanan bilgi mesajı gösterir"""
        # Toplevel penceresi oluştur
        popup = tk.Toplevel(self.root)
        popup.title(baslik)
        popup.geometry("280x100")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.overrideredirect(False)
        
        # Pencereyi ortala
        popup.geometry("+{}+{}".format(
            self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 140,
            self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 50
        ))
        
        # İkon ve mesaj frame
        content_frame = tk.Frame(popup, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Yatay düzen için frame
        h_frame = tk.Frame(content_frame, bg='white')
        h_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başarı ikonu (✓)
        icon_label = tk.Label(
            h_frame,
            text="✓",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['success'],
            bg='white'
        )
        icon_label.pack(side=tk.LEFT, padx=(10, 15))
        
        # Mesaj (kısa versiyon)
        satir_sayisi = len(self.sonuc_df) if self.sonuc_df is not None else 0
        kisa_mesaj = f"Panoya kopyalandı!\n{satir_sayisi} satır veri"
        
        msg_label = tk.Label(
            h_frame,
            text=kisa_mesaj,
            font=self.fonts['body'],
            fg=self.colors['text_primary'],
            bg='white',
            justify='left'
        )
        msg_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Belirli süre sonra otomatik kapat
        popup.after(sure, popup.destroy)
        
        # Pencereye tıklanırsa da kapansın
        popup.bind("<Button-1>", lambda e: popup.destroy())

    def otomatik_kapanan_mesaj_ozel(self, baslik, mesaj, sure=2000):
        """Belirli süre sonra otomatik kapanan genel bilgi mesajı gösterir"""
        # Toplevel penceresi oluştur
        popup = tk.Toplevel(self.root)
        popup.title(baslik)
        popup.geometry("280x100")
        popup.resizable(False, False)
        popup.transient(self.root)
        
        # Pencereyi ortala
        popup.geometry("+{}+{}".format(
            self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 140,
            self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 50
        ))
        
        # İkon ve mesaj frame
        content_frame = tk.Frame(popup, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Yatay düzen için frame
        h_frame = tk.Frame(content_frame, bg='white')
        h_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başarı ikonu (✓)
        icon_label = tk.Label(
            h_frame,
            text="✓",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['success'],
            bg='white'
        )
        icon_label.pack(side=tk.LEFT, padx=(10, 15))
        
        # Mesaj
        msg_label = tk.Label(
            h_frame,
            text=mesaj,
            font=self.fonts['body'],
            fg=self.colors['text_primary'],
            bg='white',
            justify='left'
        )
        msg_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Belirli süre sonra otomatik kapat
        popup.after(sure, popup.destroy)
        
        # Pencereye tıklanırsa da kapansın
        popup.bind("<Button-1>", lambda e: popup.destroy())

    def datakalem_sec(self):
        dosya = filedialog.askopenfilename(
            title="DataKalem Excel Dosyasını Seçin",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if dosya:
            # Sadece dosya yolunu kaydet, yükleme yapma
            self.arama_sistemi.datakalem_excel_path = dosya

            # Dosya boyutunu göster
            dosya_boyutu = os.path.getsize(dosya)
            boyut_mb = dosya_boyutu / (1024 * 1024)
            boyut_str = f"{boyut_mb:.1f} MB" if boyut_mb >= 1 else f"{dosya_boyutu / 1024:.1f} KB"

            self.datakalem_label.config(text=f"{os.path.basename(dosya)} ({boyut_str})", fg=self.colors['success'])
            self.status_label.config(text="DataKalem dosyası seçildi - Arama için hazır")


    def veri_sec(self):
        dosya = filedialog.askopenfilename(
            title="Veri Excel Dosyasını Seçin",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if dosya:
            # Sadece dosya yolunu kaydet, yükleme yapma
            self.arama_sistemi.veri_excel_path = dosya

            # Dosya boyutunu göster
            dosya_boyutu = os.path.getsize(dosya)
            boyut_mb = dosya_boyutu / (1024 * 1024)
            boyut_str = f"{boyut_mb:.1f} MB" if boyut_mb >= 1 else f"{dosya_boyutu / 1024:.1f} KB"

            self.veri_label.config(text=f"{os.path.basename(dosya)} ({boyut_str})", fg=self.colors['success'])
            self.status_label.config(text="Veri dosyası seçildi - Arama için hazır")


    def arama_yap(self):
        # Dosya seçilmiş mi kontrol et
        if not self.arama_sistemi.datakalem_excel_path or not self.arama_sistemi.veri_excel_path:
            messagebox.showwarning("Uyarı", "Önce her iki dosyayı da seçin!")
            return

        self.status_label.config(text="Dosyalar yükleniyor ve arama yapılıyor...")
        self.root.update()

        # Threading kullanarak yükleme ve arama işlemi
        def yukle_ve_ara():
            try:
                # Önce dosyaları yükle
                self.root.after(0, lambda: self.status_label.config(text="DataKalem dosyası yükleniyor..."))

                datakalem_sonuc = self.arama_sistemi.datakalem_excel_yukle_with_progress(
                    self.arama_sistemi.datakalem_excel_path
                )

                if not datakalem_sonuc:
                    self.root.after(0, lambda: self.status_label.config(text="DataKalem dosyası yüklenemedi!"))
                    return

                self.root.after(0, lambda: self.status_label.config(text="Veri dosyası yükleniyor..."))

                veri_sonuc = self.arama_sistemi.veri_excel_yukle_with_progress(
                    self.arama_sistemi.veri_excel_path
                )

                if not veri_sonuc:
                    self.root.after(0, lambda: self.status_label.config(text="Veri dosyası yüklenemedi!"))
                    return

                # Arama yap
                self.root.after(0, lambda: self.status_label.config(text="Arama yapılıyor..."))

                sonuc_df = self.arama_sistemi.sonuc_tablosu_olustur()

                # GUI güncellemesini ana thread'de yap
                self.root.after(0, lambda: self.arama_tamamlandi(sonuc_df))

            except Exception as e:
                self.root.after(0, lambda: self.arama_hatasi(str(e)))

        thread = threading.Thread(target=yukle_ve_ara, daemon=True)
        thread.start()

    def arama_tamamlandi(self, sonuc_df):
        if sonuc_df is not None:
            self.sonuc_df = sonuc_df
            self.original_df = self.sonuc_df.copy()
            self.sutun_filtreleri = {}
            self.tabloyu_goster(self.sonuc_df)
            bulunan = len([row for _, row in self.sonuc_df.iterrows() if row['KALEM'] != 'BULUNAMADI'])
            self.status_label.config(text=f"Arama tamamlandı: {bulunan} başarılı eşleşme")
        else:
            self.status_label.config(text="Arama yapılamadı")

    def arama_hatasi(self, hata_mesaji):
        self.status_label.config(text=f"Hata: {hata_mesaji}")

    def tabloyu_goster(self, df):
        """DataFrame'i Treeview'da gösterir"""
        # Önceki verileri temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        if df is None or df.empty:
            return

        # Sütunları ayarla
        columns = list(df.columns)
        self.tree["columns"] = columns

        # Sütun başlıklarını ayarla (Excel benzeri filter ikonu ile)
        for col in columns:
            self.tree.heading(col, text=f"{col} ▼", command=lambda c=col: self.sutun_filtresi_goster(c))
            self.tree.column(col, width=150, minwidth=100)

        # Verileri ekle
        for index, row in df.iterrows():
            values = [str(row[col]) for col in columns]
            item_id = self.tree.insert("", "end", values=values)

    def sutun_filtresi_goster(self, sutun_adi):
        """Excel benzeri sütün filtresi dropdown box gösterir"""
        if self.original_df is None or self.original_df.empty:
            return

        # Sütundaki benzersiz değerleri al
        benzersiz_degerler = self.original_df[sutun_adi].astype(str).unique()
        benzersiz_degerler = sorted([d for d in benzersiz_degerler if d != 'nan'])

        # Dropdown penceresi oluştur (Toplevel yerine Frame)
        filter_window = tk.Toplevel(self.root)
        filter_window.title(f"{sutun_adi} Filtresi")
        filter_window.geometry("280x450")
        filter_window.resizable(False, False)

        # Pencerenin sürüklenememesi için
        filter_window.transient(self.root)
        filter_window.grab_set()

        # Pencereyi ortala
        filter_window.geometry("+{}+{}".format(
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))

        # Ana frame
        main_frame = tk.Frame(filter_window, relief=tk.RAISED, bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Başlık
        header_frame = tk.Frame(main_frame, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(header_frame, text=f"{sutun_adi} Filtresi", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=5)

        # Tümünü seç/kaldır frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))

        self.tumunu_sec_var = tk.BooleanVar()
        self.tumunu_sec_var.set(True)

        # Tümünü seç checkbox
        tumunu_sec_cb = tk.Checkbutton(
            control_frame,
            text="Tümünü Seç",
            variable=self.tumunu_sec_var,
            command=lambda: self.tumunu_sec_toggle(checkboxes)
        )
        tumunu_sec_cb.pack(side=tk.LEFT)

        # Listbox ile scrollable alan (Text widget yerine)
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Listbox ve scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Checkbox'lar için Frame içinde Canvas kullan
        canvas = tk.Canvas(list_frame, yscrollcommand=scrollbar.set, height=280)
        scrollbar.config(command=canvas.yview)

        # Scrollable frame
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Canvas'a frame'i yerleştir
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Canvas genişliğini ayarla
        def configure_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        canvas.bind('<Configure>', configure_canvas)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Checkbox'ları oluştur
        checkboxes = {}
        for i, deger in enumerate(benzersiz_degerler):
            var = tk.BooleanVar()
            # Eğer bu sütun için filtre varsa, var olan filtreye göre ayarla
            if sutun_adi in self.sutun_filtreleri:
                var.set(deger in self.sutun_filtreleri[sutun_adi])
            else:
                var.set(True)  # Varsayılan olarak tümü seçili

            cb = tk.Checkbutton(
                scrollable_frame,
                text=str(deger),
                variable=var,
                anchor="w",
                command=lambda: self.checkbox_degisti(checkboxes)
            )
            cb.pack(fill=tk.X, padx=5, pady=1)
            checkboxes[deger] = var

        # Mouse wheel desteği
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)

        # Butonlar frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        # İptal butonu
        tk.Button(
            button_frame,
            text="İptal",
            command=filter_window.destroy,
            width=10
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Uygula butonu
        tk.Button(
            button_frame,
            text="Uygula",
            command=lambda: self.sutun_filtresini_uygula(sutun_adi, checkboxes, filter_window),
            bg="#4CAF50",
            fg="white",
            width=10
        ).pack(side=tk.RIGHT)

        # Focus ayarla
        filter_window.focus_set()

    def tumunu_sec_toggle(self, checkboxes):
        """Tümünü seç/kaldır toggle"""
        secili = self.tumunu_sec_var.get()
        for var in checkboxes.values():
            var.set(secili)

    def checkbox_degisti(self, checkboxes):
        """Checkbox değiştiğinde tümünü seç durumunu güncelle"""
        secili_sayisi = sum(1 for var in checkboxes.values() if var.get())
        toplam_sayi = len(checkboxes)

        if secili_sayisi == toplam_sayi:
            self.tumunu_sec_var.set(True)
        elif secili_sayisi == 0:
            self.tumunu_sec_var.set(False)
        else:
            # Kısmi seçim durumunda checkbox'ı belirsiz durumda bırak
            pass

    def sutun_filtresini_uygula(self, sutun_adi, checkboxes, filter_window):
        """Sütun filtresini uygular"""
        # Seçili değerleri al
        secili_degerler = [deger for deger, var in checkboxes.items() if var.get()]

        if secili_degerler:
            self.sutun_filtreleri[sutun_adi] = secili_degerler
        else:
            # Hiç bir değer seçili değilse filtreyi kaldır
            if sutun_adi in self.sutun_filtreleri:
                del self.sutun_filtreleri[sutun_adi]

        # Filtreleri uygula
        self.tum_filtreleri_uygula()
        filter_window.destroy()

    def tum_filtreleri_uygula(self):
        """Tüm aktif filtreleri uygular"""
        if self.original_df is None:
            return

        filtered_df = self.original_df.copy()

        # Sütun filtrelerini uygula
        for sutun, degerler in self.sutun_filtreleri.items():
            filtered_df = filtered_df[filtered_df[sutun].astype(str).isin(degerler)]

        # Genel arama filtresini uygula
        genel_filtre = self.filter_entry.get().lower()
        if genel_filtre:
            filtered_df = filtered_df[
                filtered_df.astype(str).apply(
                    lambda row: any(genel_filtre in str(cell).lower() for cell in row), axis=1
                )
            ]

        self.sonuc_df = filtered_df
        self.tabloyu_goster(filtered_df)

        # Durum güncelle
        filtre_sayisi = len(self.sutun_filtreleri)
        if filtre_sayisi > 0 or genel_filtre:
            self.status_label.config(text=f"Filtre uygulandı: {len(filtered_df)} sonuç ({filtre_sayisi} sütun filtresi)")
        else:
            self.status_label.config(text=f"Tüm sonuçlar: {len(filtered_df)}")

    def genel_filtre_uygula(self, event=None):
        """Genel arama filtresini uygular"""
        self.tum_filtreleri_uygula()

    def tum_filtreleri_temizle(self):
        """Tüm filtreleri temizler"""
        self.filter_entry.delete(0, tk.END)
        self.sutun_filtreleri = {}
        if self.original_df is not None:
            self.sonuc_df = self.original_df.copy()
            self.tabloyu_goster(self.sonuc_df)
            self.status_label.config(text=f"Filtreler temizlendi: {len(self.sonuc_df)} sonuç gösteriliyor")

    def sutunu_sirala(self, col):
        """Sütunu sıralar"""
        if self.sonuc_df is None:
            return

        # Sıralama durumunu takip et
        if not hasattr(self, 'sort_reverse'):
            self.sort_reverse = {}

        reverse = self.sort_reverse.get(col, False)
        self.sort_reverse[col] = not reverse

        # Şu anki görünen DataFrame'i sırala
        sorted_df = self.sonuc_df.sort_values(by=col, ascending=not reverse)
        self.sonuc_df = sorted_df
        self.tabloyu_goster(sorted_df)











    def panoya_kopyala(self):
        """Sonuç tablosunu panoya kopyalar (Excel'e yapıştırılabilir format)"""
        if self.sonuc_df is None or self.sonuc_df.empty:
            messagebox.showwarning("Uyarı", "Önce arama yapın!")
            return

        try:
            # Başlık satırını oluştur
            headers = list(self.sonuc_df.columns)
            header_line = '\t'.join(headers)

            # Veri satırlarını oluştur
            data_lines = []
            for _, row in self.sonuc_df.iterrows():
                # Her sütunu string'e çevir ve tab ile birleştir
                row_data = []
                for col in headers:
                    value = str(row[col]) if pd.notna(row[col]) else ""
                    row_data.append(value)
                data_lines.append('\t'.join(row_data))

            # Tüm satırları birleştir - sadece \n kullan
            all_lines = [header_line] + data_lines
            clipboard_text = '\n'.join(all_lines)

            # Panoya kopyala
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)
            self.root.update()

            # Başarı mesajı
            satir_sayisi = len(self.sonuc_df)
            self.status_label.config(text=f"Tablo panoya kopyalandı ({satir_sayisi} satır)")
            self.otomatik_kapanan_mesaj("Başarılı", f"Sonuç tablosu panoya kopyalandı!\n\n{satir_sayisi} satır veri Excel'e yapıştırılabilir.\n\nExcel'de Ctrl+V ile yapıştırabilirsiniz.")

        except Exception as e:
            self.status_label.config(text="Panoya kopyalama hatası!")
            messagebox.showerror("Hata", f"Panoya kopyalama hatası:\n{str(e)}")

    def temizle(self):
        # Treeview'i temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filtreleri temizle
        self.filter_entry.delete(0, tk.END)
        self.sutun_filtreleri = {}

        # Label'ları sıfırla
        self.datakalem_label.config(text="Dosya seçilmedi", fg=self.colors['text_secondary'])
        self.veri_label.config(text="Dosya seçilmedi", fg=self.colors['text_secondary'])

        # Arama sistemini sıfırla
        self.arama_sistemi = ExcelSeriArama()
        self.sonuc_df = None
        self.original_df = None
        self.status_label.config(text="Temizlendi - Yeni arama için hazır")
        
        # Otomatik kapanan mesaj göster
        self.otomatik_kapanan_mesaj_ozel("Temizlendi", "Tüm veriler temizlendi!\nYeni arama için hazır.")

    def calistir(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ExcelAramaGUI()
    app.calistir()