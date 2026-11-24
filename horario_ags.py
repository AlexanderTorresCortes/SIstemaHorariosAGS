import os
import random
import sys

# Para que los acentos se vean bien en la consola de Windows.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# DATOS DEL PROBLEMA
# ---------------------------------------------------------------------------
MATERIAS = ["Cálculo", "Programación", "Física", "Inglés"]
HORAS_NECESARIAS = [6, 5, 4, 3]          # suman 18 horas
BITS_POR_MATERIA = 3                      # 3 bits -> de 0 a 7 horas
LONGITUD = BITS_POR_MATERIA * len(MATERIAS)   # 12 bits en total

# Parámetros del algoritmo (se pueden cambiar desde el menú)
PARAMETROS = {
    "poblacion": 30,       # número de individuos
    "generaciones": 100,   # máximo de generaciones
    "p_cruce": 0.8,        # probabilidad de cruce
    "p_mutacion": 0.02,    # probabilidad de mutación por bit
}


# ---------------------------------------------------------------------------
# CODIFICACIÓN Y FITNESS
# ---------------------------------------------------------------------------
def decodificar(cromosoma):
    """Convierte los 12 bits en la lista de horas [h1, h2, h3, h4]."""
    horas = []
    for i in range(0, LONGITUD, BITS_POR_MATERIA):
        bits = cromosoma[i:i + BITS_POR_MATERIA]
        horas.append(int("".join(str(b) for b in bits), 2))
    return horas


def calcular_error(horas):
    """Suma de las diferencias absolutas contra las horas necesarias."""
    return sum(abs(h - n) for h, n in zip(horas, HORAS_NECESARIAS))


def calcular_fitness(cromosoma):
    """fitness = 1 / (1 + error). A menor error, mayor fitness (máx. 1.0)."""
    error = calcular_error(decodificar(cromosoma))
    return 1 / (1 + error)


def texto_cromosoma(cromosoma):
    """Muestra el cromosoma en grupos de 3 bits: '110 101 100 011'."""
    cadena = "".join(str(b) for b in cromosoma)
    return " ".join(cadena[i:i + BITS_POR_MATERIA]
                    for i in range(0, LONGITUD, BITS_POR_MATERIA))


def desde_texto(texto):
    """Convierte '110 101 100 011' en una lista de bits."""
    return [int(c) for c in texto if c in "01"]


# ---------------------------------------------------------------------------
# OPERADORES GENÉTICOS
# ---------------------------------------------------------------------------
def crear_poblacion(n):
    """Población inicial: n cromosomas de bits aleatorios."""
    return [[random.randint(0, 1) for _ in range(LONGITUD)] for _ in range(n)]


def ruleta(poblacion, fitnesses):
    """Selección por ruleta: más fitness = más probabilidad de ser elegido."""
    giro = random.random() * sum(fitnesses)
    acumulado = 0
    for individuo, f in zip(poblacion, fitnesses):
        acumulado += f
        if giro <= acumulado:
            return individuo
    return poblacion[-1]


def cruce(padre1, padre2, p_cruce):
    """Cruce de un punto: los padres intercambian sus mitades."""
    if random.random() < p_cruce:
        punto = random.randint(1, LONGITUD - 1)
        return padre1[:punto] + padre2[punto:], padre2[:punto] + padre1[punto:]
    return padre1[:], padre2[:]          # sin cruce: los hijos son copias


def mutacion(cromosoma, p_mutacion):
    """Cada bit se invierte con una probabilidad muy baja."""
    return [1 - b if random.random() < p_mutacion else b for b in cromosoma]


# ---------------------------------------------------------------------------
# ALGORITMO GENÉTICO COMPLETO
# ---------------------------------------------------------------------------
def algoritmo_genetico(n, generaciones, p_cruce, p_mutacion, mostrar=True):
    """Ejecuta el AGS y devuelve un diccionario con los resultados."""
    poblacion = crear_poblacion(n)

    hist_mejor, hist_promedio = [], []
    mejor_global, fitness_global, gen_global = None, -1, 0

    for gen in range(1, generaciones + 1):
        # 1) Evaluación
        fits = [calcular_fitness(c) for c in poblacion]
        mejor_gen = max(fits)
        promedio = sum(fits) / len(fits)
        hist_mejor.append(mejor_gen)
        hist_promedio.append(promedio)

        # Guardamos el mejor horario encontrado en toda la ejecución
        if mejor_gen > fitness_global:
            fitness_global = mejor_gen
            mejor_global = poblacion[fits.index(mejor_gen)][:]
            gen_global = gen

        if mostrar:
            horas = decodificar(poblacion[fits.index(mejor_gen)])
            print(f"Gen {gen:3d} | mejor horario: {horas} | "
                  f"fitness mejor: {mejor_gen:.3f} | promedio: {promedio:.3f}")

        # Condición de paro: horario perfecto
        if fitness_global >= 1.0:
            break

        # 2) Nueva generación: selección + cruce + mutación
        nueva = []
        while len(nueva) < n:
            padre1 = ruleta(poblacion, fits)
            padre2 = ruleta(poblacion, fits)
            hijo1, hijo2 = cruce(padre1, padre2, p_cruce)
            nueva.append(mutacion(hijo1, p_mutacion))
            if len(nueva) < n:
                nueva.append(mutacion(hijo2, p_mutacion))
        poblacion = nueva

    return {
        "mejor": mejor_global,
        "fitness": fitness_global,
        "generacion": gen_global,
        "generaciones_usadas": len(hist_mejor),
        "hist_mejor": hist_mejor,
        "hist_promedio": hist_promedio,
    }


def mostrar_resultado(res):
    """Imprime el mejor horario encontrado en forma de tabla."""
    horas = decodificar(res["mejor"])
    error = calcular_error(horas)

    print("\n" + "=" * 58)
    print("MEJOR HORARIO ENCONTRADO")
    print("=" * 58)
    print(f"Cromosoma: {texto_cromosoma(res['mejor'])}\n")
    print(f"{'Materia':<15}{'Necesita':>10}{'Asignadas':>12}{'Diferencia':>12}")
    print("-" * 49)
    for materia, necesita, asignadas in zip(MATERIAS, HORAS_NECESARIAS, horas):
        print(f"{materia:<15}{necesita:>10}{asignadas:>12}{asignadas - necesita:>+12}")
    print("-" * 49)
    print(f"{'Total':<15}{sum(HORAS_NECESARIAS):>10}{sum(horas):>12}")
    print(f"\nError   : {error}")
    print(f"Fitness : {res['fitness']:.3f}")
    print(f"Se encontró en la generación {res['generacion']} "
          f"(se ejecutaron {res['generaciones_usadas']}).")
    if error == 0:
        print("¡Horario perfecto!")
    print("=" * 58)


# ---------------------------------------------------------------------------
# OPCIÓN 1: EJECUCIÓN EN CONSOLA
# ---------------------------------------------------------------------------
def opcion_consola():
    p = PARAMETROS
    print("\nEjecutando el algoritmo genético...\n")
    res = algoritmo_genetico(p["poblacion"], p["generaciones"],
                             p["p_cruce"], p["p_mutacion"], mostrar=True)
    mostrar_resultado(res)


# ---------------------------------------------------------------------------
# OPCIÓN 2: EJECUCIÓN CON GRÁFICA
# ---------------------------------------------------------------------------
def opcion_grafica():
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nNo se encontró matplotlib. Instálalo con:")
        print("    pip install matplotlib")
        return

    p = PARAMETROS
    print("\nEjecutando el algoritmo genético...")
    res = algoritmo_genetico(p["poblacion"], p["generaciones"],
                             p["p_cruce"], p["p_mutacion"], mostrar=False)
    mostrar_resultado(res)

    gens = range(1, len(res["hist_mejor"]) + 1)
    plt.figure(figsize=(9, 5))
    plt.plot(gens, res["hist_mejor"], label="Mejor fitness de la generación",
             color="tab:blue", linewidth=2)
    plt.plot(gens, res["hist_promedio"], label="Fitness promedio",
             color="tab:orange", linestyle="--")
    plt.axhline(1.0, color="gray", linestyle=":", label="Horario perfecto (1.0)")
    plt.title("Evolución del fitness - Horario de estudio")
    plt.xlabel("Generación")
    plt.ylabel("Fitness")
    plt.ylim(0, 1.05)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    # Guarda la gráfica junto al programa y la muestra en pantalla
    carpeta = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(carpeta, "evolucion_fitness.png")
    plt.savefig(ruta, dpi=150)
    print(f"\nGráfica guardada en: {ruta}")
    plt.show()


# ---------------------------------------------------------------------------
# OPCIÓN 3: MODO PASO A PASO (mismo ejemplo del anteproyecto)
# ---------------------------------------------------------------------------
def pausa():
    input("\n   [Enter para continuar]")


def encabezado(texto):
    print("\n" + "-" * 70)
    print(texto)
    print("-" * 70)


def opcion_paso_a_paso():
    print("\n" + "=" * 70)
    print("MODO PASO A PASO - población de 4 individuos")
    print("Necesidades: Cálculo 6 h, Programación 5 h, Física 4 h, Inglés 3 h")
    print("=" * 70)

    # --- Paso 1: población inicial (fija, la del anteproyecto) --------------
    encabezado("PASO 1. Población inicial")
    nombres = ["A", "B", "C", "D"]
    poblacion = [desde_texto(t) for t in ("101 011 100 010",
                                          "110 101 011 011",
                                          "010 111 001 100",
                                          "100 100 101 001")]
    for nombre, c in zip(nombres, poblacion):
        print(f"  Individuo {nombre}: {texto_cromosoma(c)}")
    pausa()

    # --- Paso 2: evaluación --------------------------------------------------
    encabezado("PASO 2. Evaluación: error y fitness = 1 / (1 + error)")
    fits = []
    print(f"  {'Ind.':<6}{'Horas (C,P,F,I)':<20}{'Error':>6}{'Fitness':>10}")
    for nombre, c in zip(nombres, poblacion):
        horas = decodificar(c)
        error = calcular_error(horas)
        f = calcular_fitness(c)
        fits.append(f)
        print(f"  {nombre:<6}{str(horas):<20}{error:>6}{f:>10.3f}")
    total = sum(fits)
    print(f"\n  Suma de fitness = {total:.3f}")
    pausa()

    # --- Paso 3: selección por ruleta ---------------------------------------
    encabezado("PASO 3. Selección por ruleta")
    probs = [f / total for f in fits]
    print("  Probabilidad = fitness / suma de fitness\n")
    acumulado = 0
    limites = []
    for nombre, f, pr in zip(nombres, fits, probs):
        acumulado += pr
        limites.append(acumulado)
        print(f"  {nombre}: {f:.3f} / {total:.3f} = {pr:.3f} ({pr * 100:.1f} %)"
              f"   -> rebanada hasta {acumulado:.3f}")

    def quien_gana(giro):
        for nombre, lim in zip(nombres, limites):
            if giro <= lim:
                return nombre
        return nombres[-1]

    giro1, giro2 = 0.62, 0.15      # números "aleatorios" del ejemplo
    padre1, padre2 = quien_gana(giro1), quien_gana(giro2)
    print(f"\n  Giro 1: sale {giro1} -> gana {padre1}")
    print(f"  Giro 2: sale {giro2} -> gana {padre2}")
    pausa()

    # --- Paso 4: cruce de un punto ------------------------------------------
    encabezado("PASO 4. Cruce de un punto (corte después del bit 6)")
    cb = poblacion[nombres.index(padre1)]
    ca = poblacion[nombres.index(padre2)]
    punto = 6
    hijo1 = cb[:punto] + ca[punto:]
    hijo2 = ca[:punto] + cb[punto:]

    def con_corte(c):
        cad = "".join(str(b) for b in c)
        return cad[:punto] + " | " + cad[punto:]

    print(f"  Padre {padre1}: {con_corte(cb)}")
    print(f"  Padre {padre2}: {con_corte(ca)}\n")
    for nombre, h in (("Hijo 1", hijo1), ("Hijo 2", hijo2)):
        print(f"  {nombre}: {con_corte(h)} -> {decodificar(h)} -> "
              f"error {calcular_error(decodificar(h))} -> "
              f"fitness {calcular_fitness(h):.3f}")
    pausa()

    # --- Paso 5: mutación ----------------------------------------------------
    encabezado("PASO 5. Mutación (se invierte un bit del Hijo 1)")
    mutado = hijo1[:]
    mutado[-1] = 1 - mutado[-1]             # se invierte el último bit
    print(f"  Antes  : {texto_cromosoma(hijo1)} -> {decodificar(hijo1)} "
          f"-> fitness {calcular_fitness(hijo1):.3f}")
    print(f"  Después: {texto_cromosoma(mutado)} -> {decodificar(mutado)} "
          f"-> fitness {calcular_fitness(mutado):.3f}")
    if calcular_error(decodificar(mutado)) == 0:
        print("\n  ¡La mutación dejó un horario perfecto (error 0, fitness 1.0)!")
    pausa()

    # --- Paso 6 --------------------------------------------------------------
    encabezado("PASO 6. Nueva generación")
    print("  Los hijos reemplazan a la población anterior y todo se repite")
    print("  desde la evaluación, hasta encontrar fitness = 1 o llegar al")
    print("  máximo de generaciones. Eso es lo que hacen las opciones 1 y 2.")


# ---------------------------------------------------------------------------
# OPCIÓN 4: CAMBIAR PARÁMETROS
# ---------------------------------------------------------------------------
def pedir_numero(mensaje, tipo, minimo, maximo, actual):
    """Pide un número validando el rango. Enter deja el valor actual."""
    while True:
        texto = input(f"  {mensaje} [{actual}]: ").strip()
        if texto == "":
            return actual
        try:
            valor = tipo(texto)
        except ValueError:
            print("   Escribe un número válido.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"   El valor debe estar entre {minimo} y {maximo}.")


def opcion_parametros():
    print("\nParámetros actuales (Enter = dejar el valor actual)")
    PARAMETROS["poblacion"] = pedir_numero(
        "Tamaño de la población (2-500)", int, 2, 500, PARAMETROS["poblacion"])
    PARAMETROS["generaciones"] = pedir_numero(
        "Máximo de generaciones (1-5000)", int, 1, 5000, PARAMETROS["generaciones"])
    PARAMETROS["p_cruce"] = pedir_numero(
        "Probabilidad de cruce (0-1)", float, 0.0, 1.0, PARAMETROS["p_cruce"])
    PARAMETROS["p_mutacion"] = pedir_numero(
        "Probabilidad de mutación por bit (0-1)", float, 0.0, 1.0, PARAMETROS["p_mutacion"])
    print("\nParámetros actualizados.")


# ---------------------------------------------------------------------------
# MENÚ PRINCIPAL
# ---------------------------------------------------------------------------
def menu():
    while True:
        p = PARAMETROS
        print("\n" + "=" * 58)
        print("  ALGORITMO GENÉTICO SIMPLE - HORARIO DE ESTUDIO")
        print("=" * 58)
        print("  1. Ejecutar el algoritmo (consola)")
        print("  2. Ejecutar el algoritmo con gráfica de evolución")
        print("  3. Modo paso a paso (ejemplo del anteproyecto)")
        print("  4. Cambiar parámetros")
        print("  0. Salir")
        print("-" * 58)
        print(f"  Población: {p['poblacion']} | Generaciones: {p['generaciones']} | "
              f"Cruce: {p['p_cruce']} | Mutación: {p['p_mutacion']}")
        print("=" * 58)

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            opcion_consola()
        elif opcion == "2":
            opcion_grafica()
        elif opcion == "3":
            opcion_paso_a_paso()
        elif opcion == "4":
            opcion_parametros()
        elif opcion == "0":
            print("\n¡Hasta luego!")
            break
        else:
            print("\nOpción no válida. Elige 1, 2, 3, 4 o 0.")


if __name__ == "__main__":
    menu()
