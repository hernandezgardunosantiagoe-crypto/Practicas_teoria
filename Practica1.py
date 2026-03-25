import flet as ft
import itertools
import os


# ─────────────────────────────────────────────
#  LÓGICA (sin UI — fácil de reutilizar/testear)
# ─────────────────────────────────────────────

def calcular_subcadenas(cadena: str) -> dict:
    """Devuelve subcadenas, prefijos y sufijos de una cadena."""
    n = len(cadena)
    subcadenas = [cadena[i:j] for i in range(n) for j in range(i + 1, n + 1)]
    prefijos   = [cadena[:i] for i in range(1, n + 1)]
    sufijos    = [cadena[i:] for i in range(n)]
    return {"cadena": cadena, "subcadenas": subcadenas,
            "prefijos": prefijos, "sufijos": sufijos}


def formatear_subcadenas(datos: dict) -> str:
    """Convierte el resultado de calcular_subcadenas a texto legible."""
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
    """Devuelve cerradura de Kleene y positiva para un alfabeto dado."""
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
    """Convierte el resultado de calcular_cerraduras a texto legible."""
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
    """Guarda contenido en un archivo .txt y devuelve la ruta absoluta."""
    ruta = os.path.abspath(nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


# ─────────────────────────────────────────────
#  LÓGICA DE AUTÓMATA FINITO DETERMINISTA (AFD)
# ─────────────────────────────────────────────

def simular_AFD(transiciones: dict, estado_inicial: str,
                estados_aceptacion: set, cadena: str) -> dict:
    """
    Simula un AFD.
    transiciones = { "q0": {"a": "q1", "b": "q0"}, ... }
    """
    estado_actual = estado_inicial
    camino = [estado_actual]
    pasos  = []

    for simbolo in cadena:
        if estado_actual not in transiciones:
            pasos.append((estado_actual, simbolo, None, "Estado sin transiciones"))
            return {"aceptada": False, "camino": camino, "pasos": pasos}
        if simbolo not in transiciones[estado_actual]:
            pasos.append((estado_actual, simbolo, None, "Transición no definida"))
            return {"aceptada": False, "camino": camino, "pasos": pasos}

        siguiente = transiciones[estado_actual][simbolo]
        pasos.append((estado_actual, simbolo, siguiente, "OK"))
        estado_actual = siguiente
        camino.append(estado_actual)

    aceptada = estado_actual in estados_aceptacion
    return {"aceptada": aceptada, "camino": camino, "pasos": pasos}


def formatear_resultado_automata(resultado: dict, cadena: str,
                                  estado_inicial: str,
                                  estados_aceptacion: set) -> str:
    aceptada = resultado["aceptada"]
    texto  = f"TIPO: AFD\n"
    texto += f"CADENA EVALUADA: '{cadena}'\n"
    texto += f"ESTADO INICIAL: {estado_inicial}\n"
    texto += f"ESTADOS DE ACEPTACIÓN: {{{', '.join(sorted(estados_aceptacion))}}}\n\n"
    texto += "─── TRAZA DE EJECUCIÓN ───\n"

    for i, (src, sym, dst, nota) in enumerate(resultado["pasos"]):
        dst_str = dst if dst else "∅"
        texto += f"  Paso {i+1}: δ({src}, '{sym}') → {dst_str}   [{nota}]\n"

    texto += f"\nCAMINO: {' → '.join(resultado['camino'])}\n"
    texto += "\n" + "=" * 35 + "\n"
    texto += f"RESULTADO: {'CADENA ACEPTADA' if aceptada else 'CADENA RECHAZADA'}\n"
    texto += "=" * 35 + "\n"
    return texto


# ─────────────────────────────────────────────
#  VENTANAS DE RESULTADOS (se abren al calcular)
# ─────────────────────────────────────────────

def abrir_ventana_subcadenas(page: ft.Page, texto: str, nombre_archivo: str):
    """Abre una nueva ventana con los resultados de subcadenas."""

    def cerrar(e):
        dialogo.open = False
        page.update()

    def guardar(e):
        try:
            ruta = guardar_archivo(nombre_archivo, texto)
            snack = ft.SnackBar(content=ft.Text(f"✅ Guardado en: {ruta}"), open=True)
        except Exception as ex:
            snack = ft.SnackBar(content=ft.Text(f"❌ Error al guardar: {ex}"), open=True)
        page.overlay.append(snack)
        page.update()

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text("Subcadenas, Prefijos y Sufijos", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=600,
            height=400,
            content=ft.TextField(
                value=texto,
                multiline=True,
                read_only=True,
                expand=True,
                min_lines=15,
                max_lines=30,
            ),
        ),
        actions=[
            ft.TextButton("💾 Guardar resultados", on_click=guardar),
            ft.TextButton("Cerrar", on_click=cerrar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()


def abrir_ventana_cerraduras(page: ft.Page, texto: str, nombre_archivo: str):
    """Abre una nueva ventana con los resultados de cerraduras."""

    def cerrar(e):
        dialogo.open = False
        page.update()

    def guardar(e):
        try:
            ruta = guardar_archivo(nombre_archivo, texto)
            snack = ft.SnackBar(content=ft.Text(f"✅ Guardado en: {ruta}"), open=True)
        except Exception as ex:
            snack = ft.SnackBar(content=ft.Text(f"❌ Error al guardar: {ex}"), open=True)
        page.overlay.append(snack)
        page.update()

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cerradura de Kleene (Σ*) y Positiva (Σ+)", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=650,
            height=450,
            content=ft.TextField(
                value=texto,
                multiline=True,
                read_only=True,
                expand=True,
                min_lines=18,
                max_lines=35,
            ),
        ),
        actions=[
            ft.TextButton("💾 Guardar resultados", on_click=guardar),
            ft.TextButton("Cerrar", on_click=cerrar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()


def abrir_ventana_automata(page: ft.Page, texto: str, aceptada: bool):
    """Abre ventana con el resultado de simulación del autómata."""

    def cerrar(e):
        dialogo.open = False
        page.update()

    def guardar(e):
        try:
            ruta = guardar_archivo("resultados_automata.txt", texto)
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Guardado en: {ruta}"), open=True))
        except Exception as ex:
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Error al guardar: {ex}"), open=True))
        page.update()

    color_titulo = "green" if aceptada else "red"
    icono       = "✅" if aceptada else "❌"
    veredicto   = "CADENA ACEPTADA" if aceptada else "CADENA RECHAZADA"

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Text(f"{icono} {veredicto}", weight=ft.FontWeight.BOLD,
                    color=color_titulo, size=18),
        ]),
        content=ft.Container(
            width=650,
            height=420,
            content=ft.TextField(
                value=texto,
                multiline=True,
                read_only=True,
                expand=True,
                min_lines=18,
                max_lines=30,
            ),
        ),
        actions=[
            ft.TextButton("Guardar resultados", on_click=guardar),
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
    """Construye y devuelve la sección 1 de la UI."""

    campo_cadena = ft.TextField(
        label="Ingrese una cadena",
        hint_text="Ejemplo: hola",
        width=400,
    )

    def on_calcular(e):
        cadena = campo_cadena.value.strip()
        if not cadena:
            page.overlay.append(
                ft.SnackBar(content=ft.Text("Por favor, ingrese una cadena."), open=True)
            )
            page.update()
            return

        datos = calcular_subcadenas(cadena)
        texto = formatear_subcadenas(datos)
        abrir_ventana_subcadenas(page, texto, "resultados_subcadenas.txt")

    return ft.Column([
        ft.Text("1. Subcadenas, Prefijos y Sufijos",
                size=20, weight=ft.FontWeight.BOLD),
        campo_cadena,
        ft.Row([
            ft.ElevatedButton("Calcular", on_click=on_calcular),
        ]),
    ], spacing=12)


def seccion_cerraduras(page: ft.Page) -> ft.Column:
    """Construye y devuelve la sección 2 de la UI."""

    campo_alfabeto = ft.TextField(
        label="Ingrese el alfabeto (separado por comas)",
        hint_text="Ejemplo: a,b,c",
        width=400,
    )
    campo_longitud = ft.TextField(
        label="Longitud máxima",
        hint_text="Ejemplo: 3",
        width=180,
        value="3",
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    def on_calcular(e):
        alfabeto_str = campo_alfabeto.value.strip()
        if not alfabeto_str:
            page.overlay.append(
                ft.SnackBar(content=ft.Text("Por favor, ingrese un alfabeto."), open=True)
            )
            page.update()
            return

        try:
            max_len = int(campo_longitud.value)
            if max_len < 1:
                raise ValueError
        except ValueError:
            page.overlay.append(
                ft.SnackBar(content=ft.Text("La longitud máxima debe ser un entero ≥ 1."), open=True)
            )
            page.update()
            return

        alfabeto = [s.strip() for s in alfabeto_str.split(",") if s.strip()]
        if not alfabeto:
            page.overlay.append(
                ft.SnackBar(content=ft.Text("El alfabeto no puede estar vacío."), open=True)
            )
            page.update()
            return

        datos = calcular_cerraduras(alfabeto, max_len)
        texto = formatear_cerraduras(datos)
        abrir_ventana_cerraduras(page, texto, "resultados_cerraduras.txt")

    return ft.Column([
        ft.Text("2. Cerradura de Kleene (Σ*) y Positiva (Σ+)",
                size=20, weight=ft.FontWeight.BOLD),
        ft.Row([campo_alfabeto, campo_longitud]),
        ft.Row([
            ft.ElevatedButton("Calcular", on_click=on_calcular),
        ]),
    ], spacing=12)


def seccion_automata(page: ft.Page) -> ft.Column:
    """
    Sección 3: Simulador de Autómata Finito Determinista (AFD).

    Estado interno:
      - estados  : lista de nombres de estados  ["q0","q1",...]
      - simbolos : lista de símbolos del alfabeto ["a","b",...]
      - celdas   : dict {(fila_idx, col_idx): TextField}
    """

    # ── Estado interno ──────────────────────────────────────────
    estados  = ["q0", "q1"]
    simbolos = ["a", "b"]

    tabla_container = ft.Column(scroll=ft.ScrollMode.AUTO)

    campo_estado_inicial = ft.TextField(label="Estado inicial", value="q0", width=150)
    campo_estados_acept  = ft.TextField(label="Estados de aceptación (separados por comas)",
                                         hint_text="Ejemplo: q1, q2", width=300)
    campo_cadena         = ft.TextField(label="Cadena a evaluar",
                                         hint_text="Ejemplo: ab", width=300)

    celdas: dict = {}

    # ── Funciones de tabla ──────────────────────────────────────

    def reconstruir_tabla():
        celdas.clear()
        tabla_container.controls.clear()

        encabezado = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("δ", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    width=90, bgcolor="#E0E0E0", padding=5,
                )
            ] + [
                ft.Container(
                    content=ft.Text(s, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    width=110, bgcolor="#E0E0E0", padding=5,
                )
                for s in simbolos
            ],
        )
        tabla_container.controls.append(encabezado)

        for i, estado in enumerate(estados):
            fila_celdas = []
            for j, _ in enumerate(simbolos):
                tf = ft.TextField(hint_text="q?", width=100, height=45, text_size=12)
                celdas[(i, j)] = tf
                fila_celdas.append(tf)

            fila = ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(estado, weight=ft.FontWeight.BOLD),
                        width=90, padding=5,
                    )
                ] + fila_celdas,
            )
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

    def quitar_simbolo(e):
        if len(simbolos) > 1:
            simbolos.pop()
            reconstruir_tabla()

    # ── Determinar ──────────────────────────────────────────────

    def on_determinar(e):
        ei = campo_estado_inicial.value.strip()
        if not ei:
            page.overlay.append(ft.SnackBar(content=ft.Text("Ingresa el estado inicial."), open=True))
            page.update()
            return

        ea_str = campo_estados_acept.value.strip()
        if not ea_str:
            page.overlay.append(ft.SnackBar(content=ft.Text("Ingresa al menos un estado de aceptación."), open=True))
            page.update()
            return
        estados_acept = {s.strip() for s in ea_str.split(",") if s.strip()}

        cadena = campo_cadena.value

        transiciones: dict = {}
        for i, estado in enumerate(estados):
            transiciones[estado] = {}
            for j, simbolo in enumerate(simbolos):
                valor = celdas.get((i, j))
                val_str = valor.value.strip() if valor and valor.value else ""
                if val_str:
                    transiciones[estado][simbolo] = val_str

        resultado = simular_AFD(transiciones, ei, estados_acept, cadena)
        texto = formatear_resultado_automata(resultado, cadena, ei, estados_acept)
        abrir_ventana_automata(page, texto, resultado["aceptada"])

    reconstruir_tabla()

    botones_tabla = ft.Row([
        ft.ElevatedButton("+ Estado",  on_click=agregar_estado),
        ft.ElevatedButton("- Estado",  on_click=quitar_estado),
        ft.ElevatedButton("+ Símbolo", on_click=agregar_simbolo),
        ft.ElevatedButton("- Símbolo", on_click=quitar_simbolo),
    ], spacing=8)

    return ft.Column([
        ft.Text("3. Simulador de Autómata Finito Determinista (AFD)",
                size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Tabla de transición δ:", weight=ft.FontWeight.W_600),
        botones_tabla,
        ft.Container(
            content=tabla_container,
            border=ft.border.all(1, "#BDBDBD"),
            border_radius=8,
            padding=10,
        ),
        ft.Row([campo_estado_inicial, campo_estados_acept], spacing=12),
        campo_cadena,
        ft.ElevatedButton("Determinar", on_click=on_determinar),
    ], spacing=12)


# ─────────────────────────────────────────────
#  APP PRINCIPAL
# ─────────────────────────────────────────────

class App:
    def main(self, page: ft.Page):
        page.title = "Operaciones con Cadenas y Alfabetos"
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


def main():
    ft.app(target=App().main)


if __name__ == "__main__":
    main()