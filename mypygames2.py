import pygame
import random
import sys

# --- Inisialisasi ---
pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4 Box Aritmatika - Mega's Memory Edition")

# Font
font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 60)
clock = pygame.time.Clock()

# --- Warna Tema Malam ---
BG_TOP = (10, 10, 30)
BG_BOTTOM = (25, 25, 60)
BOX_COLOR = (40, 60, 120)
GLOW_COLOR = (80, 120, 255)
WHITE = (230, 230, 255)
GREEN = (0, 255, 150)
RED = (255, 80, 80)

# --- ☁️ Setup Background Megamendung ---
try:
    img_ori = pygame.image.load("megamendung.png").convert_alpha()
    bg_cloud = pygame.transform.scale(img_ori, (300, 180))
    bg_cloud.set_alpha(70) # Transparansi agar tidak menutupi teks
except:
    bg_cloud = None
    print("Info: megamendung.png tidak ditemukan, lanjut tanpa background.")

# ---------- Utility ----------
def draw_gradient():
    # Gambar langit malam
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * ratio
        g = BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * ratio
        b = BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * ratio
        pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (WIDTH, y))
    
    # Gambar Megamendung di belakang
    if bg_cloud:
        screen.blit(bg_cloud, (20, 50))    # Kiri atas
        screen.blit(bg_cloud, (550, 70))   # Kanan atas
        screen.blit(bg_cloud, (280, 420))  # Tengah bawah

def ease_out(t):
    return 1 - (1 - t) * (1 - t)

# ---------- Game Logic ----------
def buat_soal(level):
    a = random.randint(1, 10 + level*2)
    b = random.randint(1, 10 + level*2)
    op = random.choice(["+", "-", "*"]) 
    if op == "+": hasil = a + b
    elif op == "-": hasil = a - b
    elif op == "*": hasil = a * b
    return f"{a} {op} {b}", hasil

def buat_pilihan(jawaban):
    pilihan = [jawaban]
    while len(pilihan) < 4:
        salah = jawaban + random.randint(-15, 15)
        if salah != jawaban and salah not in pilihan:
            pilihan.append(salah)
    # Jangan di-shuffle dulu agar kita tahu posisi awalnya
    return pilihan

# ---------- Box Class ----------
class Box:
    def __init__(self, x, y, value):
        self.rect = pygame.Rect(x, y, 150, 150)
        self.start_x = x
        self.target_x = x
        self.value = value
        self.revealed = False
        self.anim_time = 0

    def move_to(self, new_x):
        self.start_x = self.rect.x
        self.target_x = new_x
        self.anim_time = 0

    def update(self, dt):
        if self.rect.x != self.target_x:
            self.anim_time += dt
            t = min(self.anim_time / 0.6, 1) # Durasi animasi geser 0.6 detik
            self.rect.x = self.start_x + (self.target_x - self.start_x) * ease_out(t)

    def draw(self):
        # Efek Cahaya (Glow)
        glow_rect = self.rect.inflate(15, 15)
        pygame.draw.rect(screen, GLOW_COLOR, glow_rect, border_radius=20)
        pygame.draw.rect(screen, BOX_COLOR, self.rect, border_radius=20)

        # Isi Kotak
        text_val = str(self.value) if self.revealed else "?"
        img = big_font.render(text_val, True, WHITE)
        text_rect = img.get_rect(center=self.rect.center)
        screen.blit(img, text_rect)

# ---------- Main Game ----------
def main():
    level = 1
    skor = 0
    timer_max = 15

    running = True
    while running:
        soal, jawaban = buat_soal(level)
        pilihan = buat_pilihan(jawaban)

        boxes = []
        start_pos_x = 100
        for i in range(4):
            # Letakkan kotak secara berurutan sesuai list pilihan
            boxes.append(Box(start_pos_x + i*185, 360, pilihan[i]))

        # --- TAHAP 1: Hafalkan (Hanya Angka, Tanpa Soal) ---
        pilihan = buat_pilihan(jawaban)
        random.shuffle(pilihan)  # <--- TAMBAHKAN BARIS INI UNTUK MENGACAK POSISI

        boxes = []
        start_pos_x = 100
        for i in range(4):
            # Sekarang pilihan[i] sudah teracak posisinya
            boxes.append(Box(start_pos_x + i*185, 360, pilihan[i]))
        
        for box in boxes: box.revealed = True
        
        start_memori = pygame.time.get_ticks()
        sedang_menghafal = True
        
        while sedang_menghafal:
            draw_gradient()
            
            # Teks Instruksi
            lbl = font.render("HAFALKAN POSISI ANGKA!", True, GREEN)
            screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 100))
            
            # UI Info
            screen.blit(font.render(f"Level: {level}", True, WHITE), (40, 30))
            screen.blit(font.render(f"Skor: {skor}", True, WHITE), (40, 60))

            for box in boxes: box.draw()
            pygame.display.flip()
            
            # Waktu hafal 2.5 detik
            if pygame.time.get_ticks() - start_memori > 2500:
                sedang_menghafal = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

        # --- TAHAP 2: Tutup & Acak (Shuffle) ---
        for box in boxes: box.revealed = False
        
        # Tunggu animasi shuffle selesai
        anim_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - anim_start < 1000:
            dt = clock.tick(60) / 1000
            draw_gradient()
            for box in boxes:
                box.update(dt)
                box.draw()
            pygame.display.flip()

        # --- TAHAP 3: Menebak (Soal Muncul) ---
        waktu_mulai = pygame.time.get_ticks()
        answered = False
        result_text = ""

        while not answered:
            dt = clock.tick(60) / 1000
            draw_gradient()

            sisa = timer_max - (pygame.time.get_ticks() - waktu_mulai)//1000
            if sisa <= 0:
                result_text = "WAKTU HABIS!"
                answered = True
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for box in boxes:
                        if box.rect.collidepoint(event.pos) and not box.revealed:
                            box.revealed = True
                            answered = True
                            if box.value == jawaban:
                                skor += 10 * level
                                level += 1
                                result_text = "BENAR!"
                            else:
                                result_text = "SALAH!"

            for box in boxes:
                box.update(dt)
                box.draw()

            # Munculkan Soal HANYA di tahap ini
            lbl_soal = font.render("BERAPAKAH HASIL DARI:", True, WHITE)
            screen.blit(lbl_soal, (WIDTH//2 - lbl_soal.get_width()//2, 160))
            txt_soal = big_font.render(soal, True, GLOW_COLOR)
            screen.blit(txt_soal, (WIDTH//2 - txt_soal.get_width()//2, 210))

            # UI Update
            screen.blit(font.render(f"Level: {level}", True, WHITE), (40, 30))
            screen.blit(font.render(f"Skor: {skor}", True, WHITE), (40, 60))
            screen.blit(font.render(f"Waktu: {sisa}", True, RED), (760, 30))

            pygame.display.flip()

        # --- Hasil Ronde ---
        for box in boxes: box.revealed = True
        draw_gradient()
        warna_res = GREEN if result_text == "BENAR!" else RED
        res_img = big_font.render(result_text, True, warna_res)
        screen.blit(res_img, (WIDTH//2 - res_img.get_width()//2, 280))
        for box in boxes: box.draw()
        pygame.display.flip()
        pygame.time.delay(1500)

        if result_text != "BENAR!":
            running = False

    # Game Over
    draw_gradient()
    screen.blit(big_font.render("GAME OVER", True, RED), (300, 250))
    screen.blit(font.render(f"Skor Akhir: {skor}", True, WHITE), (380, 330))
    pygame.display.flip()
    pygame.time.delay(3000)
    pygame.quit()

if __name__ == "__main__":
    main()