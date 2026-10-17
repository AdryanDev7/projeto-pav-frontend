import tkinter as tk
from tkinter import ttk
from views.localizacao_view import LocalizacaoView
from views.sensor_view import SensorView
from views.leitura_view import LeituraView
from views.anomalia_view import AnomaliaView

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Controlo - Sistema IoT (Frontend PAV)")
        self.root.geometry("900x600")

        # Criar o sistema de abas (Notebook)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Instanciar as abas correspondentes a cada domínio
        self.tab_localizacao = ttk.Frame(self.notebook)
        self.tab_sensor = ttk.Frame(self.notebook)
        self.tab_leitura = ttk.Frame(self.notebook)
        self.tab_anomalia = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_localizacao, text="Localizações")
        self.notebook.add(self.tab_sensor, text="Sensores")
        self.notebook.add(self.tab_leitura, text="Leituras")
        self.notebook.add(self.tab_anomalia, text="Anomalias")

        # Inicializar os conteúdos de cada aba
        LocalizacaoView(self.tab_localizacao)
        SensorView(self.tab_sensor)
        LeituraView(self.tab_leitura)
        AnomaliaView(self.tab_anomalia)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()