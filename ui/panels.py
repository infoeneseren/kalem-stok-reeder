"""
Sol ve sağ panel bileşenleri
"""
import tkinter as tk
from tkinter import ttk
from .theme import ModernTheme
from .components import ModernButton, ModernCard, ModernEntry, ModernLabel, ModernScrollbar


class LeftPanel(tk.Frame):
    """Sol kontrol paneli"""
    
    def __init__(self, parent, callbacks=None):
        self.colors = ModernTheme.COLORS
        self.fonts = ModernTheme.FONTS
        self.callbacks = callbacks or {}
        
        super().__init__(
            parent,
            bg=self.colors['bg_primary'],
            width=360
        )
        self.pack_propagate(False)
        
        self._create_file_card()
        self._create_action_card()
        self._create_filter_card()
    
    def _create_file_card(self):
        """Dosya seçim kartı"""
        card = ModernCard(self, title="Dosya Seçimi", icon="📁")
        card.pack(fill=tk.X, padx=8, pady=(8, 12))
        
        content = card.get_content_frame()
        
        # Kalem Stok Dosyası
        ModernLabel(
            content, text="Kalem Stok Dosyası", style="muted",
            bg=self.colors['bg_card']
        ).pack(anchor=tk.W, pady=(0, 6))
        
        file1_frame = tk.Frame(content, bg=self.colors['bg_card'])
        file1_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.datakalem_btn = ModernButton(
            file1_frame,
            text="Dosya Seç",
            icon="📂",
            command=self.callbacks.get('datakalem_sec'),
            style="secondary",
            width=120,
            height=36
        )
        self.datakalem_btn.pack(side=tk.LEFT)
        
        self.datakalem_label = ModernLabel(
            file1_frame, text="Seçilmedi", style="muted",
            bg=self.colors['bg_card']
        )
        self.datakalem_label.pack(side=tk.LEFT, padx=(12, 0))
        
        # Veri Dosyası
        ModernLabel(
            content, text="Veri Dosyası", style="muted",
            bg=self.colors['bg_card']
        ).pack(anchor=tk.W, pady=(0, 6))
        
        file2_frame = tk.Frame(content, bg=self.colors['bg_card'])
        file2_frame.pack(fill=tk.X)
        
        self.veri_btn = ModernButton(
            file2_frame,
            text="Dosya Seç",
            icon="📂",
            command=self.callbacks.get('veri_sec'),
            style="secondary",
            width=120,
            height=36
        )
        self.veri_btn.pack(side=tk.LEFT)
        
        self.veri_label = ModernLabel(
            file2_frame, text="Seçilmedi", style="muted",
            bg=self.colors['bg_card']
        )
        self.veri_label.pack(side=tk.LEFT, padx=(12, 0))
    
    def _create_action_card(self):
        """İşlemler kartı"""
        card = ModernCard(self, title="İşlemler", icon="⚡")
        card.pack(fill=tk.X, padx=8, pady=(0, 12))
        
        content = card.get_content_frame()
        
        # Arama Yap
        ModernButton(
            content,
            text="Arama Yap",
            icon="🔍",
            command=self.callbacks.get('arama_yap'),
            style="success",
            width=296,
            height=42
        ).pack(fill=tk.X, pady=(0, 8))
        
        # Panoya Kopyala
        ModernButton(
            content,
            text="Panoya Kopyala",
            icon="📋",
            command=self.callbacks.get('panoya_kopyala'),
            style="info",
            width=296,
            height=42
        ).pack(fill=tk.X, pady=(0, 8))
        
        # Temizle
        ModernButton(
            content,
            text="Temizle",
            icon="🗑️",
            command=self.callbacks.get('temizle'),
            style="secondary",
            width=296,
            height=42
        ).pack(fill=tk.X, pady=(0, 8))
        
        # ExternalID
        ModernButton(
            content,
            text="ExternalID",
            icon="🆔",
            command=self.callbacks.get('external_id'),
            style="warning",
            width=296,
            height=42
        ).pack(fill=tk.X)
    
    def _create_filter_card(self):
        """Filtreleme kartı"""
        card = ModernCard(self, title="Filtreleme", icon="🔎")
        card.pack(fill=tk.X, padx=8)
        
        content = card.get_content_frame()
        
        # Arama alanı
        ModernLabel(
            content, text="Genel Arama", style="muted",
            bg=self.colors['bg_card']
        ).pack(anchor=tk.W, pady=(0, 6))
        
        self.filter_entry = ModernEntry(content, placeholder="Ara...")
        self.filter_entry.pack(fill=tk.X, pady=(0, 12))
        self.filter_entry.bind('<KeyRelease>', self.callbacks.get('filtre_uygula'))
        
        # Filtreleri Temizle
        ModernButton(
            content,
            text="Filtreleri Temizle",
            icon="✖",
            command=self.callbacks.get('filtreleri_temizle'),
            style="secondary",
            width=296,
            height=36
        ).pack(fill=tk.X)
    
    def update_datakalem_label(self, text, success=False):
        """DataKalem label güncelle"""
        color = self.colors['success'] if success else self.colors['text_muted']
        self.datakalem_label.config(text=text, fg=color)
    
    def update_veri_label(self, text, success=False):
        """Veri label güncelle"""
        color = self.colors['success'] if success else self.colors['text_muted']
        self.veri_label.config(text=text, fg=color)
    
    def get_filter_text(self):
        """Filtre metnini al"""
        return self.filter_entry.get()
    
    def clear_filter(self):
        """Filtreyi temizle"""
        self.filter_entry.delete(0, tk.END)
    
    def reset_labels(self):
        """Etiketleri sıfırla"""
        self.update_datakalem_label("Seçilmedi", False)
        self.update_veri_label("Seçilmedi", False)


class RightPanel(tk.Frame):
    """Sağ sonuç paneli - Tablo görünümü"""
    
    def __init__(self, parent, on_column_click=None):
        self.colors = ModernTheme.COLORS
        self.fonts = ModernTheme.FONTS
        self.on_column_click = on_column_click
        
        super().__init__(parent, bg=self.colors['bg_primary'])
        
        self._create_result_card()
    
    def _create_result_card(self):
        """Sonuç kartı"""
        card = ModernCard(self, title="Arama Sonuçları", icon="📊")
        card.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        content = card.get_content_frame()
        
        # Tablo frame
        table_frame = tk.Frame(
            content,
            bg=self.colors['bg_primary'],
            highlightthickness=0,
            bd=0
        )
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(
            table_frame,
            show="headings",
            style="Modern.Treeview"
        )
        
        # Modern Scrollbar'lar
        self.v_scroll = ModernScrollbar(
            table_frame,
            command=self.tree.yview,
            orient="vertical"
        )
        self.h_scroll = ModernScrollbar(
            table_frame,
            command=self.tree.xview,
            orient="horizontal"
        )
        
        self.tree.configure(
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )
        
        # Mouse wheel scroll desteği
        def on_mousewheel(event):
            self.tree.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.tree.bind("<MouseWheel>", on_mousewheel)
        self.tree.bind("<Enter>", lambda e: self.tree.bind_all("<MouseWheel>", on_mousewheel))
        self.tree.bind("<Leave>", lambda e: self.tree.unbind_all("<MouseWheel>"))
        
        # Grid yerleşimi
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def show_data(self, df):
        """DataFrame'i tabloda göster"""
        # Önceki verileri temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if df is None or df.empty:
            return
        
        # Sütunları ayarla
        columns = list(df.columns)
        self.tree["columns"] = columns
        
        # Sütun başlıkları
        for col in columns:
            self.tree.heading(
                col,
                text=f"{col} ▼",
                command=lambda c=col: self._on_heading_click(c)
            )
            self.tree.column(col, width=140, minwidth=100)
        
        # Verileri ekle
        for _, row in df.iterrows():
            values = [str(row[col]) for col in columns]
            self.tree.insert("", "end", values=values)
    
    def _on_heading_click(self, column):
        """Sütun başlığına tıklandığında"""
        if self.on_column_click:
            self.on_column_click(column)
    
    def clear(self):
        """Tabloyu temizle"""
        for item in self.tree.get_children():
            self.tree.delete(item)

