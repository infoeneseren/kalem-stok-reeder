"""
Excel Seri Arama - İş Mantığı
Kalem stok arama ve eşleştirme sistemi
Multiprocessing ile hızlandırılmış versiyon
"""
import pandas as pd
import os
import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp


class ExcelSeriArama:
    """Excel dosyalarında seri numarası arama ve eşleştirme sınıfı"""
    
    def __init__(self):
        self.veri_excel_path = None
        self.datakalem_excel_path = None
        self.veri_df = None
        self.datakalem_df = None
        self.seri_sutun_index = None
        self.lookup_dict = None  # Önbelleklenmiş lookup dictionary
        
        # CPU sayısı
        self.cpu_count = max(1, mp.cpu_count() - 1)  # 1 CPU'yu sistem için bırak

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
                return str(int(deger))
            else:
                return str(deger)

        # String ise ondalık varsa kaldır
        deger_str = str(deger).strip()
        if '.' in deger_str:
            try:
                num = float(deger_str)
                return str(int(num))
            except:
                return deger_str

        return deger_str

    def seri_numara_sutunu_tespit(self, df):
        """Seri numarası sütununu otomatik tespit eder"""
        tam_eslesme_isimleri = [
            'SERİ NO', 'SERİ NUMARA', 'SERİ NUMARASI', 'SERIAL NUMBER', 'SERIAL NO', 'SN'
        ]

        # TAM EŞLEŞME
        for col_index, col_name in enumerate(df.columns):
            col_name_upper = str(col_name).upper().strip()
            if col_name_upper in tam_eslesme_isimleri:
                return col_index

        # BAŞLANGIÇ EŞLEŞME
        baslangic_isimleri = ['SERİ NO', 'SERİ NUMARA', 'SERIAL NUMBER', 'SERIAL NO']
        for col_index, col_name in enumerate(df.columns):
            col_name_upper = str(col_name).upper().strip()
            for baslagic_isim in baslangic_isimleri:
                if col_name_upper.startswith(baslagic_isim):
                    return col_index

        # İÇERİR EŞLEŞME
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

            with open(dosya_yolu, 'rb') as f:
                first_bytes = f.read(1000)

            # Excel 2003 XML formatı kontrolü
            if b'<?xml' in first_bytes and b'xmlns:ss=' in first_bytes:
                print("Excel 2003 XML formatı tespit edildi...")
                return self.excel_xml_oku(dosya_yolu)

            # Engine sırası
            if dosya_yolu.lower().endswith('.xlsx'):
                engines_to_try = ['openpyxl', 'xlrd']
            elif dosya_yolu.lower().endswith('.xls'):
                engines_to_try = ['xlrd', 'openpyxl']
            else:
                engines_to_try = ['openpyxl', 'xlrd']

            for engine in engines_to_try:
                try:
                    print(f"{engine} engine deneniyor...")
                    df = pd.read_excel(dosya_yolu, sheet_name=sheet_name, engine=engine)
                    print(f"Başarılı ({engine}): {df.shape}")
                    return df
                except Exception as e:
                    print(f"{engine} engine başarısız: {str(e)}")
                    continue

            # Varsayılan engine
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
        """Excel 2003 XML formatını okur - Paralel işleme ile hızlandırılmış"""
        try:
            import xml.etree.ElementTree as ET

            self.log_mesaj("XML dosyası okunuyor...")
            tree = ET.parse(dosya_yolu)
            root = tree.getroot()

            namespaces = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}

            worksheet = root.find('.//ss:Worksheet', namespaces)
            if worksheet is None:
                return None

            table = worksheet.find('.//ss:Table', namespaces)
            if table is None:
                return None

            rows = table.findall('.//ss:Row', namespaces)
            self.log_mesaj(f"Toplam {len(rows)} satır bulundu")

            # Paralel row işleme için fonksiyon
            def process_row(row):
                row_data = []
                cells = row.findall('.//ss:Cell', namespaces)
                current_index = 0

                for cell in cells:
                    # ss:Index attribute kontrolü (boş hücreleri atlama için)
                    index_attr = cell.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
                    if index_attr:
                        target_index = int(index_attr) - 1
                        while current_index < target_index:
                            row_data.append("")
                            current_index += 1
                    
                    data_elem = cell.find('.//ss:Data', namespaces)
                    if data_elem is not None:
                        row_data.append(data_elem.text if data_elem.text else "")
                    else:
                        row_data.append("")
                    current_index += 1
                
                return row_data
            
            # Paralel işleme
            self.log_mesaj("Paralel XML işleme başlıyor...")
            with ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
                data = list(executor.map(process_row, rows))
            
            # Boş satırları filtrele
            data = [row for row in data if row and any(cell != "" for cell in row)]

            if not data:
                return None

            if len(data) > 1:
                # İlk satırı başlık olarak kullan
                max_cols = max(len(row) for row in data)
                # Tüm satırları aynı uzunluğa getir
                data = [row + [""] * (max_cols - len(row)) for row in data]
                df = pd.DataFrame(data[1:], columns=data[0])
            else:
                df = pd.DataFrame(data)

            self.log_mesaj(f"XML başarılı: {df.shape}")
            return df

        except Exception as e:
            print(f"XML okuma hatası: {str(e)}")
            try:
                df = pd.read_csv(dosya_yolu, sep='\t', encoding='utf-8')
                return df
            except:
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
        """DataKalem DataFrame'inden hızlı arama için dictionary oluşturur - Paralel"""
        if self.datakalem_df is None or self.datakalem_df.empty:
            return {}

        # Eğer zaten oluşturulmuşsa, önbellekten döndür
        if self.lookup_dict is not None:
            return self.lookup_dict

        self.log_mesaj("Lookup dictionary oluşturuluyor (paralel)...")
        
        # DataFrame'i numpy array'e çevir (daha hızlı erişim)
        df_values = self.datakalem_df.values
        lookup_sutun = self.datakalem_df.iloc[:, 1].values  # B sütunu
        
        def process_chunk(args):
            start_idx, end_idx = args
            chunk_dict = {}
            for i in range(start_idx, end_idx):
                deger = lookup_sutun[i]
            temiz_deger = self.veri_temizle(deger)
            if temiz_deger:
                    chunk_dict[temiz_deger] = list(df_values[i])
            return chunk_dict
        
        # Chunk'lara böl
        total_rows = len(lookup_sutun)
        chunk_size = max(1000, total_rows // (self.cpu_count * 2))
        chunks = [(i, min(i + chunk_size, total_rows)) 
                  for i in range(0, total_rows, chunk_size)]
        
        self.log_mesaj(f"{len(chunks)} chunk'ta {total_rows} satır işlenecek")
        
        # Paralel işleme
        lookup_dict = {}
        with ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
            results = executor.map(process_chunk, chunks)
            for chunk_dict in results:
                lookup_dict.update(chunk_dict)

        self.lookup_dict = lookup_dict  # Önbelleğe al
        self.log_mesaj(f"Lookup dictionary oluşturuldu: {len(lookup_dict)} kayıt")
        return lookup_dict
    
    def _vlookup_chunk(self, args):
        """Paralel VLOOKUP için chunk işleme fonksiyonu"""
        chunk, lookup_dict, sutun_indexleri = args
        sonuclar = []
        
        for seri in chunk:
            temiz_seri = self.veri_temizle(seri)
            row_sonuc = {'seri': temiz_seri}
            
            if temiz_seri in lookup_dict:
                row_data = lookup_dict[temiz_seri]
                for sutun_adi, idx in sutun_indexleri.items():
                    if idx < len(row_data):
                        row_sonuc[sutun_adi] = self.veri_temizle(row_data[idx])
                    else:
                        row_sonuc[sutun_adi] = "BULUNAMADI"
            else:
                for sutun_adi in sutun_indexleri.keys():
                    row_sonuc[sutun_adi] = "BULUNAMADI"
            
            sonuclar.append(row_sonuc)
        
        return sonuclar

    def sonuc_tablosu_olustur(self):
        """Sonuç tablosunu oluşturur - Paralel işleme ile hızlandırılmış"""
        if self.veri_df is None or self.datakalem_df is None:
            print("Hata: Önce Excel dosyalarını yükleyin!")
            return None

        if self.seri_sutun_index is None:
            print("Hata: Seri numarası sütunu bulunamadı!")
            return None

        self.log_mesaj("Paralel arama başlıyor...")

        # Lookup dictionary oluştur
        lookup_dict = self.datakalem_lookup_dict_olustur()

        # Veri Excel'indeki seri numaralarını al
        seri_numaralari = self.veri_df.iloc[:, self.seri_sutun_index].dropna().tolist()
        toplam = len(seri_numaralari)
        self.log_mesaj(f"Toplam {toplam} seri numarası aranacak")

        # Sütun indexleri
        sutun_indexleri = {
            'KALEM': 3,
            'MODEL': 4,
            'KONUM': 6,
            'DURUM': 7,
            'KALEM_IC_KIMLIK': 12
        }

        # Chunk boyutu hesapla
        chunk_size = max(100, toplam // (self.cpu_count * 4))
        chunks = [seri_numaralari[i:i+chunk_size] for i in range(0, toplam, chunk_size)]
        self.log_mesaj(f"{len(chunks)} chunk, her biri ~{chunk_size} kayıt")

        # Paralel işleme
        all_results = []
        
        # ThreadPoolExecutor kullan (I/O bound işlemler için daha verimli)
        with ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
            chunk_args = [(chunk, lookup_dict, sutun_indexleri) for chunk in chunks]
            
            for i, result in enumerate(executor.map(self._vlookup_chunk, chunk_args)):
                all_results.extend(result)
                if (i + 1) % 10 == 0:
                    self.log_mesaj(f"İşlenen chunk: {i+1}/{len(chunks)}")

        self.log_mesaj("Sonuç DataFrame oluşturuluyor...")

        # Sonuç DataFrame'i oluştur
        sonuc_df = pd.DataFrame()
        sonuc_df['SERİ NUMARA'] = [r['seri'] for r in all_results]
        sonuc_df['KALEM'] = [r['KALEM'] for r in all_results]
        sonuc_df['MODEL'] = [r['MODEL'] for r in all_results]
        sonuc_df['KONUM'] = [r['KONUM'] for r in all_results]
        sonuc_df['DURUM'] = [r['DURUM'] for r in all_results]

        # BİRLEŞTİR sütunu
        sonuc_df['BİRLEŞTİR'] = sonuc_df['KALEM'].astype(str) + ' ' + sonuc_df['MODEL'].astype(str)

        # KALEM ADETİ sütunu
        bulunan_kalemler = sonuc_df[sonuc_df['KALEM'] != 'BULUNAMADI']['KALEM']
        kalem_adetleri = bulunan_kalemler.value_counts().to_dict()
        sonuc_df['KALEM ADETİ'] = sonuc_df['KALEM'].apply(
            lambda x: 'BULUNAMADI' if x == 'BULUNAMADI' else kalem_adetleri.get(x, 0)
        )

        # KALEM İÇ KİMLİK sütunu
        sonuc_df['KALEM İÇ KİMLİK'] = [r['KALEM_IC_KIMLIK'] for r in all_results]

        self.log_mesaj(f"Arama tamamlandı: {len(sonuc_df)} sonuç")
        return sonuc_df

    def datakalem_excel_yukle_with_progress(self, dosya_yolu, progress_callback=None):
        """DataKalem Excel dosyasını yükler"""
        self.datakalem_excel_path = dosya_yolu
        self.datakalem_df = self.excel_oku(dosya_yolu)

        if self.datakalem_df is not None:
            print(f"DataKalem Excel yüklendi: {len(self.datakalem_df)} satır")
            return True
        return False

    def veri_excel_yukle_with_progress(self, dosya_yolu, progress_callback=None, sheet_name=0):
        """Veri Excel dosyasını yükler"""
        self.veri_excel_path = dosya_yolu
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


# Ana uygulama başlatıcı
if __name__ == "__main__":
    from ui.main_window import MainWindow
    from license_check import LicenseChecker, check_and_run
    
    # ==================== LİSANS AYARLARI ====================
    # GitHub'a yükledikten sonra bu URL'yi güncelleyin!
    # Format: https://raw.githubusercontent.com/KULLANICI/REPO/main/license_status.json
    # Örnek: https://raw.githubusercontent.com/AhmetReeder/kalem-stok-app/main/license_status.json
    
    GITHUB_LICENSE_URL = "https://raw.githubusercontent.com/KULLANICI_ADI/REPO_ADI/main/license_status.json"
    
    # Offline modda çalışmaya izin ver (False = daha güvenli)
    LicenseChecker.ALLOW_OFFLINE = False
    # ==========================================================
    
    def start_app():
        """Uygulamayı başlatır"""
        arama_sistemi = ExcelSeriArama()
        app = MainWindow(arama_sistemi)
        app.run()
    
    # Lisans kontrolü yap ve uygulamayı başlat
    check_and_run(start_app, GITHUB_LICENSE_URL)
