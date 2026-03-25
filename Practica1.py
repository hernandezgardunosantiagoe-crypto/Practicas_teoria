import flet as ft
import itertools
import os

# ─────────────────────────────────────────────
#  LÓGICA (sin UI — fácil de reutilizar/testear)
# ─────────────────────────────────────────────

def calcular_subcadenas(cadena: str) -> dict:
    n = len(cadena)
    subcadenas = [cadena[i:j] for i in range(n) for j in range(i + 1, n + 1)]
    prefijos   = [cadena[:i] for i in range(1, n + 1)]
    sufijos    = [cadena[i:] for i in range(n)]
    return {"cadena": cadena, "subcadenas": subcadenas,
            "prefijos": prefijos, "sufijos": sufijos}

def formatear_subcadenas(datos: dict) -> str:
    cadena = datos["cadena"]
    texto  = f"CADENA: '{cadena}'\n\n"
    texto += f"SUBCADENAS ({len(datos['subcadenas'])}):\n"
    texto += ", ".join(f"'{s}'" for s in datos["subcadenas"]) + "\n\n"
    texto += f"PREFIJOS ({len(datos['prefijos'])}):\n"
    texto += ", ".join(f"'{p}'" for p in datos["prefijos"]) + "\n\n"
    texto += f"SUFIJOS ({len(datos['sufijos'])}):\n"
    texto += ", ".join(f"'{s}'" for s in datos["sufijos"])
    return texto

def calcular_cerraduras(alfabeto: list[str], max_len: int) -> dict:
    kleene   = [""]
    positiva = []
    for i in range(1, max_len + 1):
        for combo in itertools.product(alfabeto, repeat=i):
            cadena = "".join(combo)
            kleene.append(cadena)
            positiva.append(cadena)
    return {"alfabeto": alfabeto, "max_len": max_len,
            "kleene": kleene, "positiva": positiva}

def formatear_cerraduras(datos: dict) -> str:
    alfabeto = datos["alfabeto"]
    max_len  = datos["max_len"]
    texto    = f"ALFABETO: {{{', '.join(alfabeto)}}}\n"
    texto   += f"LONGITUD MÁXIMA: {max_len}\n\n"
    texto   += f"CERRADURA DE KLEENE (Σ*) — {len(datos['kleene'])} cadenas:\n"

    for i in range(max_len + 1):
        if i == 0:
            cadenas = ["ε (cadena vacía)"]
        else:
            cadenas = ["".join(p) for p in itertools.product(alfabeto, repeat=i)]
        texto += f"  Longitud {i}: " + ", ".join(f"'{c}'" for c in cadenas) + "\n"

    texto += f"\nCERRADURA POSITIVA (Σ+) — {len(datos['positiva'])} cadenas:\n"
    for i in range(1, max_len + 1):
        cadenas = ["".join(p) for p in itertools.product(alfabeto, repeat=i)]
        texto += f"  Longitud {i}: " + ", ".join(f"'{c}'" for c in cadenas) + "\n"

    return texto

def guardar_archivo(nombre: str, contenido: str) -> str:
    ruta = os.path.abspath(nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta

# ─────────────────────────────────────────────
#  LÓGICA DE AUTÓMATAS (AFD, AFN, AFN-λ)
# ─────────────────────────────────────────────

def cerradura_epsilon(estados: set, transiciones: dict) -> set:
    """Calcula la λ-cerradura (o ε-cerradura) de un conjunto de estados."""
    pila = list(estados)
    cerradura = set(estados)
    
    while pila:
        estado_actual = pila.pop()
        # Verificamos si hay transiciones lambda ('E')
        if estado_actual in transiciones and 'E' in transiciones[estado_actual]:
            para_agregar = set(transiciones[estado_actual]['E']) - cerradura
            cerradura.update(para_agregar)
            pila.extend(para_agregar)
            
    return cerradura

def mover(estados: set, simbolo: str, transiciones: dict) -> set:
    """Calcula el conjunto de estados alcanzables con un símbolo dado."""
    alcanzables = set()
    for estado in estados:
        if estado in transiciones and simbolo in transiciones[estado]:
            alcanzables.update(transiciones[estado][simbolo])
    return alcanzables

def simular_AFN(transiciones: dict, estado_inicial: str, estados_aceptacion: set, cadena: str) -> dict:
    """Simula un AFN o AFN-λ usando conjuntos de estados."""
    estados_actuales = cerradura_epsilon({estado_inicial}, transiciones)
    pasos = [(estados_actuales.copy(), "Inicio (con λ-cerradura)")]
    
    for simbolo in cadena:
        alcanzables = mover(estados_actuales, simbolo, transiciones)
        estados_actuales = cerradura_epsilon(alcanzables, transiciones)
        pasos.append((estados_actuales.copy(), f"Leer '{simbolo}' -> {estados_actuales if estados_actuales else '∅'}"))
        
        if not estados_actuales:
            break # Estado muerto
            
    aceptada = bool(estados_actuales.intersection(estados_aceptacion))
    return {"aceptada": aceptada, "pasos": pasos, "estados_finales": estados_actuales}

def formatear_resultado_afn(resultado: dict, cadena: str, estado_inicial: str, estados_aceptacion: set) -> str:
    aceptada = resultado["aceptada"]
    texto  = f"TIPO: AFN / AFN-λ\n"
    texto += f"CADENA EVALUADA: '{cadena}'\n"
    texto += f"ESTADO INICIAL: {estado_inicial}\n"
    texto += f"ESTADOS DE ACEPTACIÓN: {{{', '.join(sorted(estados_aceptacion))}}}\n\n"
    texto += "─── TRAZA DE EJECUCIÓN (CONJUNTOS) ───\n"

    for i, (conjunto, nota) in enumerate(resultado["pasos"]):
        conjunto_str = "{" + ", ".join(sorted(conjunto)) + "}" if conjunto else "∅"
        texto += f"  Paso {i}: {nota}\n"

    texto += "\n" + "=" * 35 + "\n"
    texto += f"RESULTADO: {'CADENA ACEPTADA' if aceptada else 'CADENA RECHAZADA'}\n"
    texto += "=" * 35 + "\n"
    return texto

def convertir_AFN_a_AFD(transiciones: dict, estado_inicial: str, estados_aceptacion: set, simbolos: list) -> str:
    """Convierte un AFN/AFN-λ a AFD usando Construcción de Subconjuntos."""
    simbolos_reales = [s for s in simbolos if s != 'E']
    
    estado_inicial_afd = frozenset(cerradura_epsilon({estado_inicial}, transiciones))
    estados_afd = [estado_inicial_afd]
    transiciones_afd = {}
    
    cola = [estado_inicial_afd]
    
    while cola:
        actual = cola.pop(0)
        transiciones_afd[actual] = {}
        
        for sim in simbolos_reales:
            destino = frozenset(cerradura_epsilon(mover(set(actual), sim, transiciones), transiciones))
            if destino:
                transiciones_afd[actual][sim] = destino
                if destino not in estados_afd:
                    estados_afd.append(destino)
                    cola.append(destino)
                    
    # Formatear el resultado para mostrarlo
    def format_set(s):
        return "{" + ",".join(sorted(s)) + "}" if s else "∅"

    texto = "─── CONVERSIÓN DE AFN A AFD ───\n\n"
    texto += f"NUEVO ESTADO INICIAL:\n{format_set(estado_inicial_afd)}\n\n"
    
    nuevos_aceptacion = [s for s in estados_afd if set(s).intersection(estados_aceptacion)]
    texto += "NUEVOS ESTADOS DE ACEPTACIÓN:\n"
    for na in nuevos_aceptacion:
         texto += f"- {format_set(na)}\n"
         
    texto += "\nNUEVA TABLA DE TRANSICIONES (AFD):\n"
    for estado in estados_afd:
        for sim in simbolos_reales:
            destino = transiciones_afd[estado].get(sim, frozenset())
            texto += f"δ({format_set(estado)}, '{sim}') = {format_set(destino)}\n"

    return texto

# ─────────────────────────────────────────────
#  VENTANAS DE RESULTADOS
# ─────────────────────────────────────────────

def abrir_ventana_generica(page: ft.Page, titulo: str, texto: str, icono=""):
    def cerrar(e):
        dialogo.open = False
        page.update()

    def guardar(e):
        try:
            ruta = guardar_archivo("resultado.txt", texto)
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Guardado en: {ruta}"), open=True))
        except Exception as ex:
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Error al guardar: {ex}"), open=True))
        page.update()

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Row([ft.Text(f"{icono} {titulo}", weight=ft.FontWeight.BOLD, size=18)]),
        content=ft.Container(
            width=650, height=450,
            content=ft.TextField(value=texto, multiline=True, read_only=True, expand=True)
        ),
        actions=[
            ft.TextButton("Guardar", on_click=guardar),
            ft.TextButton("Cerrar", on_click=cerrar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()

# ─────────────────────────────────────────────
#  SECCIONES DE LA PANTALLA PRINCIPAL
# ─────────────────────────────────────────────

def seccion_subcadenas(page: ft.Page) -> ft.Column:
    campo_cadena = ft.TextField(label="Ingrese una cadena", width=400)
    
    def on_calcular(e):
        cadena = campo_cadena.value.strip()
        if not cadena: return
        datos = calcular_subcadenas(cadena)
        abrir_ventana_generica(page, "Subcadenas, Prefijos y Sufijos", formatear_subcadenas(datos), "✂️")

    return ft.Column([
        ft.Text("1. Subcadenas, Prefijos y Sufijos", size=20, weight=ft.FontWeight.BOLD),
        campo_cadena,
        ft.ElevatedButton("Calcular", on_click=on_calcular),
    ], spacing=12)

def seccion_cerraduras(page: ft.Page) -> ft.Column:
    campo_alfabeto = ft.TextField(label="Alfabeto (comas)", width=400)
    campo_longitud = ft.TextField(label="Longitud", width=180, value="3", keyboard_type=ft.KeyboardType.NUMBER)

    def on_calcular(e):
        alfabeto = [s.strip() for s in campo_alfabeto.value.split(",") if s.strip()]
        if not alfabeto: return
        try:
            max_len = int(campo_longitud.value)
            datos = calcular_cerraduras(alfabeto, max_len)
            abrir_ventana_generica(page, "Cerraduras", formatear_cerraduras(datos), "♾️")
        except ValueError:
            pass

    return ft.Column([
        ft.Text("2. Cerradura de Kleene y Positiva", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([campo_alfabeto, campo_longitud]),
        ft.ElevatedButton("Calcular", on_click=on_calcular),
    ], spacing=12)

def seccion_automata(page: ft.Page) -> ft.Column:
    estados  = ["q0", "q1"]
    simbolos = ["a", "b"]
    celdas: dict = {}

    tabla_container = ft.Column(scroll=ft.ScrollMode.AUTO)
    campo_estado_inicial = ft.TextField(label="Estado inicial", value="q0", width=150)
    campo_estados_acept  = ft.TextField(label="Estados de aceptación (comas)", width=300)
    campo_cadena         = ft.TextField(label="Cadena a evaluar", width=300)

    def reconstruir_tabla():
        celdas.clear()
        tabla_container.controls.clear()

        encabezado = ft.Row([ft.Container(content=ft.Text("δ", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), width=90, bgcolor="#E0E0E0", padding=5)] + 
                            [ft.Container(content=ft.Text(s, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), width=110, bgcolor="#E0E0E0", padding=5) for s in simbolos])
        tabla_container.controls.append(encabezado)

        for i, estado in enumerate(estados):
            fila_celdas = []
            for j, _ in enumerate(simbolos):
                tf = ft.TextField(hint_text="ej: q1,q2", width=100, height=45, text_size=12)
                celdas[(i, j)] = tf
                fila_celdas.append(tf)

            fila = ft.Row([ft.Container(content=ft.Text(estado, weight=ft.FontWeight.BOLD), width=90, padding=5)] + fila_celdas)
            tabla_container.controls.append(fila)
        page.update()

    def agregar_estado(e):
        estados.append(f"q{len(estados)}")
        reconstruir_tabla()

    def quitar_estado(e):
        if len(estados) > 1:
            estados.pop()
            reconstruir_tabla()

    def agregar_simbolo(e):
        letras = "abcdefghijklmnopqrstuvwxyz0123456789"
        nuevo  = letras[len(simbolos)] if len(simbolos) < len(letras) else str(len(simbolos))
        simbolos.append(nuevo)
        reconstruir_tabla()
        
    def agregar_epsilon(e):
        if 'E' not in simbolos:
            simbolos.append('E')
            reconstruir_tabla()

    def quitar_simbolo(e):
        if len(simbolos) > 1:
            simbolos.pop()
            reconstruir_tabla()
            
    def recolectar_transiciones():
        transiciones = {}
        for i, estado in enumerate(estados):
            transiciones[estado] = {}
            for j, simbolo in enumerate(simbolos):
                val_str = celdas[(i, j)].value.strip()
                if val_str:
                    # Separar por comas para soportar AFN
                    destinos = [s.strip() for s in val_str.split(",") if s.strip()]
                    transiciones[estado][simbolo] = destinos
        return transiciones

    def on_simular(e):
        ei = campo_estado_inicial.value.strip()
        ea = {s.strip() for s in campo_estados_acept.value.split(",") if s.strip()}
        cadena = campo_cadena.value
        transiciones = recolectar_transiciones()
        
        resultado = simular_AFN(transiciones, ei, ea, cadena)
        texto = formatear_resultado_afn(resultado, cadena, ei, ea)
        icono = "✅" if resultado["aceptada"] else "❌"
        abrir_ventana_generica(page, "Resultado Simulación", texto, icono)
        
    def on_convertir(e):
        ei = campo_estado_inicial.value.strip()
        ea = {s.strip() for s in campo_estados_acept.value.split(",") if s.strip()}
        transiciones = recolectar_transiciones()
        
        texto = convertir_AFN_a_AFD(transiciones, ei, ea, simbolos)
        abrir_ventana_generica(page, "Conversión a AFD", texto, "⚙️")

    reconstruir_tabla()

    botones_tabla = ft.Row([
        ft.ElevatedButton("+ Estado",  on_click=agregar_estado),
        ft.ElevatedButton("- Estado",  on_click=quitar_estado),
        ft.ElevatedButton("+ Símbolo", on_click=agregar_simbolo),
        ft.ElevatedButton("+ λ/ε (E)", on_click=agregar_epsilon, bgcolor=ft.Colors.AMBER_100),
        ft.ElevatedButton("- Símbolo", on_click=quitar_simbolo),
    ], spacing=8)

    return ft.Column([
        ft.Text("3. Autómatas (Soporta AFD, AFN y AFN-λ)", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Tabla de transición δ: (Usa comas para múltiples estados, ej: q1,q2)", weight=ft.FontWeight.W_600),
        botones_tabla,
        ft.Container(content=tabla_container, border=ft.border.all(1, "#BDBDBD"), border_radius=8, padding=10),
        ft.Row([campo_estado_inicial, campo_estados_acept], spacing=12),
        campo_cadena,
        ft.Row([
            ft.ElevatedButton("Simular Cadena", on_click=on_simular, bgcolor=ft.Colors.BLUE_100),
            ft.ElevatedButton("Convertir a AFD", on_click=on_convertir, bgcolor=ft.Colors.GREEN_100),
        ])
    ], spacing=12)

# ─────────────────────────────────────────────
#  APP PRINCIPAL
# ─────────────────────────────────────────────

class App:
    def main(self, page: ft.Page):
        page.title = "Teoría de la Computación - ESCOM"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 24
        page.scroll = ft.ScrollMode.AUTO

        page.add(
            seccion_subcadenas(page),
            ft.Divider(height=30),
            seccion_cerraduras(page),
            ft.Divider(height=30),
            seccion_automata(page),
        )

if __name__ == "__main__":
    ft.app(target=App().main)