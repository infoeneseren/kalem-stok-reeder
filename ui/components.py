"""
Modern UI bileşenleri - Flutter/Material Design benzeri
"""
import tkinter as tk
from .theme import ModernTheme


class ModernButton(tk.Canvas):
    """Modern görünümlü buton - yuvarlak köşeli, hover efektli"""
    
    def __init__(self, parent, text="", icon=None, command=None, 
                 style="primary", width=None, height=40, **kwargs):
        
        self.colors = ModernTheme.COLORS
        self.fonts = ModernTheme.FONTS
        
        # Stil renklerini belirle
        self.style_colors = self._get_style_colors(style)
        
        # Canvas boyutları
        self.btn_width = width or 200
        self.btn_height = height
        
        super().__init__(
            parent,
            width=self.btn_width,
            height=self.btn_height,
            bg=parent.cget('bg') if hasattr(parent, 'cget') else self.colors['bg_card'],
            highlightthickness=0,
            **kwargs
        )
        
        self.command = command
        self.text = text
        self.icon = icon
        self.is_hovered = False
        self.is_pressed = False
        
        self._draw_button()
        self._bind_events()
    
    def _get_style_colors(self, style):
        """Buton stiline göre renkleri döndür"""
        styles = {
            'primary': {
                'bg': self.colors['btn_primary'],
                'bg_hover': self.colors['btn_primary_hover'],
                'fg': self.colors['text_primary']
            },
            'success': {
                'bg': self.colors['btn_success'],
                'bg_hover': self.colors['btn_success_hover'],
                'fg': self.colors['text_primary']
            },
            'danger': {
                'bg': self.colors['btn_danger'],
                'bg_hover': self.colors['btn_danger_hover'],
                'fg': self.colors['text_primary']
            },
            'secondary': {
                'bg': self.colors['btn_secondary'],
                'bg_hover': self.colors['btn_secondary_hover'],
                'fg': self.colors['text_primary']
            },
            'warning': {
                'bg': self.colors['warning'],
                'bg_hover': self.colors['warning_light'],
                'fg': self.colors['bg_primary']
            },
            'info': {
                'bg': self.colors['info'],
                'bg_hover': self.colors['info_light'],
                'fg': self.colors['text_primary']
            }
        }
        return styles.get(style, styles['primary'])
    
    def _draw_button(self):
        """Butonu çiz"""
        self.delete("all")
        
        r = 8  # Border radius
        w, h = self.btn_width, self.btn_height
        
        # Arka plan rengi
        bg_color = self.style_colors['bg_hover'] if self.is_hovered else self.style_colors['bg']
        
        # Yuvarlak köşeli dikdörtgen çiz
        self._create_rounded_rect(2, 2, w-2, h-2, r, fill=bg_color, outline="")
        
        # Metin
        display_text = f"{self.icon}  {self.text}" if self.icon else self.text
        self.create_text(
            w // 2, h // 2,
            text=display_text,
            fill=self.style_colors['fg'],
            font=self.fonts['button']
        )
    
    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """Yuvarlak köşeli dikdörtgen oluştur"""
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _bind_events(self):
        """Olayları bağla"""
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
    
    def _on_enter(self, event):
        self.is_hovered = True
        self.config(cursor="hand2")
        self._draw_button()
    
    def _on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self._draw_button()
    
    def _on_click(self, event):
        self.is_pressed = True
        self._draw_button()
    
    def _on_release(self, event):
        if self.is_pressed and self.command:
            self.command()
        self.is_pressed = False
        self._draw_button()


class ModernCard(tk.Frame):
    """Modern kart bileşeni - gölgeli, yuvarlak köşeli"""
    
    def __init__(self, parent, title=None, icon=None, **kwargs):
        self.colors = ModernTheme.COLORS
        self.fonts = ModernTheme.FONTS
        
        super().__init__(
            parent,
            bg=self.colors['bg_card'],
            highlightbackground=self.colors['bg_tertiary'],
            highlightthickness=1,
            highlightcolor=self.colors['bg_tertiary'],
            bd=0,
            **kwargs
        )
        
        if title:
            self._create_header(title, icon)
    
    def _create_header(self, title, icon):
        """Kart başlığı oluştur"""
        header = tk.Frame(self, bg=self.colors['bg_card'])
        header.pack(fill=tk.X, padx=16, pady=(16, 8))
        
        # Başlık metni
        title_text = f"{icon}  {title}" if icon else title
        tk.Label(
            header,
            text=title_text,
            font=self.fonts['heading'],
            fg=self.colors['text_primary'],
            bg=self.colors['bg_card']
        ).pack(side=tk.LEFT)
        
        # Alt çizgi
        divider = tk.Frame(self, bg=self.colors['accent_primary'], height=2)
        divider.pack(fill=tk.X, padx=16, pady=(0, 8))
    
    def get_content_frame(self):
        """İçerik frame'i döndür"""
        content = tk.Frame(self, bg=self.colors['bg_card'])
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        return content


class ModernEntry(tk.Frame):
    """Modern input alanı - placeholder, focus efektli"""
    
    def __init__(self, parent, placeholder="", **kwargs):
        self.colors = ModernTheme.COLORS
        self.fonts = ModernTheme.FONTS
        
        super().__init__(
            parent,
            bg=self.colors['bg_tertiary'],
            highlightthickness=0,
            bd=0
        )
        
        self.placeholder = placeholder
        self.has_focus = False
        
        # İç frame
        inner = tk.Frame(self, bg=self.colors['input_bg'], highlightthickness=0, bd=0)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Entry widget
        self.entry = tk.Entry(
            inner,
            font=self.fonts['body'],
            bg=self.colors['input_bg'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_primary'],
            relief=tk.FLAT,
            bd=0,
            **kwargs
        )
        self.entry.pack(fill=tk.X, padx=12, pady=10)
        
        # Placeholder göster
        if placeholder:
            self._show_placeholder()
        
        # Event'ler
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
    
    def _show_placeholder(self):
        """Placeholder göster"""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=self.colors['text_muted'])
    
    def _hide_placeholder(self):
        """Placeholder gizle"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self.colors['text_primary'])
    
    def _on_focus_in(self, event):
        self.has_focus = True
        self.config(bg=self.colors['accent_primary'])
        self._hide_placeholder()
    
    def _on_focus_out(self, event):
        self.has_focus = False
        self.config(bg=self.colors['bg_tertiary'])
        if self.placeholder:
            self._show_placeholder()
    
    def get(self):
        """Değeri al (placeholder hariç)"""
        value = self.entry.get()
        return "" if value == self.placeholder else value
    
    def delete(self, first, last):
        """İçeriği sil"""
        self.entry.delete(first, last)
    
    def bind(self, event, callback):
        """Event bağla"""
        self.entry.bind(event, callback)


class ModernLabel(tk.Label):
    """Modern etiket - önceden ayarlanmış stiller"""
    
    STYLES = {
        'title': {'font_key': 'title', 'color_key': 'text_primary'},
        'subtitle': {'font_key': 'subtitle', 'color_key': 'text_primary'},
        'heading': {'font_key': 'heading', 'color_key': 'text_primary'},
        'body': {'font_key': 'body', 'color_key': 'text_primary'},
        'secondary': {'font_key': 'body', 'color_key': 'text_secondary'},
        'muted': {'font_key': 'small', 'color_key': 'text_muted'},
        'success': {'font_key': 'body', 'color_key': 'success'},
        'error': {'font_key': 'body', 'color_key': 'error'},
        'warning': {'font_key': 'body', 'color_key': 'warning'},
    }
    
    def __init__(self, parent, text="", style="body", **kwargs):
        colors = ModernTheme.COLORS
        fonts = ModernTheme.FONTS
        
        style_config = self.STYLES.get(style, self.STYLES['body'])
        
        super().__init__(
            parent,
            text=text,
            font=fonts[style_config['font_key']],
            fg=colors[style_config['color_key']],
            bg=kwargs.pop('bg', colors['bg_card']),
            **kwargs
        )


class ModernScrollbar(tk.Canvas):
    """Modern özel scrollbar - yuvarlak köşeli, sürüklenebilir"""
    
    def __init__(self, parent, command=None, orient="vertical", **kwargs):
        self.colors = ModernTheme.COLORS
        self.orient = orient
        self.command = command
        
        # Boyutlar
        if orient == "vertical":
            width = 14
            super().__init__(parent, width=width, bg=self.colors['bg_primary'], 
                           highlightthickness=0, bd=0, **kwargs)
        else:
            height = 14
            super().__init__(parent, height=height, bg=self.colors['bg_primary'],
                           highlightthickness=0, bd=0, **kwargs)
        
        # Scrollbar durumu
        self.thumb_pos = 0.0
        self.thumb_size = 0.3
        self.dragging = False
        self.drag_start = 0
        self.drag_start_pos = 0
        self.is_hovered = False
        
        # Event'ler
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", lambda e: self._draw())
        
        self._draw()
    
    def set(self, first, last):
        """Scrollbar pozisyonunu ayarla"""
        self.thumb_pos = float(first)
        self.thumb_size = float(last) - float(first)
        if self.thumb_size < 0.08:
            self.thumb_size = 0.08
        self._draw()
    
    def _draw(self):
        """Scrollbar'ı çiz"""
        self.delete("all")
        
        w = self.winfo_width()
        h = self.winfo_height()
        
        if w <= 1 or h <= 1:
            return
        
        padding = 3
        radius = 5
        
        if self.orient == "vertical":
            # Track arka plan
            self._draw_rounded_rect(padding, padding, w-padding, h-padding, 
                                   radius, self.colors['bg_secondary'])
            
            # Thumb hesapla
            available_h = h - 2*padding
            thumb_h = max(40, available_h * self.thumb_size)
            thumb_y = padding + (available_h - thumb_h) * self.thumb_pos
            
            # Thumb rengi
            if self.dragging:
                thumb_color = self.colors['accent_secondary']
            elif self.is_hovered:
                thumb_color = self.colors['accent_primary']
            else:
                thumb_color = self.colors['bg_tertiary']
            
            # Thumb çiz
            self._draw_rounded_rect(padding+2, thumb_y+2, w-padding-2, thumb_y+thumb_h-2,
                                   radius, thumb_color)
        else:
            # Track arka plan
            self._draw_rounded_rect(padding, padding, w-padding, h-padding,
                                   radius, self.colors['bg_secondary'])
            
            # Thumb hesapla
            available_w = w - 2*padding
            thumb_w = max(40, available_w * self.thumb_size)
            thumb_x = padding + (available_w - thumb_w) * self.thumb_pos
            
            # Thumb rengi
            if self.dragging:
                thumb_color = self.colors['accent_secondary']
            elif self.is_hovered:
                thumb_color = self.colors['accent_primary']
            else:
                thumb_color = self.colors['bg_tertiary']
            
            # Thumb çiz
            self._draw_rounded_rect(thumb_x+2, padding+2, thumb_x+thumb_w-2, h-padding-2,
                                   radius, thumb_color)
    
    def _draw_rounded_rect(self, x1, y1, x2, y2, r, color):
        """Yuvarlak köşeli dikdörtgen"""
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        self.create_polygon(points, fill=color, smooth=True, outline="")
    
    def _on_click(self, event):
        """Tıklama başlat"""
        self.dragging = True
        self.config(cursor="hand2")
        
        if self.orient == "vertical":
            self.drag_start = event.y
            h = self.winfo_height()
            thumb_h = max(40, h * self.thumb_size)
            thumb_y = (h - thumb_h) * self.thumb_pos
            
            # Thumb dışına tıklandıysa, oraya atla
            if event.y < thumb_y or event.y > thumb_y + thumb_h:
                new_pos = event.y / h
                new_pos = max(0, min(1 - self.thumb_size, new_pos))
                self.thumb_pos = new_pos
                if self.command:
                    self.command("moveto", str(new_pos))
        else:
            self.drag_start = event.x
            w = self.winfo_width()
            thumb_w = max(40, w * self.thumb_size)
            thumb_x = (w - thumb_w) * self.thumb_pos
            
            if event.x < thumb_x or event.x > thumb_x + thumb_w:
                new_pos = event.x / w
                new_pos = max(0, min(1 - self.thumb_size, new_pos))
                self.thumb_pos = new_pos
                if self.command:
                    self.command("moveto", str(new_pos))
        
        self.drag_start_pos = self.thumb_pos
        self._draw()
    
    def _on_drag(self, event):
        """Sürükleme"""
        if not self.dragging:
            return
        
        if self.orient == "vertical":
            h = self.winfo_height()
            thumb_h = max(40, h * self.thumb_size)
            available = h - thumb_h
            if available > 0:
                delta = (event.y - self.drag_start) / available
                new_pos = self.drag_start_pos + delta
                new_pos = max(0, min(1 - self.thumb_size, new_pos))
                self.thumb_pos = new_pos
                if self.command:
                    self.command("moveto", str(new_pos))
        else:
            w = self.winfo_width()
            thumb_w = max(40, w * self.thumb_size)
            available = w - thumb_w
            if available > 0:
                delta = (event.x - self.drag_start) / available
                new_pos = self.drag_start_pos + delta
                new_pos = max(0, min(1 - self.thumb_size, new_pos))
                self.thumb_pos = new_pos
                if self.command:
                    self.command("moveto", str(new_pos))
        
        self._draw()
    
    def _on_release(self, event):
        """Bırakma"""
        self.dragging = False
        self.config(cursor="")
        self._draw()
    
    def _on_enter(self, event):
        """Mouse girdi"""
        self.is_hovered = True
        self.config(cursor="hand2")
        self._draw()
    
    def _on_leave(self, event):
        """Mouse çıktı"""
        if not self.dragging:
            self.is_hovered = False
            self.config(cursor="")
        self._draw()