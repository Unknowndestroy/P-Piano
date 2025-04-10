import pygame
import sys
import numpy as np
import tkinter as tk
from tkinter import filedialog

# Tkinter'ı arka planda başlatıp gizleyelim
tk_root = tk.Tk()
tk_root.withdraw()

# Pygame ayarları
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Piano Uygulaması - Döngüde Çalma Özelliği")
clock = pygame.time.Clock()

# Renk tanımları
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (200, 200, 200)
GREEN = (100, 255, 100)
RED   = (255, 100, 100)
BLUE  = (100, 100, 255)

# Global mod: eğer True ise ses yükleme modunda
sound_load_mode = False

# Butonlar için dikdörtgenler:
# Sağ üstte: Ses yükleme modunu değiştiren buton
load_button_rect = pygame.Rect(WIDTH - 110, 10, 100, 30)
# En altta: Varsayılan seslere sıfırlama butonu
default_button_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT - 40, 100, 30)

def generate_default_sound(frequency, duration=0.5, volume=0.5, sample_rate=44100):
    """
    Belirtilen frekansta duration süresinde sine dalgası üreterek pygame.Sound nesnesi döndürür.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * frequency * t)
    audio = wave * (2**15 - 1) * volume
    audio = audio.astype(np.int16)
    sound = pygame.mixer.Sound(buffer=audio.tobytes())
    return sound

class PianoKey:
    def __init__(self, x, y, width, height, note, label, frequency):
        self.rect = pygame.Rect(x, y, width, height)
        self.note = note       # Örneğin "C", "D", ...
        self.label = label     # Üzerinde gösterilecek harf
        self.frequency = frequency
        self.base_color = WHITE
        self.active_color = GREEN
        self.current_color = self.base_color
        # Öncelikle varsayılan sesi üretiyoruz.
        self.sound = generate_default_sound(frequency)
        # Döngüde çalan sesin durumunu kontrol etmek için bir flag
        self.is_playing_loop = False
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # kenarlık
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(self.label, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def activate(self):
        self.current_color = self.active_color
        # Döngüde çalması için loops=-1 kullanıyoruz
        if not sound_load_mode and not self.is_playing_loop:
            self.sound.play(loops=-1)
            self.is_playing_loop = True
                
    def deactivate(self):
        self.current_color = self.base_color
        if self.is_playing_loop:
            self.sound.stop()
            self.is_playing_loop = False
        
    def load_custom_sound(self):
        # Tkinter üzerinden dosya seçimi yapılıyor (yalnızca WAV desteği)
        file_path = filedialog.askopenfilename(
            title="{} için ses dosyası seç".format(self.label),
            filetypes=[("WAV Files", "*.wav"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                self.sound = pygame.mixer.Sound(file_path)
            except Exception as e:
                print("Ses dosyası yüklenirken hata oluştu:", e)

    def reset_default(self):
        # Varsayılan sesi yeniden üret
        self.sound = generate_default_sound(self.frequency)

# Piyano tuşlarını oluşturma
NUM_KEYS = 14  
keys = []
key_width = WIDTH // NUM_KEYS
key_height = 150
base_frequency = 220  
for i in range(NUM_KEYS):
    label = chr(65 + i)  # A, B, C, ... şeklinde etiketleniyor
    x = i * key_width
    frequency = base_frequency * (2 ** (i / 12))
    key = PianoKey(x, HEIGHT - key_height, key_width, key_height, note=label, label=label, frequency=frequency)
    keys.append(key)

# Düşen tek bir parçayı temsil eden sınıf
class FallingNote:
    def __init__(self, note, x, y=-50, speed=3):
        self.note = note
        self.x = x
        self.y = y
        self.speed = speed
        self.width = 40
        self.height = 40
        self.font = pygame.font.SysFont("Arial", 25)
        
    def update(self):
        self.y += self.speed
        
    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)
        text = self.font.render(self.note, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
        
# Global değişken: Sadece tek bir düşen parça var
falling_note = None

# Klavye tuşlarının piyano tuşlarıyla eşleştirilmesi (örneğin; A, S, D, ...)
keyboard_map = {
    pygame.K_a: 0,
    pygame.K_s: 1,
    pygame.K_d: 2,
    pygame.K_f: 3,
    pygame.K_g: 4,
    pygame.K_h: 5,
    pygame.K_j: 6,
    pygame.K_k: 7,
    pygame.K_l: 8,
    pygame.K_SEMICOLON: 9,
    pygame.K_QUOTE: 10,
}

def create_falling_note(note, x_center):
    global falling_note
    falling_note = FallingNote(note, x_center - 20)

# Ana döngü
running = True
while running:
    screen.fill(GRAY)
    
    # Butonları çizelim:
    pygame.draw.rect(screen, BLUE, load_button_rect)
    load_font = pygame.font.SysFont("Arial", 16)
    load_text = "Load Mode" if sound_load_mode else "Play Mode"
    load_render = load_font.render(load_text, True, WHITE)
    load_rect = load_render.get_rect(center=load_button_rect.center)
    screen.blit(load_render, load_rect)
    
    pygame.draw.rect(screen, BLUE, default_button_rect)
    default_font = pygame.font.SysFont("Arial", 16)
    default_render = default_font.render("Varsayılan", True, WHITE)
    default_rect = default_render.get_rect(center=default_button_rect.center)
    screen.blit(default_render, default_rect)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Sağ üst butona tıklanırsa mod değiştiriliyor.
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if load_button_rect.collidepoint(mouse_pos):
                sound_load_mode = not sound_load_mode
            elif default_button_rect.collidepoint(mouse_pos):
                for key in keys:
                    key.reset_default()
            else:
                for key in keys:
                    if key.rect.collidepoint(mouse_pos):
                        if sound_load_mode:
                            key.load_custom_sound()
                        else:
                            key.activate()
                            if falling_note is None:
                                note_letter = key.label
                                note_x = key.rect.x + key.rect.width / 2
                                create_falling_note(note_letter, note_x)
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = event.pos
            for key in keys:
                if key.rect.collidepoint(mouse_pos):
                    key.deactivate()
                    
        # Klavye ile çalma
        if event.type == pygame.KEYDOWN:
            if event.key in keyboard_map:
                idx = keyboard_map[event.key]
                if idx < len(keys):
                    if sound_load_mode:
                        keys[idx].load_custom_sound()
                    else:
                        keys[idx].activate()
                        if falling_note is None:
                            note_letter = keys[idx].label
                            note_x = keys[idx].rect.x + keys[idx].rect.width / 2
                            create_falling_note(note_letter, note_x)
        if event.type == pygame.KEYUP:
            if event.key in keyboard_map:
                idx = keyboard_map[event.key]
                if idx < len(keys):
                    keys[idx].deactivate()
                    
    # Düşen notanın güncellenmesi ve çizilmesi
    if falling_note:
        falling_note.update()
        falling_note.draw(screen)
        if falling_note.y > HEIGHT:
            falling_note = None

    for key in keys:
        key.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
sys.exit()
