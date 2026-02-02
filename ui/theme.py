"""
Modern tema ayarları - Flutter/Material Design benzeri
"""
import tkinter as tk
from tkinter import ttk


class ModernTheme:
    """Modern renk paleti ve font ayarları"""
    
    # Ana renkler - Kullanıcı renkleri: #79d84b (yeşil) #051c2c (koyu lacivert)
    COLORS = {
        # Arka plan renkleri
        'bg_primary': '#051c2c',        # En koyu arka plan
        'bg_secondary': '#072a40',      # Orta arka plan
        'bg_tertiary': '#0a3654',       # Açık arka plan
        'bg_card': '#0a2e47',           # Kart arka planı
        
        # Vurgu renkleri
        'accent_primary': '#79d84b',    # Ana vurgu (yeşil)
        'accent_secondary': '#8fe05f',  # İkincil vurgu (açık yeşil)
        'accent_gradient_start': '#79d84b',
        'accent_gradient_end': '#5bc236',
        
        # Durum renkleri
        'success': '#79d84b',           # Yeşil
        'success_light': '#8fe05f',
        'warning': '#f59e0b',           # Turuncu
        'warning_light': '#fbbf24',
        'error': '#ef4444',             # Kırmızı
        'error_light': '#f87171',
        'info': '#3b82f6',              # Mavi
        'info_light': '#60a5fa',
        
        # Metin renkleri
        'text_primary': '#f8fafc',      # Ana metin (beyaz)
        'text_secondary': '#94a3b8',    # İkincil metin
        'text_muted': '#64748b',        # Soluk metin
        'text_disabled': '#475569',     # Devre dışı metin
        
        # Çerçeve ve bölücü
        'border': '#0a3654',
        'border_light': '#0d4a6e',
        'divider': '#072a40',
        
        # Buton renkleri
        'btn_primary': '#79d84b',
        'btn_primary_hover': '#8fe05f',
        'btn_success': '#79d84b',
        'btn_success_hover': '#8fe05f',
        'btn_danger': '#ef4444',
        'btn_danger_hover': '#f87171',
        'btn_secondary': '#0a3654',
        'btn_secondary_hover': '#0d4a6e',
        
        # Tablo renkleri
        'table_header': '#072a40',
        'table_row': '#051c2c',
        'table_row_alt': '#072a40',
        'table_selected': '#79d84b',
        
        # Input renkleri
        'input_bg': '#051c2c',
        'input_border': '#0a3654',
        'input_focus': '#79d84b',
    }
    
    # Font ayarları
    FONTS = {
        'title': ('Segoe UI', 18, 'bold'),
        'subtitle': ('Segoe UI', 14, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'body_bold': ('Segoe UI', 10, 'bold'),
        'small': ('Segoe UI', 9),
        'tiny': ('Segoe UI', 8),
        'button': ('Segoe UI', 10, 'bold'),
        'icon': ('Segoe UI Emoji', 16),
        'icon_large': ('Segoe UI Emoji', 24),
    }
    
    # Boyut sabitleri
    SIZES = {
        'padding_xs': 4,
        'padding_sm': 8,
        'padding_md': 12,
        'padding_lg': 16,
        'padding_xl': 24,
        'border_radius': 8,
        'button_height': 40,
        'input_height': 38,
        'card_padding': 16,
    }
    
    @classmethod
    def apply_styles(cls, root):
        """ttk widget stillerini uygula"""
        style = ttk.Style(root)
        style.theme_use('clam')
        
        # Treeview stili
        style.configure(
            "Modern.Treeview",
            background=cls.COLORS['table_row'],
            foreground=cls.COLORS['text_primary'],
            fieldbackground=cls.COLORS['table_row'],
            borderwidth=0,
            font=cls.FONTS['body'],
            rowheight=36
        )
        style.configure(
            "Modern.Treeview.Heading",
            background=cls.COLORS['table_header'],
            foreground=cls.COLORS['text_primary'],
            borderwidth=0,
            font=cls.FONTS['body_bold'],
            relief='flat',
            padding=(10, 8)
        )
        style.map("Modern.Treeview",
            background=[('selected', cls.COLORS['table_selected'])],
            foreground=[('selected', cls.COLORS['text_primary'])]
        )
        style.map("Modern.Treeview.Heading",
            background=[('active', cls.COLORS['bg_tertiary'])]
        )
        
        # Modern Scrollbar stili - daha belirgin ve şık
        style.layout("Modern.Vertical.TScrollbar", [
            ("Modern.Vertical.TScrollbar.trough", {
                "children": [
                    ("Modern.Vertical.TScrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                ],
                "sticky": "ns"
            })
        ])
        
        style.layout("Modern.Horizontal.TScrollbar", [
            ("Modern.Horizontal.TScrollbar.trough", {
                "children": [
                    ("Modern.Horizontal.TScrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                ],
                "sticky": "ew"
            })
        ])
        
        style.configure(
            "Modern.Vertical.TScrollbar",
            background=cls.COLORS['accent_primary'],
            troughcolor=cls.COLORS['bg_secondary'],
            bordercolor=cls.COLORS['bg_secondary'],
            lightcolor=cls.COLORS['accent_primary'],
            darkcolor=cls.COLORS['accent_primary'],
            borderwidth=0,
            arrowsize=0,
            width=14,
            relief='flat'
        )
        style.map("Modern.Vertical.TScrollbar",
            background=[
                ('pressed', cls.COLORS['accent_secondary']),
                ('active', cls.COLORS['accent_secondary']),
                ('!disabled', cls.COLORS['accent_primary'])
            ]
        )
        
        style.configure(
            "Modern.Horizontal.TScrollbar",
            background=cls.COLORS['accent_primary'],
            troughcolor=cls.COLORS['bg_secondary'],
            bordercolor=cls.COLORS['bg_secondary'],
            lightcolor=cls.COLORS['accent_primary'],
            darkcolor=cls.COLORS['accent_primary'],
            borderwidth=0,
            arrowsize=0,
            width=14,
            relief='flat'
        )
        style.map("Modern.Horizontal.TScrollbar",
            background=[
                ('pressed', cls.COLORS['accent_secondary']),
                ('active', cls.COLORS['accent_secondary']),
                ('!disabled', cls.COLORS['accent_primary'])
            ]
        )
        
        # Frame border'larını kaldır
        style.configure("TFrame", background=cls.COLORS['bg_primary'], borderwidth=0)
        style.configure("TLabelframe", background=cls.COLORS['bg_card'], borderwidth=0)
        
        return style

