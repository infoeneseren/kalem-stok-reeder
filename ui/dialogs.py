"""
Modern dialog ve popup bileşenleri
"""
import tkinter as tk
from .theme import ModernTheme
from .components import ModernButton


class ToastNotification(tk.Toplevel):
    """Modern toast bildirim - otomatik kapanan"""
    
    def __init__(self, parent, message, title="Bilgi", style="success", duration=2000):
        super().__init__(parent)
        
        self.colors = ModernTheme.COLORS
        self.fonts = ModernTheme.FONTS
        
        # Pencere ayarları
        self.overrideredirect(True)  # Çerçevesiz
        self.attributes('-topmost', True)
        self.configure(bg=self.colors['bg_card'])
        
        # Boyut ve konum
        width, height = 360, 100
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Stil renklerine göre ikon ve renk
        style_config = self._get_style_config(style)
        
        # Ana frame
        main_frame = tk.Frame(
            self,
            bg=self.colors['bg_card'],
            highlightbackground=style_config['color'],
            highlightthickness=2
        )
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # İçerik
        content = tk.Frame(main_frame, bg=self.colors['bg_card'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # İkon
        icon_label = tk.Label(
            content,
            text=style_config['icon'],
            font=self.fonts['icon_large'],
            fg=style_config['color'],
            bg=self.colors['bg_card']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 16))
        
        # Metin alanı
        text_frame = tk.Frame(content, bg=self.colors['bg_card'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Başlık
        tk.Label(
            text_frame,
            text=title,
            font=self.fonts['body_bold'],
            fg=self.colors['text_primary'],
            bg=self.colors['bg_card'],
            anchor='w'
        ).pack(fill=tk.X)
        
        # Mesaj
        tk.Label(
            text_frame,
            text=message,
            font=self.fonts['small'],
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_card'],
            anchor='w',
            wraplength=250
        ).pack(fill=tk.X)
        
        # Tıklama ile kapat
        self.bind("<Button-1>", lambda e: self.destroy())
        main_frame.bind("<Button-1>", lambda e: self.destroy())
        
        # Otomatik kapat
        self.after(duration, self.destroy)
    
    def _get_style_config(self, style):
        """Stil konfigürasyonu"""
        styles = {
            'success': {'icon': '✓', 'color': self.colors['success']},
            'error': {'icon': '✕', 'color': self.colors['error']},
            'warning': {'icon': '⚠', 'color': self.colors['warning']},
            'info': {'icon': 'ℹ', 'color': self.colors['info']},
        }
        return styles.get(style, styles['info'])


class FilterDialog(tk.Toplevel):
    """Modern filtre dialog penceresi"""
    
    def __init__(self, parent, column_name, values, selected_values=None, on_apply=None):
        super().__init__(parent)
        
        self.colors = ModernTheme.COLORS
        self.fonts = ModernTheme.FONTS
        self.on_apply = on_apply
        self.checkboxes = {}
        
        # Pencere ayarları
        self.title(f"{column_name} Filtresi")
        self.geometry("340x520")
        self.resizable(False, False)
        self.configure(bg=self.colors['bg_primary'])
        self.transient(parent)
        self.grab_set()
        
        # Pencereyi ortala
        x = parent.winfo_rootx() + 100
        y = parent.winfo_rooty() + 100
        self.geometry(f"+{x}+{y}")
        
        # Ana frame
        main_frame = tk.Frame(
            self,
            bg=self.colors['bg_card'],
            highlightbackground=self.colors['bg_tertiary'],
            highlightthickness=1,
            highlightcolor=self.colors['bg_tertiary'],
            bd=0
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Başlık
        self._create_header(main_frame, column_name)
        
        # Tümünü seç
        self._create_select_all(main_frame)
        
        # Checkbox listesi
        self._create_checkbox_list(main_frame, values, selected_values)
        
        # Butonlar
        self._create_buttons(main_frame)
    
    def _create_header(self, parent, column_name):
        """Başlık oluştur"""
        header = tk.Frame(parent, bg=self.colors['bg_card'])
        header.pack(fill=tk.X, padx=16, pady=(16, 8))
        
        tk.Label(
            header,
            text=f"🔽  {column_name}",
            font=self.fonts['heading'],
            fg=self.colors['text_primary'],
            bg=self.colors['bg_card']
        ).pack(side=tk.LEFT)
        
        # Ayırıcı çizgi
        divider = tk.Frame(parent, bg=self.colors['accent_primary'], height=2)
        divider.pack(fill=tk.X, padx=16, pady=(0, 12))
    
    def _create_select_all(self, parent):
        """Tümünü seç checkbox"""
        control_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        control_frame.pack(fill=tk.X, padx=16, pady=(0, 8))
        
        self.select_all_var = tk.BooleanVar(value=True)
        
        cb = tk.Checkbutton(
            control_frame,
            text="Tümünü Seç",
            variable=self.select_all_var,
            command=self._toggle_all,
            font=self.fonts['body_bold'],
            fg=self.colors['text_primary'],
            bg=self.colors['bg_card'],
            selectcolor=self.colors['bg_primary'],
            activebackground=self.colors['bg_card'],
            activeforeground=self.colors['text_primary']
        )
        cb.pack(side=tk.LEFT)
    
    def _create_checkbox_list(self, parent, values, selected_values):
        """Checkbox listesi"""
        list_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(
            list_frame,
            bg=self.colors['bg_primary'],
            highlightthickness=0,
            height=300
        )
        scrollbar = tk.Scrollbar(
            list_frame,
            orient="vertical",
            command=canvas.yview
        )
        
        scrollable = tk.Frame(canvas, bg=self.colors['bg_primary'])
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_frame = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def configure_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        canvas.bind('<Configure>', configure_canvas)
        
        # Mouse wheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable.bind("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Checkbox'lar
        for value in values:
            var = tk.BooleanVar()
            var.set(selected_values is None or value in selected_values)
            
            cb = tk.Checkbutton(
                scrollable,
                text=str(value),
                variable=var,
                font=self.fonts['small'],
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_primary'],
                selectcolor=self.colors['bg_secondary'],
                activebackground=self.colors['bg_primary'],
                activeforeground=self.colors['text_primary'],
                anchor='w'
            )
            cb.pack(fill=tk.X, padx=8, pady=2)
            self.checkboxes[value] = var
    
    def _create_buttons(self, parent):
        """Butonları oluştur"""
        btn_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        btn_frame.pack(fill=tk.X, padx=16, pady=(0, 16))
        
        # İptal butonu
        cancel_btn = ModernButton(
            btn_frame,
            text="İptal",
            command=self.destroy,
            style="secondary",
            width=130,
            height=36
        )
        cancel_btn.pack(side=tk.LEFT)
        
        # Uygula butonu
        apply_btn = ModernButton(
            btn_frame,
            text="Uygula",
            command=self._apply,
            style="success",
            width=130,
            height=36
        )
        apply_btn.pack(side=tk.RIGHT)
    
    def _toggle_all(self):
        """Tümünü seç/kaldır"""
        state = self.select_all_var.get()
        for var in self.checkboxes.values():
            var.set(state)
    
    def _apply(self):
        """Filtreyi uygula"""
        selected = [k for k, v in self.checkboxes.items() if v.get()]
        if self.on_apply:
            self.on_apply(selected)
        self.destroy()
    
    def get_selected(self):
        """Seçili değerleri döndür"""
        return [k for k, v in self.checkboxes.items() if v.get()]

