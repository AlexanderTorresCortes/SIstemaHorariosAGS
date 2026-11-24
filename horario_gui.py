import math
import tkinter as tk

import ags_nucleo as ags

# ---------------------------------------------------------------------------
# COLORES Y FUENTES
# ---------------------------------------------------------------------------
BG = "#0b1020"
PANEL = "#141b34"
PANEL2 = "#1b2447"
LINEA = "#2b3566"
TEXTO = "#e8ecff"
APAGADO = "#8b95c9"
CIAN = "#22d3ee"
VERDE = "#34d399"
AMBAR = "#fbbf24"
ROJO = "#fb7185"
VIOLETA = "#a78bfa"
AZUL = "#60a5fa"
NARANJA = "#fb923c"
ROSA = "#f472b6"

COLOR_MATERIA = [AZUL, VIOLETA, VERDE, AMBAR]     # un color por materia
COLOR_PADRE1 = "#38bdf8"
COLOR_PADRE2 = NARANJA
COLORES_RULETA = ["#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa", "#fb923c",
                  "#22d3ee", "#f87171", "#a3e635", "#e879f9", "#2dd4bf", "#facc15"]

FUENTE = "Segoe UI"
MONO = "Consolas"

ANCHO_TABLA = 800      # ancho de la tabla de individuos
CELDA = 19             # tamaño de cada bit dibujado
PASO_BIT = CELDA + 2   # separación entre bits
HUECO_GRUPO = 8        # separación extra entre grupos de 3 bits
ANCHO_BITS = ags.LONGITUD * PASO_BIT + (len(ags.MATERIAS) - 1) * HUECO_GRUPO


# ---------------------------------------------------------------------------
# UTILIDADES DE DIBUJO
# ---------------------------------------------------------------------------
def mezclar(c1, c2, t):
    """Mezcla dos colores hex: t=0 -> c1, t=1 -> c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    r = [int(a[k] + (b[k] - a[k]) * t) for k in range(3)]
    return "#%02x%02x%02x" % (r[0], r[1], r[2])


def rect_red(cv, x1, y1, x2, y2, r=8, **kw):
    """Rectángulo con esquinas redondeadas (polígono suavizado)."""
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
           x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
           x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, **kw)


def x_bit(x0, i):
    """Coordenada x del bit número i (0 a 11) cuando la fila empieza en x0."""
    return x0 + i * PASO_BIT + (i // ags.BITS_POR_MATERIA) * HUECO_GRUPO


def x_corte(x0, punto):
    """Coordenada x de la línea de corte entre el bit punto-1 y el bit punto."""
    if punto % ags.BITS_POR_MATERIA == 0:
        return x_bit(x0, punto) - (HUECO_GRUPO + 2) / 2
    return x_bit(x0, punto) - 1


def dibujar_bits(cv, x, y, bits, colores=None, resaltar=(), oculto=False):
    """Dibuja un cromosoma como 12 casillas (un color por materia)."""
    for i, b in enumerate(bits):
        cx = x_bit(x, i)
        base = colores[i] if colores else COLOR_MATERIA[i // ags.BITS_POR_MATERIA]
        marcado = i in resaltar
        if oculto:
            rect_red(cv, cx, y, cx + CELDA, y + CELDA, 5, fill=PANEL2, outline=LINEA, width=1)
            cv.create_text(cx + CELDA / 2, y + CELDA / 2, text="?", fill=APAGADO,
                           font=(MONO, 10, "bold"))
            continue
        relleno = base if b else mezclar(base, BG, 0.72)
        rect_red(cv, cx, y, cx + CELDA, y + CELDA, 5, fill=relleno,
                 outline=ROJO if marcado else mezclar(base, BG, 0.3),
                 width=3 if marcado else 1)
        cv.create_text(cx + CELDA / 2, y + CELDA / 2, text=str(b),
                       fill=BG if b else mezclar(base, TEXTO, 0.35),
                       font=(MONO, 10, "bold"))


def color_fitness(f):
    """Rojo (fitness bajo) -> ámbar -> verde (fitness alto)."""
    if f < 0.5:
        return mezclar(ROJO, AMBAR, f * 2)
    return mezclar(AMBAR, VERDE, (f - 0.5) * 2)


def color_diferencia(dif):
    """Verde si la materia está bien, ámbar si falla por 1 hora, rojo si falla más."""
    if dif == 0:
        return VERDE
    return AMBAR if dif == 1 else ROJO


def dibujar_horas(cv, x, y, horas, ancho=38, alto=10):
    """Cuatro barritas (una por materia). La marca blanca indica las horas necesarias."""
    for k, h in enumerate(horas):
        bx = x + k * (ancho + 26)
        col = color_diferencia(abs(h - ags.HORAS_NECESARIAS[k]))
        cv.create_rectangle(bx, y, bx + ancho, y + alto, fill=PANEL2, outline="")
        if h > 0:
            cv.create_rectangle(bx, y, bx + ancho * h / ags.HORAS_MAXIMAS, y + alto,
                                fill=col, outline="")
        xm = bx + ancho * ags.HORAS_NECESARIAS[k] / ags.HORAS_MAXIMAS
        cv.create_line(xm, y - 3, xm, y + alto + 3, fill=TEXTO, width=2)
        cv.create_text(bx + ancho + 5, y + alto / 2, text=str(h), anchor="w",
                       fill=col, font=(FUENTE, 10, "bold"))


def boton(padre, texto, comando, color=CIAN, fg=BG, tam=11, ancho=0):
    """Botón plano con efecto al pasar el mouse."""
    b = tk.Button(padre, text=texto, command=comando, bg=color, fg=fg,
                  activebackground=mezclar(color, "#ffffff", 0.25), activeforeground=fg,
                  disabledforeground=mezclar(fg, color, 0.5),
                  relief="flat", bd=0, padx=16, pady=8, cursor="hand2",
                  font=(FUENTE, tam, "bold"))
    if ancho:
        b.config(width=ancho)
    b.bind("<Enter>", lambda e: b.config(bg=mezclar(color, "#ffffff", 0.18)))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b


class PantallaBase(tk.Frame):
    """Clase base: anima con 'despues' sin fallar si la pantalla ya se cerró."""

    def __init__(self, app):
        super().__init__(app.contenedor, bg=BG)
        self.app = app
        self.vivo = True
        self.epoca = 0          # sube al reiniciar: invalida animaciones viejas

    def despues(self, ms, funcion):
        epoca = self.epoca

        def envoltura():
            if self.vivo and epoca == self.epoca:
                funcion()
        return self.after(ms, envoltura)

    def destroy(self):
        self.vivo = False
        super().destroy()


# ===========================================================================
# PANTALLA 1: MENÚ DE INICIO
# ===========================================================================
class PantallaMenu(PantallaBase):
    def __init__(self, app):
        super().__init__(app)
        tarjeta = tk.Frame(self, bg=PANEL, highlightbackground=LINEA, highlightthickness=1)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(tarjeta, text="ALGORITMO GENÉTICO SIMPLE", bg=PANEL, fg=CIAN,
                 font=(FUENTE, 26, "bold")).pack(padx=60, pady=(30, 0))
        tk.Label(tarjeta, text="Optimización de un horario de estudio semanal", bg=PANEL,
                 fg=TEXTO, font=(FUENTE, 13)).pack()
        tk.Label(tarjeta, text="Inteligencia Artificial", bg=PANEL, fg=APAGADO,
                 font=(FUENTE, 11, "italic")).pack(pady=(0, 22))

        opciones = [
            ("Paso a paso animado", self.app.mostrar_paso, CIAN),
            ("Ejemplo del anteproyecto (A, B, C, D)", self.app.mostrar_ejemplo, PANEL2),
            ("Ejecución automática con gráfica", self.app.mostrar_auto, PANEL2),
            ("Parámetros", self.app.mostrar_parametros, PANEL2),
            ("Salir", self.app.destroy, PANEL2),
        ]
        for texto, comando, color in opciones:
            b = boton(tarjeta, texto, comando, color=color,
                      fg=BG if color == CIAN else TEXTO, tam=13, ancho=38)
            b.pack(padx=60, pady=6)
        tk.Label(tarjeta, text="12 bits por individuo  ·  3 bits por materia  ·  "
                               "fitness = 1 / (1 + error)", bg=PANEL, fg=APAGADO,
                 font=(MONO, 10)).pack(pady=(18, 26))


# ===========================================================================
# PANTALLA 2: PARÁMETROS
# ===========================================================================
class PantallaParametros(PantallaBase):
    def __init__(self, app):
        super().__init__(app)
        tarjeta = tk.Frame(self, bg=PANEL, highlightbackground=LINEA, highlightthickness=1)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(tarjeta, text="Parámetros", bg=PANEL, fg=CIAN,
                 font=(FUENTE, 22, "bold")).pack(padx=60, pady=(26, 14))

        p = app.params
        self.controles = {}
        definiciones = [
            ("n_visual", "Individuos en el modo paso a paso", 4, 12, 1),
            ("n_auto", "Individuos en la ejecución automática", 10, 100, 1),
            ("generaciones", "Máximo de generaciones (automático)", 10, 300, 10),
            ("p_cruce", "Probabilidad de cruce", 0.1, 1.0, 0.05),
            ("p_mutacion", "Probabilidad de mutación por bit", 0.0, 0.2, 0.01),
        ]
        for clave, texto, minimo, maximo, paso in definiciones:
            tk.Label(tarjeta, text=texto, bg=PANEL, fg=TEXTO,
                     font=(FUENTE, 11)).pack(anchor="w", padx=60)
            s = tk.Scale(tarjeta, from_=minimo, to=maximo, resolution=paso, orient="horizontal",
                         length=420, bg=PANEL, fg=CIAN, troughcolor=BG, highlightthickness=0,
                         activebackground=CIAN, font=(FUENTE, 10, "bold"))
            s.set(p[clave])
            s.pack(padx=60, pady=(0, 6))
            self.controles[clave] = s

        fila = tk.Frame(tarjeta, bg=PANEL)
        fila.pack(pady=(16, 26))
        boton(fila, "Guardar y volver", self.guardar, color=VERDE).pack(side="left", padx=8)
        boton(fila, "Restaurar valores", self.restaurar, color=PANEL2, fg=TEXTO).pack(side="left", padx=8)

    def guardar(self):
        for clave, s in self.controles.items():
            valor = s.get()
            self.app.params[clave] = int(valor) if clave in ("n_visual", "n_auto", "generaciones") \
                else round(float(valor), 2)
        self.app.mostrar_menu()

    def restaurar(self):
        for clave, s in self.controles.items():
            s.set(ags.PARAMETROS_INICIALES[clave])


# ===========================================================================
# PANTALLA 3: PASO A PASO ANIMADO
# ===========================================================================
class PantallaPaso(PantallaBase):
    FASES = ["poblacion", "evaluacion", "seleccion", "cruce", "mutacion", "reemplazo"]
    TITULOS = {"poblacion": "1 · Población", "evaluacion": "2 · Evaluación",
               "seleccion": "3 · Selección", "cruce": "4 · Cruce",
               "mutacion": "5 · Mutación", "reemplazo": "6 · Nueva generación"}
    ETIQUETAS = {"poblacion": "Población", "evaluacion": "Evaluación",
                 "seleccion": "Selección", "cruce": "Cruce",
                 "mutacion": "Mutación", "reemplazo": "Reemplazo"}

    def __init__(self, app, ejemplo=False):
        super().__init__(app)
        self.ejemplo = ejemplo
        self._construir()
        self.app.bind("<Right>", lambda e: self.siguiente())
        self.app.bind("<Return>", lambda e: self.siguiente())
        self.app.bind("<Escape>", lambda e: self.app.mostrar_menu())
        self.reiniciar()

    # ----------------------------------------------------------- interfaz --
    def _construir(self):
        # Barra inferior (se empaqueta primero para que siempre se vea)
        barra = tk.Frame(self, bg=PANEL, height=64)
        barra.pack(side="bottom", fill="x")
        boton(barra, "☰  Menú", self.app.mostrar_menu, color=PANEL2, fg=TEXTO).pack(side="left", padx=(14, 6), pady=10)
        boton(barra, "⟲  Reiniciar", self.reiniciar, color=PANEL2, fg=TEXTO).pack(side="left", padx=6, pady=10)
        self.btn_sig = boton(barra, "Siguiente paso  ▶", self.siguiente, color=CIAN, tam=12)
        self.btn_sig.pack(side="left", padx=(24, 6), pady=10)
        self.btn_auto = boton(barra, "▶▶  Automático", self.alternar_auto, color=VERDE, tam=11)
        self.btn_auto.pack(side="left", padx=6, pady=10)
        tk.Label(barra, text="Velocidad", bg=PANEL, fg=APAGADO, font=(FUENTE, 10)).pack(side="left", padx=(16, 2))
        self.vel = tk.Scale(barra, from_=1, to=5, orient="horizontal", showvalue=False, length=110,
                            bg=PANEL, troughcolor=BG, highlightthickness=0, activebackground=CIAN)
        self.vel.set(3)
        self.vel.pack(side="left")
        self.lbl_info = tk.Label(barra, text="", bg=PANEL, fg=TEXTO, font=(FUENTE, 11, "bold"))
        self.lbl_info.pack(side="right", padx=16)

        # Indicador de etapas (arriba)
        self.cv_pasos = tk.Canvas(self, height=62, bg=BG, highlightthickness=0)
        self.cv_pasos.pack(side="top", fill="x")

        # Panel derecho
        der = tk.Frame(self, bg=PANEL, width=340)
        der.pack(side="right", fill="y", padx=(6, 8), pady=(0, 8))
        der.pack_propagate(False)
        self.lbl_fase = tk.Label(der, text="", bg=PANEL, fg=CIAN, font=(FUENTE, 14, "bold"), anchor="w")
        self.lbl_fase.pack(fill="x", padx=12, pady=(10, 2))
        self.lbl_exp = tk.Label(der, text="", bg=PANEL, fg=TEXTO, font=(FUENTE, 10),
                                wraplength=312, justify="left", anchor="nw", height=10)
        self.lbl_exp.pack(fill="x", padx=12)
        tk.Label(der, text="Evolución del fitness", bg=PANEL, fg=APAGADO,
                 font=(FUENTE, 9, "bold"), anchor="w").pack(fill="x", padx=12, pady=(6, 0))
        self.cv_mini = tk.Canvas(der, width=316, height=130, bg=BG, highlightthickness=0)
        self.cv_mini.pack(padx=12, pady=(2, 6))
        tk.Label(der, text="Notificaciones", bg=PANEL, fg=APAGADO,
                 font=(FUENTE, 9, "bold"), anchor="w").pack(fill="x", padx=12)
        self.log = tk.Text(der, bg=BG, fg=TEXTO, font=(FUENTE, 10), wrap="word", relief="flat",
                           height=10, padx=8, pady=6, state="disabled")
        self.log.pack(fill="both", expand=True, padx=12, pady=(2, 12))
        for etiqueta, color in (("info", TEXTO), ("paso", CIAN), ("ok", VERDE),
                                ("warn", AMBAR), ("mut", ROSA)):
            self.log.tag_configure(etiqueta, foreground=color)
        self.log.tag_configure("exito", foreground=VERDE, font=(FUENTE, 10, "bold"))

        # Lienzo principal
        self.cv = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.cv.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 8))
        self.cv.bind("<Configure>", lambda e: self.redibujar())

    # ------------------------------------------------------------- estado --
    def reiniciar(self):
        self.epoca += 1
        p = self.app.params
        if self.ejemplo:
            self.poblacion = [ags.desde_texto(t) for t in ags.EJEMPLO_POBLACION]
            self.guion = ags.EJEMPLO_GUION
        else:
            self.poblacion = ags.crear_poblacion(p["n_visual"])
            self.guion = None
        self.nombres = list(ags.NOMBRES[:len(self.poblacion)])
        self.gen = 1
        self.fits = None
        self.fase = "poblacion"
        self.pareja = None
        self.siguiente_pob = None
        self.fits_sig = None
        self.hist_mejor, self.hist_prom = [], []
        self.ocupado = False
        self.terminado = False
        self.auto = False
        self.auto_token = 0
        self.toast = None
        self.toast_id = 0
        self.rot = 0.0
        self.spin_ok = [False, False]
        self.spin_actual = 0
        self.etapa = 0
        self.t_anim = 1.0
        self.btn_sig.config(state="normal")
        self.btn_auto.config(text="▶▶  Automático")
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        modo = "ejemplo del anteproyecto" if self.ejemplo else "población al azar"
        self.notificar(f"Generación 1 creada: {len(self.poblacion)} individuos ({modo}).", "paso")
        if self.ejemplo:
            self.notificar("En este ejemplo el 'azar' está fijado para coincidir con el documento.", "info")
        self.explicar()
        self.redibujar()

    def p_cruce(self):
        return self.app.params["p_cruce"]

    def p_mut(self):
        return self.app.params["p_mutacion"]

    # ------------------------------------------------------ notificaciones --
    def notificar(self, texto, tipo="info", toast=False, grande=False):
        simbolo = {"info": "•", "paso": "→", "ok": "✔", "warn": "▲", "mut": "⚡", "exito": "★"}[tipo]
        self.log.config(state="normal")
        self.log.insert("end", f"{simbolo} {texto}\n", tipo)
        self.log.see("end")
        self.log.config(state="disabled")
        if toast:
            color = {"info": CIAN, "paso": CIAN, "ok": VERDE, "warn": AMBAR,
                     "mut": ROSA, "exito": VERDE}[tipo]
            self.toast_id += 1
            self.toast = (f"{simbolo}  {texto}", color, grande)
            actual = self.toast_id
            self.despues(3800 if not grande else 6000, lambda: self.quitar_toast(actual))
            self.redibujar()

    def quitar_toast(self, ident):
        if ident == self.toast_id:
            self.toast = None
            self.redibujar()

    def explicar(self):
        f = self.fase
        self.lbl_fase.config(text=self.TITULOS[f])
        if f == "poblacion":
            t = ("Cada individuo es un horario posible, guardado como un cromosoma de 12 bits: "
                 "4 grupos de 3 bits, uno por materia.\n\nCada grupo se lee en binario: "
                 "110 = 6 horas, 011 = 3 horas.\n\nLas barritas muestran las horas asignadas; "
                 "la marca blanca es lo que la materia necesita.")
        elif f == "evaluacion":
            mejor = max(self.fits)
            i = self.fits.index(mejor)
            e = ags.calcular_error(ags.decodificar(self.poblacion[i]))
            t = ("error = suma de |horas asignadas - horas necesarias|\n"
                 "fitness = 1 / (1 + error)\n\n"
                 f"Ejemplo con el mejor ({self.nombres[i]}): error {e}  →  "
                 f"fitness = 1/(1+{e}) = {mejor:.3f}\n\n"
                 "Error 0 = horario perfecto (fitness 1).")
        elif f == "seleccion":
            t = ("Ruleta: cada individuo ocupa una rebanada proporcional a su fitness "
                 "(fitness ÷ suma de fitness).\n\nSe gira dos veces para elegir a los dos padres. "
                 "Los mejores tienen más probabilidad, pero cualquiera puede salir.")
        elif f == "cruce":
            t = ("Se elige un punto de corte al azar y los padres intercambian las colas de su "
                 "cromosoma.\n\nCada hijo hereda un pedazo de cada padre: los colores muestran "
                 f"de quién viene cada bit.\n\nProbabilidad de cruce: {self.p_cruce()}.")
        elif f == "mutacion":
            t = ("Cada bit puede invertirse (0↔1) con una probabilidad muy baja: "
                 f"{self.p_mut()} por bit.\n\nLa mutación es rara, pero introduce variedad y "
                 "puede crear soluciones que el cruce no encontraría.")
        else:
            t = ("Los hijos forman la nueva generación. Aquí se detalla solo la primera pareja; "
                 "las demás parejas se generan igual (ruleta, cruce y mutación).\n\n"
                 "Los dos primeros (marcados Hijo 1 y Hijo 2) son la pareja que acabas de ver.\n"
                 "La generación anterior se reemplaza completa (AGS sin elitismo).")
        self.lbl_exp.config(text=t)

    # ------------------------------------------------------------- avance --
    def siguiente(self):
        if self.ocupado or self.terminado:
            return
        f = self.fase
        if f == "poblacion":
            self.entrar_evaluacion()
        elif f == "evaluacion":
            self.entrar_seleccion()
        elif f == "seleccion":
            self.entrar_cruce()
        elif f == "cruce":
            self.entrar_mutacion()
        elif f == "mutacion":
            self.entrar_reemplazo()
        else:
            self.pasar_a_siguiente_generacion()

    # --- Evaluación ---------------------------------------------------------
    def entrar_evaluacion(self):
        self.fase = "evaluacion"
        self.fits = ags.evaluar_poblacion(self.poblacion)
        self.hist_mejor.append(max(self.fits))
        self.hist_prom.append(sum(self.fits) / len(self.fits))
        self.explicar()
        self.animar_barras(self.fin_evaluacion)

    def animar_barras(self, al_terminar, cuadros=16):
        self.ocupado = True
        self.t_anim = 0.0

        def cuadro(k):
            self.t_anim = k / cuadros
            self.redibujar()
            if k < cuadros:
                self.despues(30, lambda: cuadro(k + 1))
            else:
                self.ocupado = False
                al_terminar()
        cuadro(1)

    def fin_evaluacion(self):
        mejor = max(self.fits)
        i = self.fits.index(mejor)
        horas = ags.decodificar(self.poblacion[i])
        self.notificar(f"Mejor de la generación {self.gen}: {self.nombres[i]} {horas} "
                       f"→ fitness {mejor:.3f}", "ok")
        peor = min(self.fits)
        j = self.fits.index(peor)
        self.notificar(f"Peor: {self.nombres[j]} → fitness {peor:.3f}", "info")
        if mejor >= 1.0:
            self.horario_perfecto(i)

    def horario_perfecto(self, i):
        self.terminado = True
        self.auto = False
        self.btn_auto.config(text="▶▶  Automático")
        self.btn_sig.config(state="disabled")
        self.notificar(f"Horario perfecto: {self.nombres[i]} cubre todas las horas necesarias "
                       f"(generación {self.gen}).", "exito", toast=True, grande=True)
        self.redibujar()

    # --- Selección (ruleta) -------------------------------------------------
    def entrar_seleccion(self):
        self.fase = "seleccion"
        self.pareja = ags.reproducir_pareja(self.poblacion, self.fits, self.p_cruce(),
                                            self.p_mut(), self.guion)
        self.guion = None                       # el guion solo vale para la primera pareja
        self.spin_ok = [False, False]
        self.spin_actual = 0
        self.rot = 0.0
        self.explicar()
        self.redibujar()
        self.ocupado = True
        self.despues(500, lambda: self.girar(1))

    def girar(self, k):
        d = self.pareja
        giro = d["giro1"] if k == 1 else d["giro2"]
        self.spin_actual = k
        inicio = self.rot
        base = math.floor(inicio / 360) * 360
        final = base + 360 * 3 + ((-giro * 360) % 360)
        cuadros = 30

        def cuadro(n):
            t = n / cuadros
            self.rot = inicio + (final - inicio) * (1 - (1 - t) ** 3)
            self.redibujar()
            if n < cuadros:
                self.despues(40, lambda: cuadro(n + 1))
            else:
                self.fin_giro(k)
        cuadro(1)

    def fin_giro(self, k):
        d = self.pareja
        self.spin_ok[k - 1] = True
        self.spin_actual = 0
        indice = d["i1"] if k == 1 else d["i2"]
        giro = d["giro1"] if k == 1 else d["giro2"]
        self.notificar(f"Giro {k}: salió {giro:.3f} → gana {self.nombres[indice]} (Padre {k})", "ok")
        self.redibujar()
        if k == 1:
            self.despues(600, lambda: self.girar(2))
        else:
            if d["i1"] == d["i2"]:
                self.notificar(f"{self.nombres[d['i1']]} fue elegido como ambos padres. "
                               "La ruleta lo permite: es azar con ventaja para los mejores.",
                               "warn", toast=True)
            self.ocupado = False

    # --- Cruce --------------------------------------------------------------
    def entrar_cruce(self):
        self.fase = "cruce"
        self.etapa = 0
        self.ocupado = True
        self.explicar()
        self.redibujar()
        self.despues(800, self.cruce_etapa1)

    def cruce_etapa1(self):
        d = self.pareja
        self.etapa = 1
        if d["punto"] is None:
            self.notificar(f"No hubo cruce (probabilidad {self.p_cruce()}): los hijos son "
                           "copias de los padres.", "warn", toast=True)
        else:
            self.notificar(f"Punto de corte: después del bit {d['punto']}.", "paso", toast=True)
        self.redibujar()
        self.despues(1000, self.cruce_etapa2)

    def cruce_etapa2(self):
        d = self.pareja
        self.etapa = 2
        f1 = ags.calcular_fitness(d["cruzado1"])
        f2 = ags.calcular_fitness(d["cruzado2"])
        self.notificar(f"Hijo 1: {ags.decodificar(d['cruzado1'])} → fitness {f1:.3f}", "info")
        self.notificar(f"Hijo 2: {ags.decodificar(d['cruzado2'])} → fitness {f2:.3f}", "info")
        self.ocupado = False
        self.redibujar()

    # --- Mutación -----------------------------------------------------------
    def entrar_mutacion(self):
        self.fase = "mutacion"
        self.etapa = 0
        self.ocupado = True
        self.explicar()
        self.redibujar()
        self.despues(1000, self.mutacion_etapa1)

    def mutacion_etapa1(self):
        d = self.pareja
        self.etapa = 1
        hubo = bool(d["mut1"] or d["mut2"])
        if not hubo:
            self.notificar(f"Sin mutaciones en esta pareja: ninguno de los 24 bits cayó "
                           f"dentro de la probabilidad {self.p_mut()}.", "info", toast=True)
            self.ocupado = False
            self.redibujar()
            return
        for k, (antes, despues, pos) in enumerate(
                [(d["cruzado1"], d["hijo1"], d["mut1"]), (d["cruzado2"], d["hijo2"], d["mut2"])], 1):
            for i in pos:
                materia = ags.MATERIAS[i // ags.BITS_POR_MATERIA]
                ha = ags.decodificar(antes)[i // ags.BITS_POR_MATERIA]
                hd = ags.decodificar(despues)[i // ags.BITS_POR_MATERIA]
                self.notificar(f"Mutación: Hijo {k}, bit {i + 1}: {antes[i]} → {despues[i]} "
                               f"({materia}: {ha} h → {hd} h)", "mut", toast=True, grande=True)
        for k, (a, b) in enumerate([(d["cruzado1"], d["hijo1"]), (d["cruzado2"], d["hijo2"])], 1):
            if a != b:
                fa, fb = ags.calcular_fitness(a), ags.calcular_fitness(b)
                if fb > fa:
                    self.notificar(f"La mutación mejoró al Hijo {k}: {fa:.3f} → {fb:.3f}", "ok")
                elif fb < fa:
                    self.notificar(f"La mutación empeoró al Hijo {k}: {fa:.3f} → {fb:.3f}", "warn")
        self.ocupado = False
        self.redibujar()

    # --- Reemplazo ----------------------------------------------------------
    def entrar_reemplazo(self):
        self.fase = "reemplazo"
        self.siguiente_pob = ags.siguiente_generacion(self.poblacion, self.fits, self.p_cruce(),
                                                      self.p_mut(), self.pareja)
        self.fits_sig = ags.evaluar_poblacion(self.siguiente_pob)
        self.explicar()
        self.animar_barras(self.fin_reemplazo)

    def fin_reemplazo(self):
        antes, ahora = max(self.fits), max(self.fits_sig)
        resto = len(self.poblacion) // 2 - 1
        if resto == 1:
            self.notificar("Se generó la otra pareja con el mismo proceso.", "info")
        elif resto > 1:
            self.notificar(f"Se generaron las otras {resto} parejas con el mismo proceso.", "info")
        if ahora > antes:
            self.notificar(f"El mejor fitness subió: {antes:.3f} → {ahora:.3f}", "ok", toast=True)
        elif ahora < antes:
            self.notificar(f"El mejor fitness bajó: {antes:.3f} → {ahora:.3f}. Pasa en el AGS "
                           "simple: la generación se reemplaza completa.", "warn", toast=True)
        else:
            self.notificar(f"El mejor fitness se mantiene en {ahora:.3f}.", "info", toast=True)

    def pasar_a_siguiente_generacion(self):
        self.poblacion = self.siguiente_pob
        self.siguiente_pob = None
        self.gen += 1
        self.pareja = None
        self.notificar(f"— Generación {self.gen} —", "paso")
        self.entrar_evaluacion()

    # --- Modo automático de esta pantalla ----------------------------------
    def alternar_auto(self):
        if self.terminado:
            return
        self.auto = not self.auto
        self.btn_auto.config(text="⏸  Pausar" if self.auto else "▶▶  Automático")
        if self.auto:
            self.auto_token += 1
            self.auto_tick(self.auto_token)

    def auto_tick(self, token):
        if not self.auto or token != self.auto_token or self.terminado:
            return
        if not self.ocupado:
            self.siguiente()
        pausa = [2600, 1700, 1100, 650, 300][int(self.vel.get()) - 1]
        self.despues(pausa, lambda: self.auto_tick(token))

    # ----------------------------------------------------------- dibujo ---
    def redibujar(self):
        cv = self.cv
        cv.delete("all")
        W = max(cv.winfo_width(), 900)
        H = max(cv.winfo_height(), 560)
        f = self.fase
        sub = {"poblacion": "Horarios candidatos (cromosomas de 12 bits)",
               "evaluacion": "¿Qué tan bueno es cada horario?",
               "seleccion": "La ruleta elige a los padres",
               "cruce": "Los padres combinan sus cromosomas",
               "mutacion": "Pequeños cambios al azar",
               "reemplazo": "Nace la siguiente generación"}[f]
        titulo = f"Generación {self.gen + (1 if f == 'reemplazo' else 0)}  ·  {self.ETIQUETAS[f]}"
        cv.create_text(14, 12, text=titulo, anchor="nw", fill=TEXTO, font=(FUENTE, 18, "bold"))
        cv.create_text(14, 42, text=sub, anchor="nw", fill=APAGADO, font=(FUENTE, 10))

        if f == "poblacion":
            self.dibujar_tabla(W, H, self.poblacion, None)
        elif f == "evaluacion":
            self.dibujar_tabla(W, H, self.poblacion, self.fits, self.t_anim)
        elif f == "seleccion":
            self.dibujar_ruleta(W, H)
        elif f == "cruce":
            self.dibujar_cruce(W, H)
        elif f == "mutacion":
            self.dibujar_mutacion(W, H)
        else:
            marcas = {0: (COLOR_PADRE1, "← Hijo 1"),
                      1: (COLOR_PADRE2, "← Hijo 2")}
            self.dibujar_tabla(W, H, self.siguiente_pob, self.fits_sig, self.t_anim, marcas)

        if self.terminado:
            cv.create_text(W - 24, 30, text="Horario perfecto", anchor="e", fill=VERDE,
                           font=(FUENTE, 26, "bold"))
        self.dibujar_toast(W, H)
        self.actualizar_paneles()

    def dibujar_toast(self, W, H):
        if not self.toast:
            return
        texto, color, grande = self.toast
        alto = 62 if grande else 44
        ancho = min(W - 40, max(420, int(len(texto) * (11 if grande else 8.5)) + 50))
        x1, x2 = (W - ancho) / 2, (W + ancho) / 2
        y2 = H - 14
        y1 = y2 - alto
        borde = color
        rect_red(self.cv, x1, y1, x2, y2, 14, fill=mezclar(color, BG, 0.82), outline=borde,
                 width=3 if grande else 2)
        self.cv.create_text(W / 2, (y1 + y2) / 2, text=texto, fill=TEXTO, width=ancho - 30,
                            justify="center", font=(FUENTE, 13 if grande else 11, "bold"))

    # --- Tabla de individuos ------------------------------------------------
    def dibujar_tabla(self, W, H, pob, fits, t=1.0, marcas=None):
        cv = self.cv
        x0 = 14
        y0 = 74
        n = len(pob)
        alto_fila = max(30, min(56, (H - y0 - 40 - 84) // n))
        # Encabezados
        for g in range(len(ags.MATERIAS)):
            gx = x_bit(x0 + 52, g * ags.BITS_POR_MATERIA)
            cv.create_text(gx + (3 * PASO_BIT - 2) / 2, y0 + 6, text=ags.ABREVIATURAS[g],
                           fill=COLOR_MATERIA[g], font=(FUENTE, 9, "bold"))
            hx = x0 + 340 + g * 64
            cv.create_text(hx + 19, y0 + 6, text=f"{ags.ABREVIATURAS[g]} ({ags.HORAS_NECESARIAS[g]})",
                           fill=COLOR_MATERIA[g], font=(FUENTE, 9, "bold"))
        cv.create_text(x0 + 52 + ANCHO_BITS / 2, y0 + 22, text="cromosoma (3 bits por materia)",
                       fill=APAGADO, font=(FUENTE, 8))
        cv.create_text(x0 + 340 + 128, y0 + 22, text="horas asignadas (marca = necesaria)",
                       fill=APAGADO, font=(FUENTE, 8))
        cv.create_text(x0 + 622, y0 + 10, text="Error", fill=APAGADO, font=(FUENTE, 9, "bold"))
        cv.create_text(x0 + 700, y0 + 10, text="Fitness", fill=APAGADO, font=(FUENTE, 9, "bold"))

        mejor = max(fits) if fits else None
        for i, c in enumerate(pob):
            y = y0 + 34 + i * alto_fila
            h = alto_fila - 6
            marca = marcas.get(i) if marcas else None
            rect_red(cv, x0, y, x0 + ANCHO_TABLA, y + h, 8, fill=PANEL if i % 2 == 0 else PANEL2,
                     outline=marca[0] if marca else LINEA, width=3 if marca else 1)
            # nombre
            es_mejor = fits is not None and t >= 1 and fits[i] == mejor
            cv.create_oval(x0 + 8, y + h / 2 - 15, x0 + 38, y + h / 2 + 15,
                           fill=AMBAR if es_mejor else mezclar(CIAN, BG, 0.55), outline="")
            cv.create_text(x0 + 23, y + h / 2, text=ags.NOMBRES[i], fill=BG if es_mejor else TEXTO,
                           font=(FUENTE, 13, "bold"))
            if es_mejor:
                cv.create_text(x0 + 46, y + h / 2 - 12, text="★", fill=AMBAR, font=(FUENTE, 11, "bold"))
            # cromosoma y horas
            dibujar_bits(cv, x0 + 52, y + (h - CELDA) / 2, c)
            horas = ags.decodificar(c)
            dibujar_horas(cv, x0 + 340, y + h / 2 - 5, horas)
            # error y fitness
            if fits is None:
                cv.create_text(x0 + 622, y + h / 2, text="—", fill=APAGADO, font=(FUENTE, 13))
                cv.create_text(x0 + 740, y + h / 2, text="—", fill=APAGADO, font=(FUENTE, 13))
            else:
                err = ags.calcular_error(horas)
                f = fits[i]
                cv.create_text(x0 + 622, y + h / 2, text=str(err), fill=color_diferencia(0 if err == 0 else (1 if err <= 2 else 3)),
                               font=(FUENTE, 14, "bold"))
                cv.create_rectangle(x0 + 662, y + h / 2 - 6, x0 + 762, y + h / 2 + 6, fill=BG, outline="")
                if f * t > 0.001:
                    cv.create_rectangle(x0 + 662, y + h / 2 - 6, x0 + 662 + 100 * f * t, y + h / 2 + 6,
                                        fill=color_fitness(f), outline="")
                cv.create_text(x0 + 768, y + h / 2, text=f"{f * t:.3f}", anchor="w", fill=TEXTO,
                               font=(MONO, 10, "bold"))
            if marca:
                cv.create_text(x0 + ANCHO_TABLA + 12, y + h / 2, text=marca[1], anchor="w",
                               fill=marca[0], font=(FUENTE, 8, "bold"), width=86)

    # --- Ruleta -------------------------------------------------------------
    def dibujar_ruleta(self, W, H):
        cv = self.cv
        d = self.pareja
        n = len(self.poblacion)
        probs = ags.calcular_probabilidades(self.fits)
        r = min(200, (H - 210) / 2)
        cx = 30 + r + 10
        cy = 110 + r + 14
        cum = 0.0
        for i, p in enumerate(probs):
            ini = 90 - self.rot - cum * 360
            cv.create_arc(cx - r, cy - r, cx + r, cy + r, start=ini, extent=-p * 360,
                          fill=COLORES_RULETA[i % len(COLORES_RULETA)], outline=BG, width=2,
                          style="pieslice")
            if p * 360 > 15:
                mid = math.radians(ini - p * 180)
                cv.create_text(cx + 0.72 * r * math.cos(mid), cy - 0.72 * r * math.sin(mid),
                               text=ags.NOMBRES[i], fill=BG, font=(FUENTE, 14, "bold"))
            cum += p
        # rebanadas ganadoras resaltadas
        for k, (ok, indice, color) in enumerate([(self.spin_ok[0], d["i1"], COLOR_PADRE1),
                                                 (self.spin_ok[1], d["i2"], COLOR_PADRE2)]):
            if ok:
                ini = 90 - self.rot - sum(probs[:indice]) * 360
                cv.create_arc(cx - r - 4 + 2 * k, cy - r - 4 + 2 * k, cx + r + 4 - 2 * k, cy + r + 4 - 2 * k,
                              start=ini, extent=-probs[indice] * 360, fill="", outline=color,
                              width=5, style="pieslice")
        cv.create_oval(cx - 30, cy - 30, cx + 30, cy + 30, fill=BG, outline=CIAN, width=3)
        cv.create_text(cx, cy, text="AGS", fill=CIAN, font=(FUENTE, 12, "bold"))
        cv.create_polygon([cx - 16, cy - r - 24, cx + 16, cy - r - 24, cx, cy - r + 8],
                          fill=ROJO, outline=TEXTO, width=2)
        # giros
        yg = cy + r + 20
        for k, (giro, indice, color) in enumerate([(d["giro1"], d["i1"], COLOR_PADRE1),
                                                   (d["giro2"], d["i2"], COLOR_PADRE2)], 1):
            if self.spin_ok[k - 1]:
                txt = f"Giro {k}: {giro:.3f}  →  gana {self.nombres[indice]}  (Padre {k})"
                col = color
            elif self.spin_actual == k:
                txt = f"Giro {k}: girando..."
                col = TEXTO
            else:
                txt = f"Giro {k}: esperando..."
                col = APAGADO
            cv.create_text(cx, yg + (k - 1) * 24, text=txt, fill=col, font=(FUENTE, 12, "bold"))
        # tabla de probabilidades
        tx = cx + r + 50
        alto = max(24, min(34, (H - 190) // n))
        cv.create_text(tx, 92, text="Ind.", anchor="w", fill=APAGADO, font=(FUENTE, 9, "bold"))
        cv.create_text(tx + 52, 92, text="Fitness", anchor="w", fill=APAGADO, font=(FUENTE, 9, "bold"))
        cv.create_text(tx + 122, 92, text="Probab.", anchor="w", fill=APAGADO, font=(FUENTE, 9, "bold"))
        cv.create_text(tx + 200, 92, text="Rango", anchor="w", fill=APAGADO, font=(FUENTE, 9, "bold"))
        acumulado = 0.0
        for i, p in enumerate(probs):
            y = 108 + i * alto
            elegido = None
            if self.spin_ok[0] and i == d["i1"]:
                elegido = (COLOR_PADRE1, "← Padre 1")
            if self.spin_ok[1] and i == d["i2"]:
                elegido = (COLOR_PADRE2, "← Padre 2") if elegido is None else (COLOR_PADRE2, "← P1 y P2")
            rect_red(cv, tx - 8, y, tx + 372, y + alto - 4, 6, fill=PANEL if i % 2 == 0 else PANEL2,
                     outline=elegido[0] if elegido else LINEA, width=3 if elegido else 1)
            cv.create_oval(tx - 2, y + 4, tx + 14, y + alto - 8,
                           fill=COLORES_RULETA[i % len(COLORES_RULETA)], outline="")
            cv.create_text(tx + 24, y + (alto - 4) / 2, text=ags.NOMBRES[i], anchor="w", fill=TEXTO,
                           font=(FUENTE, 11, "bold"))
            cv.create_text(tx + 52, y + (alto - 4) / 2, text=f"{self.fits[i]:.3f}", anchor="w", fill=TEXTO,
                           font=(MONO, 10))
            cv.create_text(tx + 122, y + (alto - 4) / 2, text=f"{p * 100:.1f} %", anchor="w", fill=TEXTO,
                           font=(MONO, 10, "bold"))
            cv.create_text(tx + 200, y + (alto - 4) / 2, text=f"{acumulado:.3f}–{acumulado + p:.3f}",
                           anchor="w", fill=APAGADO, font=(MONO, 9))
            if elegido:
                cv.create_text(tx + 296, y + (alto - 4) / 2, text=elegido[1], anchor="w", fill=elegido[0],
                               font=(FUENTE, 9, "bold"))
            acumulado += p
        cv.create_text(tx, 108 + n * alto + 14, anchor="nw", fill=APAGADO, font=(FUENTE, 9),
                       text="Probabilidad = fitness / suma de fitness.\n"
                            "Gana la rebanada donde cae el número del giro (entre 0 y 1).",
                       width=440)

    # --- Cruce --------------------------------------------------------------
    def colores_hijos(self, d):
        """Color de cada bit de los hijos según el padre del que lo heredó."""
        punto = d["punto"]
        if punto is None:
            c1 = [COLOR_PADRE1] * ags.LONGITUD
            c2 = [COLOR_PADRE2] * ags.LONGITUD
        else:
            c1 = [COLOR_PADRE1 if i < punto else COLOR_PADRE2 for i in range(ags.LONGITUD)]
            c2 = [COLOR_PADRE2 if i < punto else COLOR_PADRE1 for i in range(ags.LONGITUD)]
        return c1, c2

    def fila_cromosoma(self, x, y, etiqueta, bits, colores, color_etiqueta, resaltar=(), oculto=False):
        cv = self.cv
        cv.create_text(x - 14, y + CELDA / 2, text=etiqueta, anchor="e", fill=color_etiqueta,
                       font=(FUENTE, 12, "bold"))
        dibujar_bits(cv, x, y, bits, colores=colores, resaltar=resaltar, oculto=oculto)
        if not oculto:
            horas = ags.decodificar(bits)
            f = ags.calcular_fitness(bits)
            cv.create_text(x + ANCHO_BITS + 16, y + CELDA / 2, anchor="w", fill=TEXTO,
                           text=f"{horas}  fitness {f:.3f}", font=(MONO, 10, "bold"))

    def dibujar_cruce(self, W, H):
        cv = self.cv
        d = self.pareja
        xb = 250
        yp1, yp2, yh1, yh2 = 130, 188, 336, 394
        n1, n2 = self.nombres[d["i1"]], self.nombres[d["i2"]]
        cv.create_text(xb - 14, 96, text="PADRES", anchor="e", fill=APAGADO, font=(FUENTE, 10, "bold"))
        cv.create_text(xb - 14, 300, text="HIJOS", anchor="e", fill=APAGADO, font=(FUENTE, 10, "bold"))
        self.fila_cromosoma(xb, yp1, f"Padre 1 · {n1}", d["padre1"], [COLOR_PADRE1] * ags.LONGITUD, COLOR_PADRE1)
        self.fila_cromosoma(xb, yp2, f"Padre 2 · {n2}", d["padre2"], [COLOR_PADRE2] * ags.LONGITUD, COLOR_PADRE2)
        c1, c2 = self.colores_hijos(d)
        if self.etapa >= 1:
            if d["punto"] is None:
                cv.create_text(xb + ANCHO_BITS / 2, 246, text="SIN CRUCE", fill=AMBAR, font=(FUENTE, 18, "bold"))
                cv.create_text(xb + ANCHO_BITS / 2, 272, text=f"(la probabilidad de cruce es {self.p_cruce()})",
                               fill=AMBAR, font=(FUENTE, 10))
            else:
                xc = x_corte(xb, d["punto"])
                cv.create_line(xc, 112, xc, 424, fill=ROJO, width=3, dash=(7, 4))
                cv.create_text(xc, 100, text="✂", fill=ROJO, font=(FUENTE, 16, "bold"))
                cv.create_text(xc, 438, text=f"corte tras el bit {d['punto']}", fill=ROJO,
                               font=(FUENTE, 10, "bold"))
        if self.etapa >= 2:
            self.fila_cromosoma(xb, yh1, "Hijo 1", d["cruzado1"], c1, TEXTO)
            self.fila_cromosoma(xb, yh2, "Hijo 2", d["cruzado2"], c2, TEXTO)
            f1 = ags.calcular_fitness(d["cruzado1"])
            f2 = ags.calcular_fitness(d["cruzado2"])
            fp = max(ags.calcular_fitness(d["padre1"]), ags.calcular_fitness(d["padre2"]))
            mejor = max(f1, f2)
            if d["punto"] is None:
                msg, col = "Los hijos son copias exactas de los padres", APAGADO
            elif mejor > fp:
                msg, col = f"Un hijo superó a sus padres ({fp:.3f} → {mejor:.3f})", VERDE
            elif mejor < fp:
                msg, col = f"Los hijos quedaron por debajo del mejor padre ({fp:.3f})", AMBAR
            else:
                msg, col = "Los hijos igualan al mejor padre", TEXTO
            cv.create_text(xb + ANCHO_BITS / 2, 478, text=msg, fill=col, font=(FUENTE, 12, "bold"))
        else:
            self.fila_cromosoma(xb, yh1, "Hijo 1", d["cruzado1"], c1, APAGADO, oculto=True)
            self.fila_cromosoma(xb, yh2, "Hijo 2", d["cruzado2"], c2, APAGADO, oculto=True)
        # leyenda
        ly = H - 96
        cv.create_rectangle(xb, ly, xb + 14, ly + 14, fill=COLOR_PADRE1, outline="")
        cv.create_text(xb + 22, ly + 7, text="bit heredado del Padre 1", anchor="w", fill=TEXTO, font=(FUENTE, 10))
        cv.create_rectangle(xb + 220, ly, xb + 234, ly + 14, fill=COLOR_PADRE2, outline="")
        cv.create_text(xb + 242, ly + 7, text="bit heredado del Padre 2", anchor="w", fill=TEXTO, font=(FUENTE, 10))

    # --- Mutación -----------------------------------------------------------
    def dibujar_mutacion(self, W, H):
        cv = self.cv
        d = self.pareja
        xb = 250
        c1, c2 = self.colores_hijos(d)
        bloques = [(1, 130, d["cruzado1"], d["hijo1"], d["mut1"], c1),
                   (2, 330, d["cruzado2"], d["hijo2"], d["mut2"], c2)]
        for k, y, antes, despues, pos, colores in bloques:
            cv.create_text(xb - 14, y - 22, text=f"HIJO {k}", anchor="e", fill=APAGADO, font=(FUENTE, 10, "bold"))
            self.fila_cromosoma(xb, y, "antes", antes, colores, APAGADO)
            cv.create_text(xb + ANCHO_BITS / 2, y + 44, text="▼", fill=APAGADO, font=(FUENTE, 12))
            if self.etapa == 0:
                self.fila_cromosoma(xb, y + 68, "después", despues, colores, APAGADO, oculto=True)
                continue
            col_flip = [colores[i] for i in range(ags.LONGITUD)]
            self.fila_cromosoma(xb, y + 68, "después", despues, col_flip, TEXTO, resaltar=set(pos))
            if pos:
                fa, fb = ags.calcular_fitness(antes), ags.calcular_fitness(despues)
                flecha = "▲" if fb > fa else ("▼" if fb < fa else "=")
                col = VERDE if fb > fa else (AMBAR if fb < fa else TEXTO)
                for j, i in enumerate(pos):
                    xm = x_bit(xb, i) + CELDA / 2
                    cv.create_text(xm, y + 68 + CELDA + 14, text="▲", fill=ROSA, font=(FUENTE, 13, "bold"))
                cv.create_text(xb, y + 68 + CELDA + 36, anchor="w", fill=col, font=(FUENTE, 11, "bold"),
                               text=f"mutación en bit(s) {', '.join(str(i + 1) for i in pos)}   "
                                    f"fitness {fa:.3f} → {fb:.3f} {flecha}")
            else:
                cv.create_text(xb, y + 68 + CELDA + 22, anchor="w", fill=APAGADO, font=(FUENTE, 10),
                               text="sin cambios")
        if self.etapa >= 1 and not (d["mut1"] or d["mut2"]):
            cv.create_text(xb + ANCHO_BITS / 2, 270, text="Ninguna mutación esta vez", fill=AMBAR,
                           font=(FUENTE, 16, "bold"))

    # --- Paneles laterales --------------------------------------------------
    def actualizar_paneles(self):
        # indicador de etapas
        cv = self.cv_pasos
        cv.delete("all")
        W = max(cv.winfo_width(), 900)
        n = len(self.FASES)
        ancho = (W - 28) / n
        actual = self.FASES.index(self.fase)
        for i, f in enumerate(self.FASES):
            x1 = 14 + i * ancho
            x2 = x1 + ancho - 8
            if i == actual:
                fondo, fg, borde = CIAN, BG, CIAN
            elif i < actual or self.terminado:
                fondo, fg, borde = mezclar(VERDE, BG, 0.75), TEXTO, mezclar(VERDE, BG, 0.4)
            else:
                fondo, fg, borde = PANEL, APAGADO, LINEA
            rect_red(cv, x1, 10, x2, 52, 12, fill=fondo, outline=borde, width=2)
            cv.create_text((x1 + x2) / 2, 31, text=self.TITULOS[f], fill=fg, font=(FUENTE, 11, "bold"))
        # información inferior
        mejor = f"{max(self.fits):.3f}" if self.fits else "—"
        self.lbl_info.config(text=f"Generación {self.gen}   ·   Individuos {len(self.poblacion)}   ·   "
                                  f"Mejor fitness {mejor}")
        # mini gráfica
        mc = self.cv_mini
        mc.delete("all")
        w, h = 316, 130
        x1, y1, x2, y2 = 30, 10, w - 10, h - 22
        for v in (0, 0.5, 1.0):
            y = y2 - (y2 - y1) * v
            mc.create_line(x1, y, x2, y, fill=LINEA)
            mc.create_text(x1 - 4, y, text=f"{v:g}", anchor="e", fill=APAGADO, font=(FUENTE, 8))
        n_pts = len(self.hist_mejor)
        if n_pts:
            xs = [x1 + (x2 - x1) * (k / max(n_pts - 1, 1)) if n_pts > 1 else (x1 + x2) / 2 for k in range(n_pts)]
            for serie, color in ((self.hist_prom, AMBAR), (self.hist_mejor, CIAN)):
                pts = []
                for xk, v in zip(xs, serie):
                    pts += [xk, y2 - (y2 - y1) * v]
                if n_pts > 1:
                    mc.create_line(pts, fill=color, width=2)
                mc.create_oval(pts[-2] - 3, pts[-1] - 3, pts[-2] + 3, pts[-1] + 3, fill=color, outline="")
        mc.create_text(x1, h - 8, text="generaciones →", anchor="w", fill=APAGADO, font=(FUENTE, 8))
        mc.create_text(x2, h - 8, text="mejor", anchor="e", fill=CIAN, font=(FUENTE, 8, "bold"))
        mc.create_text(x2 - 36, h - 8, text="promedio", anchor="e", fill=AMBAR, font=(FUENTE, 8, "bold"))

    def destroy(self):
        self.app.unbind("<Right>")
        self.app.unbind("<Return>")
        self.app.unbind("<Escape>")
        super().destroy()


# ===========================================================================
# PANTALLA 4: EJECUCIÓN AUTOMÁTICA CON GRÁFICA
# ===========================================================================
class PantallaAuto(PantallaBase):
    def __init__(self, app):
        super().__init__(app)
        barra = tk.Frame(self, bg=PANEL, height=64)
        barra.pack(side="bottom", fill="x")
        boton(barra, "☰  Menú", self.app.mostrar_menu, color=PANEL2, fg=TEXTO).pack(side="left", padx=(14, 6), pady=10)
        self.btn_inicio = boton(barra, "▶  Iniciar", self.alternar, color=VERDE, tam=12)
        self.btn_inicio.pack(side="left", padx=6, pady=10)
        boton(barra, "⟲  Reiniciar", self.reiniciar, color=PANEL2, fg=TEXTO).pack(side="left", padx=6, pady=10)
        tk.Label(barra, text="Velocidad", bg=PANEL, fg=APAGADO, font=(FUENTE, 10)).pack(side="left", padx=(16, 2))
        self.vel = tk.Scale(barra, from_=1, to=5, orient="horizontal", showvalue=False, length=110,
                            bg=PANEL, troughcolor=BG, highlightthickness=0, activebackground=CIAN)
        self.vel.set(3)
        self.vel.pack(side="left")
        self.lbl_info = tk.Label(barra, text="", bg=PANEL, fg=TEXTO, font=(FUENTE, 11, "bold"))
        self.lbl_info.pack(side="right", padx=16)
        self.cv = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.cv.pack(side="top", fill="both", expand=True, padx=8, pady=8)
        self.cv.bind("<Configure>", lambda e: self.redibujar())
        self.app.bind("<Escape>", lambda e: self.app.mostrar_menu())
        self.reiniciar()

    def reiniciar(self):
        self.epoca += 1
        p = self.app.params
        self.poblacion = ags.crear_poblacion(p["n_auto"])
        self.gen = 0
        self.hist_mejor, self.hist_prom = [], []
        self.mejor = None
        self.mejor_fitness = 0.0
        self.gen_mejor = 0
        self.corriendo = False
        self.token = 0
        self.terminado = False
        self.mensaje = None
        self.btn_inicio.config(text="▶  Iniciar")
        self.redibujar()

    def alternar(self):
        if self.terminado:
            self.reiniciar()
        self.corriendo = not self.corriendo
        self.btn_inicio.config(text="⏸  Pausar" if self.corriendo else "▶  Continuar")
        self.token += 1
        if self.corriendo:
            self.tick(self.token)

    def tick(self, token):
        if not self.corriendo or token != self.token:
            return
        p = self.app.params
        fits = ags.evaluar_poblacion(self.poblacion)
        self.gen += 1
        mejor = max(fits)
        self.hist_mejor.append(mejor)
        self.hist_prom.append(sum(fits) / len(fits))
        if mejor > self.mejor_fitness:
            self.mejor_fitness = mejor
            self.mejor = self.poblacion[fits.index(mejor)][:]
            self.gen_mejor = self.gen
        if self.mejor_fitness >= 1.0:
            self.terminar(f"Horario perfecto en la generación {self.gen}!", VERDE, True)
        elif self.gen >= p["generaciones"]:
            self.terminar(f"Se llegó al máximo de {p['generaciones']} generaciones. "
                          f"Mejor fitness: {self.mejor_fitness:.3f}", AMBAR, False)
        else:
            self.poblacion = ags.siguiente_generacion(self.poblacion, fits, p["p_cruce"], p["p_mutacion"])
            self.redibujar()
            pausa = [500, 250, 110, 40, 8][int(self.vel.get()) - 1]
            self.despues(pausa, lambda: self.tick(token))

    def terminar(self, texto, color, celebrar):
        self.corriendo = False
        self.terminado = True
        self.mensaje = (texto, color)
        self.btn_inicio.config(text="▶  Nueva ejecución")
        self.redibujar()

    def redibujar(self):
        cv = self.cv
        cv.delete("all")
        W = max(cv.winfo_width(), 900)
        H = max(cv.winfo_height(), 520)
        p = self.app.params
        cv.create_text(14, 10, text="Ejecución automática", anchor="nw", fill=TEXTO, font=(FUENTE, 18, "bold"))
        cv.create_text(14, 40, anchor="nw", fill=APAGADO, font=(FUENTE, 10),
                       text=f"Población {p['n_auto']}  ·  cruce {p['p_cruce']}  ·  mutación {p['p_mutacion']}  ·  "
                            f"máximo {p['generaciones']} generaciones")
        # ---- gráfica ----
        gx1, gy1, gx2, gy2 = 70, 90, W - 420, H - 60
        rect_red(cv, gx1 - 50, gy1 - 30, gx2 + 20, gy2 + 46, 12, fill=PANEL, outline=LINEA, width=1)
        cv.create_text((gx1 + gx2) / 2, gy1 - 14, text="Evolución del fitness", fill=TEXTO, font=(FUENTE, 12, "bold"))
        for v in (0, 0.25, 0.5, 0.75, 1.0):
            y = gy2 - (gy2 - gy1) * v
            cv.create_line(gx1, y, gx2, y, fill=LINEA)
            cv.create_text(gx1 - 8, y, text=f"{v:.2f}", anchor="e", fill=APAGADO, font=(FUENTE, 9))
        cv.create_line(gx1, gy2 - (gy2 - gy1), gx2, gy2 - (gy2 - gy1), fill=VERDE, width=2, dash=(3, 4))
        n = len(self.hist_mejor)
        xmax = max(10, n)
        paso = 5 if xmax <= 50 else (10 if xmax <= 100 else 50)
        for g in range(0, xmax + 1, paso):
            x = gx1 + (gx2 - gx1) * g / xmax
            cv.create_text(x, gy2 + 12, text=str(g), fill=APAGADO, font=(FUENTE, 9))
        cv.create_text((gx1 + gx2) / 2, gy2 + 32, text="generación", fill=APAGADO, font=(FUENTE, 10))
        if n:
            for serie, color, dash in ((self.hist_prom, AMBAR, (5, 3)), (self.hist_mejor, CIAN, None)):
                pts = []
                for k, v in enumerate(serie, 1):
                    pts += [gx1 + (gx2 - gx1) * k / xmax, gy2 - (gy2 - gy1) * v]
                if n > 1:
                    if dash:
                        cv.create_line(pts, fill=color, width=2, dash=dash)
                    else:
                        cv.create_line(pts, fill=color, width=4)
                cv.create_oval(pts[-2] - 5, pts[-1] - 5, pts[-2] + 5, pts[-1] + 5, fill=color, outline=BG)
        # leyenda
        cv.create_line(gx1 + 10, gy2 - 16, gx1 + 40, gy2 - 16, fill=CIAN, width=4)
        cv.create_text(gx1 + 46, gy2 - 16, text="mejor del momento", anchor="w", fill=TEXTO, font=(FUENTE, 9))
        cv.create_line(gx1 + 190, gy2 - 16, gx1 + 220, gy2 - 16, fill=AMBAR, width=2, dash=(5, 3))
        cv.create_text(gx1 + 226, gy2 - 16, text="promedio", anchor="w", fill=TEXTO, font=(FUENTE, 9))
        # ---- panel del mejor horario ----
        px = W - 390
        rect_red(cv, px, 60, W - 14, H - 14, 12, fill=PANEL, outline=LINEA, width=1)
        cv.create_text(px + 18, 78, text="Mejor horario encontrado", anchor="nw", fill=CIAN, font=(FUENTE, 14, "bold"))
        if self.mejor is None:
            cv.create_text(px + 190, 200, text="Pulsa  ▶ Iniciar", fill=APAGADO, font=(FUENTE, 14))
        else:
            horas = ags.decodificar(self.mejor)
            for k, materia in enumerate(ags.MATERIAS):
                y = 130 + k * 56
                necesita = ags.HORAS_NECESARIAS[k]
                col = color_diferencia(abs(horas[k] - necesita))
                cv.create_text(px + 18, y, text=materia, anchor="w", fill=COLOR_MATERIA[k], font=(FUENTE, 11, "bold"))
                cv.create_rectangle(px + 18, y + 14, px + 258, y + 30, fill=PANEL2, outline="")
                if horas[k] > 0:
                    cv.create_rectangle(px + 18, y + 14, px + 18 + 240 * horas[k] / ags.HORAS_MAXIMAS, y + 30,
                                        fill=col, outline="")
                xm = px + 18 + 240 * necesita / ags.HORAS_MAXIMAS
                cv.create_line(xm, y + 10, xm, y + 34, fill=TEXTO, width=2)
                cv.create_text(px + 270, y + 22, text=f"{horas[k]} h", anchor="w", fill=col, font=(FUENTE, 13, "bold"))
                cv.create_text(px + 330, y + 22, text=f"(pide {necesita})", anchor="w", fill=APAGADO, font=(FUENTE, 9))
            dibujar_bits(cv, px + 18, 362, self.mejor)
            err = ags.calcular_error(horas)
            cv.create_text(px + 18, 408, text=f"Error {err}   ·   Fitness {self.mejor_fitness:.3f}", anchor="w",
                           fill=TEXTO, font=(FUENTE, 13, "bold"))
            cv.create_text(px + 18, 436, text=f"Apareció en la generación {self.gen_mejor}", anchor="w",
                           fill=APAGADO, font=(FUENTE, 10))
        if self.mensaje:
            texto, color = self.mensaje
            rect_red(cv, px + 14, H - 118, W - 28, H - 30, 14,
                     fill=mezclar(color, BG, 0.8), outline=color, width=3)
            cv.create_text(px + 14 + (W - 28 - px - 14) / 2, H - 74, text=texto, fill=TEXTO,
                           width=W - 28 - px - 50, justify="center", font=(FUENTE, 13, "bold"))
        mejor_txt = f"{self.hist_mejor[-1]:.3f}" if self.hist_mejor else "—"
        self.lbl_info.config(text=f"Generación {self.gen}   ·   Mejor del momento {mejor_txt}")

    def destroy(self):
        self.app.unbind("<Escape>")
        super().destroy()


# ===========================================================================
# VENTANA PRINCIPAL
# ===========================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Algoritmo Genético Simple · Horario de estudio")
        self.geometry("1280x800")
        self.minsize(1180, 720)
        self.configure(bg=BG)
        self.params = dict(ags.PARAMETROS_INICIALES)
        self.contenedor = tk.Frame(self, bg=BG)
        self.contenedor.pack(fill="both", expand=True)
        self.pantalla = None
        self.mostrar_menu()

    def _mostrar(self, crear):
        # Primero se cierra la pantalla actual (y sus atajos de teclado),
        # después se construye la nueva.
        if self.pantalla is not None:
            self.pantalla.destroy()
        self.pantalla = crear()
        self.pantalla.pack(fill="both", expand=True)

    def mostrar_menu(self):
        self._mostrar(lambda: PantallaMenu(self))

    def mostrar_paso(self):
        self._mostrar(lambda: PantallaPaso(self, ejemplo=False))

    def mostrar_ejemplo(self):
        self._mostrar(lambda: PantallaPaso(self, ejemplo=True))

    def mostrar_auto(self):
        self._mostrar(lambda: PantallaAuto(self))

    def mostrar_parametros(self):
        self._mostrar(lambda: PantallaParametros(self))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
