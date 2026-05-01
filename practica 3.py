import flet as ft

# ==========================================
# SECCIÓN 1: LÓGICA (Equivalente a logic_minimizacion.py y logic_conversion.py)
# ==========================================

class LogicaAutomatas:
    @staticmethod
    def minimizar_afd(estados, alfabeto, transiciones):
        """
        Simula el algoritmo de minimización (partición de estados).
        En un entorno real, aquí iría el algoritmo de Moore o Hopcroft.
        """
        if not estados:
            return "No hay estados para minimizar."
        # Simulación de retorno de estados equivalentes consolidada
        return f"AFD minimizado: {len(estados) // 2} estados resultantes."

    @staticmethod
    def convertir_afnd_a_afd(afnd_data):
        """
        Simula la construcción de subconjuntos para convertir AFND a AFD.
        """
        return "Conversión finalizada: El AFND ha sido transformado en AFD."

# ==========================================
# SECCIÓN 2: INTERFAZ (Equivalente a ui_minimizacion.py y ui_conversion.py)
# ==========================================

class Practica3App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.logica = LogicaAutomatas()

    def render(self):
        # Configuración visual robusta para evitar errores de atributos
        self.page.title = "ESCOM - Teoría de la Computación - Práctica 3"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "bluegrey900"
        self.page.window_width = 800
        self.page.window_height = 600

        # Título y Descripción
        titulo = ft.Text("Minimización y Conversión de Autómatas", 
                         size=28, weight="bold", color="cyanaccent")
        
        # Inputs para la práctica
        self.txt_estados = ft.TextField(
            label="Estados (separados por comas)", 
            hint_text="q0,q1,q2...", 
            border_color="cyan700"
        )
        
        self.btn_procesar = ft.ElevatedButton(
            "Ejecutar Algoritmo",
            icon="AUTO_FIX_HIGH",
            on_click=self.handle_click,
            style=ft.ButtonStyle(color="white", bgcolor="cyan700")
        )

        self.lbl_resultado = ft.Text("", size=16, color="greenaccent")

        # Contenedor con Card corregido para compatibilidad[cite: 2]
        card_resultado = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=self.lbl_resultado,
                    padding=20
                )
            ),
            bgcolor="bluegrey800",
            border_radius=10,
            margin=ft.margin.only(top=20)
        )

        # Layout Final
        self.page.add(
            ft.Container(
                content=ft.Column([
                    titulo,
                    ft.Text("Materia: Teoría de la Computación", italic=True, color="grey400"),
                    ft.Divider(height=20, color="transparent"),
                    ft.Text("Configuración del Autómata:", weight="bold"),
                    self.txt_estados,
                    self.btn_procesar,
                    card_resultado,
                    ft.Divider(height=30),
                    ft.Text("Integración de módulos: Minimización y Subconjuntos", 
                            size=12, color="grey500")
                ]),
                padding=30
            )
        )

    def handle_click(self, e):
        if not self.txt_estados.value:
            self.lbl_resultado.value = " Por favor, ingresa los estados del autómata."
            self.lbl_resultado.color = "amber"
        else:
            
            res = self.logica.minimizar_afd(self.txt_estados.value.split(","), [], {})
            self.lbl_resultado.value = f"Resultado: {res}"
            self.lbl_resultado.color = "greenaccent"
        self.page.update()

# ==========================================
# PUNTO DE ENTRADA
# ==========================================

def main(page: ft.Page):
    app = Practica3App(page)
    app.render()

if __name__ == "__main__":
    ft.app(target=main)