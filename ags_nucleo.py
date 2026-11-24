import random

# ---------------------------------------------------------------------------
# DATOS DEL PROBLEMA
# ---------------------------------------------------------------------------
MATERIAS = ["Cálculo", "Programación", "Física", "Inglés"]
ABREVIATURAS = ["Cál", "Prog", "Fís", "Ing"]
HORAS_NECESARIAS = [6, 5, 4, 3]            # suman 18 horas por semana
BITS_POR_MATERIA = 3                        # 3 bits -> de 0 a 7 horas
HORAS_MAXIMAS = 2 ** BITS_POR_MATERIA - 1   # 7
LONGITUD = BITS_POR_MATERIA * len(MATERIAS)  # 12 bits en total

NOMBRES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"       # nombres de los individuos

PARAMETROS_INICIALES = {
    "n_visual": 8,        # individuos en el modo paso a paso (4 a 12)
    "n_auto": 30,         # individuos en la ejecución automática
    "generaciones": 100,  # máximo de generaciones (modo automático)
    "p_cruce": 0.8,       # probabilidad de cruce
    "p_mutacion": 0.05,   # probabilidad de mutación por bit
}

# Ejemplo del anteproyecto (población fija y "azar" controlado)
EJEMPLO_POBLACION = ["101 011 100 010",   # A
                     "110 101 011 011",   # B
                     "010 111 001 100",   # C
                     "100 100 101 001"]   # D
EJEMPLO_GUION = {
    "giros": (0.62, 0.15),   # ruleta: gana B y luego A
    "punto": 6,              # el cruce corta después del bit 6
    "mut1": [11],            # se invierte el último bit del hijo 1
    "mut2": [],              # el hijo 2 no muta
}


# ---------------------------------------------------------------------------
# CODIFICACIÓN
# ---------------------------------------------------------------------------
def decodificar(cromosoma):
    """12 bits -> [horas_calculo, horas_programacion, horas_fisica, horas_ingles]."""
    horas = []
    for i in range(0, LONGITUD, BITS_POR_MATERIA):
        bits = cromosoma[i:i + BITS_POR_MATERIA]
        horas.append(int("".join(str(b) for b in bits), 2))
    return horas


def texto_cromosoma(cromosoma):
    """[1,1,0,1,0,1,...] -> '110 101 100 011'."""
    cadena = "".join(str(b) for b in cromosoma)
    return " ".join(cadena[i:i + BITS_POR_MATERIA]
                    for i in range(0, LONGITUD, BITS_POR_MATERIA))


def desde_texto(texto):
    """'110 101 100 011' -> lista de bits."""
    return [int(c) for c in texto if c in "01"]


# ---------------------------------------------------------------------------
# FUNCIÓN DE APTITUD
# ---------------------------------------------------------------------------
def calcular_error(horas):
    """error = |h1-6| + |h2-5| + |h3-4| + |h4-3|"""
    return sum(abs(h - n) for h, n in zip(horas, HORAS_NECESARIAS))


def calcular_fitness(cromosoma):
    """fitness = 1 / (1 + error). Vale 1.0 cuando el horario es perfecto."""
    return 1 / (1 + calcular_error(decodificar(cromosoma)))


def evaluar_poblacion(poblacion):
    """Lista con el fitness de cada individuo."""
    return [calcular_fitness(c) for c in poblacion]


# ---------------------------------------------------------------------------
# POBLACIÓN INICIAL
# ---------------------------------------------------------------------------
def crear_poblacion(n):
    """n cromosomas de 12 bits generados al azar."""
    return [[random.randint(0, 1) for _ in range(LONGITUD)] for _ in range(n)]


# ---------------------------------------------------------------------------
# SELECCIÓN POR RULETA
# ---------------------------------------------------------------------------
def calcular_probabilidades(fitnesses):
    """probabilidad_i = fitness_i / suma de todos los fitness."""
    total = sum(fitnesses)
    return [f / total for f in fitnesses]


def ruleta(fitnesses, giro=None):
    """
    Gira la ruleta una vez. Devuelve (indice_elegido, giro).
    'giro' es un número entre 0 y 1; si no se da, se genera al azar.
    El individuo elegido es aquel cuya rebanada contiene al giro.
    """
    if giro is None:
        giro = random.random()
    acumulado = 0.0
    for i, p in enumerate(calcular_probabilidades(fitnesses)):
        acumulado += p
        if giro <= acumulado:
            return i, giro
    return len(fitnesses) - 1, giro


# ---------------------------------------------------------------------------
# CRUCE DE UN PUNTO
# ---------------------------------------------------------------------------
def cruce(padre1, padre2, p_cruce, punto=None):
    """
    Cruce de un punto. Devuelve (hijo1, hijo2, punto).
    Si no hubo cruce (por la probabilidad), los hijos son copias y punto = None.
    Si se da 'punto', el cruce siempre se realiza en ese punto.
    """
    if punto is None:
        if random.random() >= p_cruce:
            return padre1[:], padre2[:], None
        punto = random.randint(1, LONGITUD - 1)
    hijo1 = padre1[:punto] + padre2[punto:]
    hijo2 = padre2[:punto] + padre1[punto:]
    return hijo1, hijo2, punto


# ---------------------------------------------------------------------------
# MUTACIÓN
# ---------------------------------------------------------------------------
def mutacion(cromosoma, p_mutacion, posiciones=None):
    """
    Invierte bits. Devuelve (cromosoma_mutado, posiciones_invertidas).
    Cada bit se invierte con probabilidad p_mutacion.
    Si se da 'posiciones', se invierten exactamente esos bits.
    """
    if posiciones is None:
        posiciones = [i for i in range(LONGITUD) if random.random() < p_mutacion]
    nuevo = cromosoma[:]
    for i in posiciones:
        nuevo[i] = 1 - nuevo[i]
    return nuevo, list(posiciones)


# ---------------------------------------------------------------------------
# UNA PAREJA COMPLETA Y UNA GENERACIÓN COMPLETA
# ---------------------------------------------------------------------------
def reproducir_pareja(poblacion, fitnesses, p_cruce, p_mutacion, guion=None):
    """
    Ruleta (x2) + cruce + mutación. Devuelve un diccionario con todos los
    detalles para poder mostrarlos paso a paso.
    'guion' permite fijar el "azar" (se usa en el ejemplo del anteproyecto).
    """
    g = guion or {}
    giros = g.get("giros", (None, None))
    i1, giro1 = ruleta(fitnesses, giros[0])
    i2, giro2 = ruleta(fitnesses, giros[1])
    padre1, padre2 = poblacion[i1], poblacion[i2]

    cruzado1, cruzado2, punto = cruce(padre1, padre2, p_cruce, g.get("punto"))
    hijo1, mut1 = mutacion(cruzado1, p_mutacion, g.get("mut1"))
    hijo2, mut2 = mutacion(cruzado2, p_mutacion, g.get("mut2"))

    return {
        "i1": i1, "i2": i2, "giro1": giro1, "giro2": giro2,
        "padre1": padre1[:], "padre2": padre2[:],
        "punto": punto,
        "cruzado1": cruzado1, "cruzado2": cruzado2,
        "hijo1": hijo1, "hijo2": hijo2,
        "mut1": mut1, "mut2": mut2,
    }


def siguiente_generacion(poblacion, fitnesses, p_cruce, p_mutacion, pareja_inicial=None):
    """
    Construye la nueva población del mismo tamaño que la actual.
    Si se da 'pareja_inicial' (resultado de reproducir_pareja), sus dos hijos
    ocupan los primeros lugares y el resto se genera con nuevas parejas.
    """
    n = len(poblacion)
    nueva = []
    if pareja_inicial is not None:
        nueva += [pareja_inicial["hijo1"], pareja_inicial["hijo2"]]
    while len(nueva) < n:
        d = reproducir_pareja(poblacion, fitnesses, p_cruce, p_mutacion)
        nueva.append(d["hijo1"])
        if len(nueva) < n:
            nueva.append(d["hijo2"])
    return nueva[:n]
