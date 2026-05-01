import flet as ft
import re

# ==========================================
# SECCIÓN 1: LÓGICA COMPUTACIONAL
# ==========================================

class LogicaComputacional:
    @staticmethod
    def validar_er(expresion):
        """Valida la sintaxis de una Expresión Regular."""
        try:
            # Lógica extraída de logic_er_validator.py[cite: 1, 2]
            re.compile(expresion)
            return True
        except re.error:
            return False

# ==========================================
# SECCIÓN 2: INTERFAZ GRÁFICA (Flet UI)
# ==========================================

class Practica4App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.logica = LogicaComputacional()
        
    def render(self):
        # Configuración estética de la página[cite: 1, 2]
        self.page.title = "ESCOM - Teoría de la Computación - Práctica 4"
        self.page.theme_mode = ft.ThemeMode.DARK 
        self.page.window_width = 700
        self.page.window_height = 600
        self.page.bgcolor = "bluegrey900" 

        # Componentes Visuales
        self.titulo = ft.Text("Analizador de Lenguajes Regulares", 
                             size=32, weight="bold", color="cyanaccent")
        
        self.input_er = ft.TextField(
            label="Expresión Regular a validar",
            border_color="cyan700",
            hint_text="Ejemplo: [a-z]+[0-9]*",
            expand=True
        )

        self.btn_validar = ft.ElevatedButton(
            "Validar Sintaxis",
            icon="CHECK_CIRCLE", 
            on_click=self.ejecutar_validacion,
            style=ft.ButtonStyle(color="white", bgcolor="cyan700")
        )

        self.resultado_txt = ft.Text("", size=18)
        
        # Contenedor principal[cite: 1, 2]
        container = ft.Container(
            content=ft.Column([
                self.titulo,
                ft.Text("Materia: Teoría de la Computación", italic=True, color="grey400"),
                ft.Divider(height=20, color="transparent"),
                ft.Row([self.input_er, self.btn_validar]),
                # SOLUCIÓN DEFINITIVA: Quitamos el 'color' del Card y usamos un Container
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=self.resultado_txt,
                            padding=20
                        )
                    ),
                    bgcolor="bluegrey800", # Aquí el fondo no falla
                    border_radius=10
                ),
                ft.Divider(height=30),
                ft.Text("Módulo consolidado - Práctica 4 - ESCOM", size=12, color="grey500")
            ]),
            padding=30
        )

        self.page.add(container)

    def ejecutar_validacion(self, e):
        if not self.input_er.value:
            self.resultado_txt.value = " Ingrese una expresión para analizar"
            self.resultado_txt.color = "amber"
        else:
            es_valida = self.logica.validar_er(self.input_er.value)
            if es_valida:
                self.resultado_txt.value = f"La cadena '{self.input_er.value}' es una ER válida."
                self.resultado_txt.color = "greenaccent"
            else:
                self.resultado_txt.value = " Error Sintáctico: Estructura de ER no reconocida."
                self.resultado_txt.color = "redaccent"
        self.page.update()

# ==========================================
# PUNTO DE ENTRADA (Main)
# ==========================================

def main(page: ft.Page):
    app = Practica4App(page)
    app.render()

if __name__ == "__main__":
    # Ejecución principal consolidada[cite: 1, 2]
    ft.app(target=main)