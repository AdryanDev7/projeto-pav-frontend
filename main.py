import tkinter as tk
from tkinter import ttk

from views.localizacao_view import LocalizacaoView
from views.sensor_view import SensorView
from views.leitura_view import LeituraView
from views.anomalia_view import AnomaliaView
from views.analise_view import AnaliseView


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Controlo - Sistema IoT (Frontend PAV)")
        self.root.geometry("1000x700")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # (título da aba, classe da view). Cada view recebe o Frame da sua aba.
        abas = [("Localizações", LocalizacaoView), ("Sensores", SensorView),
                ("Leituras", LeituraView), ("Anomalias", AnomaliaView),
                ("Análise / Estatísticas", AnaliseView)]

        self.views = {}   # {nome do widget da aba: instância da view}
        for titulo, classe_view in abas:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=titulo)
            self.views[str(frame)] = classe_view(frame)

        # Ao trocar de aba, as views que precisarem (ex.: Análise) atualizam seus dados
        self.notebook.bind("<<NotebookTabChanged>>", self.ao_trocar_aba)

    def ao_trocar_aba(self, _evento=None):
        view = self.views.get(self.notebook.select())
        if view is not None and hasattr(view, "ao_exibir"):
            view.ao_exibir()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
