import tkinter as tk
import random
import math
import winsound
import threading
import sys
import os

NUM_ESTRELLAS = 180
PROB_METEORO = 0.003
PROB_TKM = 0.05


# ----------------------------------------------------------
# Para cargar recursos (música) dentro del .exe
# ----------------------------------------------------------
def ruta_recurso(nombre):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, nombre)
    return nombre


# ----------------------------------------------------------
# Música en loop
# ----------------------------------------------------------
def reproducir_musica():
    ruta_audio = ruta_recurso("where_the_light_is.wav")
    winsound.PlaySound(ruta_audio, winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)


threading.Thread(target=reproducir_musica, daemon=True).start()


# ----------------------------------------------------------
# Estrella normal
# ----------------------------------------------------------
class Estrella:
    def __init__(self, canvas):
        self.canvas = canvas
        self.reset(True)

    def reset(self, full_random=False):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if full_random:
            self.x = random.randint(-w, w)
            self.y = random.randint(-h, h)
        else:
            self.x = random.randint(-200, -50)
            self.y = random.randint(-100, h)

        self.vel = random.uniform(2.5, 5.5)
        self.dx = self.vel * 1.4
        self.dy = self.vel
        self.longitud = random.randint(8, 22)
        self.estela = random.random() < 0.35

        b = random.randint(200, 255)
        self.color = f"#{b:02x}{b:02x}ff"

    def update(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        self.x += self.dx
        self.y += self.dy

        if self.x > w + 200 or self.y > h + 200:
            self.reset(False)

    def draw(self):
        x1 = self.x - self.dx * (self.longitud * (0.2 if self.estela else 1))
        y1 = self.y - self.dy * (self.longitud * (0.2 if self.estela else 1))
        self.canvas.create_line(x1, y1, self.x, self.y, fill=self.color, width=2)


# ----------------------------------------------------------
# Meteoro fugaz
# ----------------------------------------------------------
class Meteoro:
    def __init__(self, canvas):
        self.canvas = canvas
        self.spawn()

    def spawn(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        self.x = random.randint(-300, -50)
        self.y = random.randint(-50, h - 50)

        self.vel = random.uniform(8, 14)
        self.dx = self.vel * 1.6
        self.dy = self.vel * 0.9
        self.longitud = random.randint(40, 90)
        self.color = "#ff4d7d"
        self.alive = random.randint(30, 55)

    def update(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        self.x += self.dx
        self.y += self.dy
        self.alive -= 1

        return self.alive > 0 and self.x < w + 200 and self.y < h + 200

    def draw(self):
        x1 = self.x - self.dx * self.longitud
        y1 = self.y - self.dy * self.longitud
        self.canvas.create_line(x1, y1, self.x, self.y, fill=self.color, width=3)


# ----------------------------------------------------------
# Fondo responsivo
# ----------------------------------------------------------
def crear_fondo(canvas):
    w = canvas.winfo_width()
    h = canvas.winfo_height()

    for y in range(h):
        t = y / max(1, h)
        r = int(6 * (1 - t) + 10 * t)
        g = int(8 * (1 - t) + 20 * t)
        b = int(25 * (1 - t) + 55 * t)
        canvas.create_line(0, y, w, y, fill=f"#{r:02x}{g:02x}{b:02x}")


# ----------------------------------------------------------
# Planeta orbitado (responsivo)
# ----------------------------------------------------------
class Planeta:
    def __init__(self, canvas):
        self.canvas = canvas
        self.radio = 160
        self.angulo = 0
        self.orbita = 90

    def update(self):
        self.angulo = (self.angulo + 0.3) % 360

    def draw(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        cx = w // 2 + math.cos(math.radians(self.angulo)) * self.orbita
        cy = h // 2 + math.sin(math.radians(self.angulo)) * self.orbita

        self.canvas.create_oval(cx - self.radio, cy - self.radio,
                                cx + self.radio, cy + self.radio,
                                fill="#0b0e1a", outline="")

        for i in range(1, 6):
            r = self.radio + i * 15
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    fill="#0b0e1a", outline="")

        return cx, cy


# ----------------------------------------------------------
# Evento TKM
# ----------------------------------------------------------
class EventoTKM:
    def __init__(self, canvas, cx, cy):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.t = 0
        self.fase = "in"

    def update(self):
        self.t += 1
        if self.fase == "in" and self.t > 40:
            self.fase = "hold"; self.t = 0
        elif self.fase == "hold" and self.t > 40:
            self.fase = "out"; self.t = 0
        elif self.fase == "out" and self.t > 40:
            return False
        return True

    def draw(self):
        if self.fase == "in":
            a = min(1.0, self.t / 40)
        elif self.fase == "hold":
            a = 1.0
        else:
            a = max(0.0, 1 - self.t / 40)

        b = int(255 * a)
        color = f"#{b:02x}{80:02x}{80:02x}"

        for _ in range(30):
            px = self.cx + random.randint(-50, 50)
            py = self.cy + random.randint(-50, 50)
            size = random.randint(3, 8)
            self.canvas.create_rectangle(px, py, px + size, py + size, fill=color, outline="")

        self.canvas.create_text(self.cx, self.cy, text="TKM", fill=color, font=("Arial", 28, "bold"))


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------
def main():
    root = tk.Tk()
    root.title("Estrellas + Planeta + Meteoros + Música + TKM")
    root.state("zoomed")   # abre maximizado
    root.configure(bg="black")

    canvas = tk.Canvas(root, bg="black")
    canvas.pack(fill="both", expand=True)

    estrellas = []
    meteoros = []
    evento = None
    planeta = Planeta(canvas)

    # Inicializar cuando el canvas reporte dimensiones válidas
    def init_estrellas():
        if canvas.winfo_width() < 10:
            root.after(50, init_estrellas)
        else:
            for _ in range(NUM_ESTRELLAS):
                estrellas.append(Estrella(canvas))
    init_estrellas()

    def animar():
        nonlocal evento

        canvas.delete("all")
        crear_fondo(canvas)

        planeta.update()
        cx, cy = planeta.draw()

        for e in estrellas:
            e.update()
            e.draw()

        if random.random() < PROB_METEORO:
            meteoros.append(Meteoro(canvas))

        nuevos = []
        for m in meteoros:
            if m.update():
                m.draw()
                nuevos.append(m)
        meteoros[:] = nuevos

        if evento is None and random.random() < PROB_TKM:
            evento = EventoTKM(canvas, cx, cy)

        if evento:
            if evento.update():
                evento.draw()
            else:
                evento = None

        root.after(16, animar)

    animar()
    root.mainloop()


if __name__ == "__main__":
    main()
