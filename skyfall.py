import tkinter as tk
import random
import math
import winsound
import threading
import sys
import os

ANCHO = 900
ALTO = 600
NUM_ESTRELLAS = 180
PROB_METEORO = 0.003
PROB_TKM = 0.05


# ----------------------------------------------------------
# Función para obtener archivos dentro del .exe
# ----------------------------------------------------------
def ruta_recurso(nombre):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, nombre)
    return nombre


# ----------------------------------------------------------
# Música de fondo en loop
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
        self.reset(inicio_aleatorio=True)

    def reset(self, inicio_aleatorio=False):
        if inicio_aleatorio:
            self.x = random.randint(-ANCHO, ANCHO)
            self.y = random.randint(-ALTO, ALTO)
        else:
            self.x = random.randint(-200, -50)
            self.y = random.randint(-100, ALTO)

        self.velocidad = random.uniform(2.5, 5.5)
        self.dx = self.velocidad * 1.4
        self.dy = self.velocidad
        self.longitud = random.randint(8, 22)
        self.con_estela = random.random() < 0.35

        brillo = random.randint(200, 255)
        self.color = f"#{brillo:02x}{brillo:02x}ff"

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.x - self.longitud > ANCHO or self.y - self.longitud > ALTO:
            self.reset()

    def draw(self):
        x1 = self.x - (self.dx * self.longitud * (0.2 if self.con_estela else 1))
        y1 = self.y - (self.dy * self.longitud * (0.2 if self.con_estela else 1))
        x2 = self.x
        y2 = self.y

        self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=2)


# ----------------------------------------------------------
# Meteoro fugaz
# ----------------------------------------------------------
class Meteoro:
    def __init__(self, canvas):
        self.canvas = canvas
        self.spawn()

    def spawn(self):
        self.x = random.randint(-300, -50)
        self.y = random.randint(-50, ALTO - 50)
        self.velocidad = random.uniform(8, 14)
        self.dx = self.velocidad * 1.6
        self.dy = self.velocidad * 0.9
        self.longitud = random.randint(40, 90)
        self.color = "#ff4d7d"
        self.vida = random.randint(30, 55)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.vida -= 1

    def draw(self):
        x1 = self.x - self.dx * self.longitud
        y1 = self.y - self.dy * self.longitud
        x2 = self.x
        y2 = self.y

        self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=3)

    def terminado(self):
        fuera = self.x > ANCHO + 200 or self.y > ALTO + 200
        return self.vida <= 0 or fuera


# ----------------------------------------------------------
# Fondo
# ----------------------------------------------------------
def crear_fondo(canvas):
    for y in range(ALTO):
        t = y / ALTO
        r = int(6 * (1 - t) + 10 * t)
        g = int(8 * (1 - t) + 20 * t)
        b = int(25 * (1 - t) + 55 * t)
        canvas.create_line(0, y, ANCHO, y, fill=f"#{r:02x}{g:02x}{b:02x}")


# ----------------------------------------------------------
# Planeta orbitado
# ----------------------------------------------------------
class Planeta:
    def __init__(self, canvas):
        self.canvas = canvas
        self.radio = 160
        self.angulo = 0
        self.orbita_radio = 90

    def update(self):
        self.angulo = (self.angulo + 0.3) % 360

    def draw(self):
        ox = math.cos(math.radians(self.angulo)) * self.orbita_radio
        oy = math.sin(math.radians(self.angulo)) * self.orbita_radio

        cx = ANCHO // 2 + ox
        cy = ALTO // 2 + oy

        self.canvas.create_oval(cx - self.radio, cy - self.radio,
                                cx + self.radio, cy + self.radio,
                                fill="#0b0e1a", outline="")

        for i in range(1, 6):
            r = self.radio + i * 15
            self.canvas.create_oval(cx - r, cy - r,
                                    cx + r, cy + r,
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
        self.id_items = []

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
        for item in self.id_items:
            self.canvas.delete(item)
        self.id_items.clear()

        if self.fase == "in":
            alpha = min(1.0, self.t / 40)
        elif self.fase == "hold":
            alpha = 1.0
        else:
            alpha = max(0.0, 1 - self.t / 40)

        brillo = int(255 * alpha)
        color = f"#{brillo:02x}{80:02x}{80:02x}"

        for _ in range(30):
            px = self.cx + random.randint(-50, 50)
            py = self.cy + random.randint(-50, 50)
            size = random.randint(3, 8)
            self.id_items.append(
                self.canvas.create_rectangle(px, py, px + size, py + size,
                                             fill=color, outline="")
            )

        self.id_items.append(
            self.canvas.create_text(self.cx, self.cy,
                                    text="TKM",
                                    fill=color,
                                    font=("Arial", 28, "bold"))
        )


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------
def main():
    root = tk.Tk()
    root.title("TKM")

    canvas = tk.Canvas(root, width=ANCHO, height=ALTO)
    canvas.pack()

    estrellas = [Estrella(canvas) for _ in range(NUM_ESTRELLAS)]
    planeta = Planeta(canvas)
    meteoros = []
    evento_tkm = None

    def animar():
        nonlocal evento_tkm

        canvas.delete("all")
        crear_fondo(canvas)

        planeta.update()
        cx, cy = planeta.draw()

        for estrella in estrellas:
            estrella.update()
            estrella.draw()

        if random.random() < PROB_METEORO:
            meteoros.append(Meteoro(canvas))

        meteoros[:] = [m for m in meteoros if not m.terminado()]
        for m in meteoros:
            m.update()
            m.draw()

        if evento_tkm is None and random.random() < PROB_TKM:
            evento_tkm = EventoTKM(canvas, cx, cy)

        if evento_tkm:
            if evento_tkm.update():
                evento_tkm.draw()
            else:
                evento_tkm = None

        root.after(16, animar)

    animar()
    root.mainloop()


if __name__ == "__main__":
    main()
