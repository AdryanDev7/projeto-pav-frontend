"""Interface gráfica (Tkinter). Roda FORA do Docker:  python main.py
Para apontar para outra API:  API_URL=http://IP:8000 python main.py"""
import tkinter as tk
from tkinter import ttk

from api_client import ApiClient
from tela_alertas import TelaAlertas
from tela_analise import TelaAnalise
from tela_leituras import TelaLeituras
from tela_login import TelaLogin
from tela_manutencoes import TelaManutencoes
from tela_operadores import TelaOperadores
from tela_sensores import TelaSensores


class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IoT Monitor - Análise de Sensores")
        self.geometry("1250x760")
        self.api = ApiClient()
        self._quadro = None
        self._mostrar_login()

    def _trocar_quadro(self, novo):
        if self._quadro is not None:
            self._quadro.destroy()
        self._quadro = novo
        self._quadro.pack(fill="both", expand=True)

    def _mostrar_login(self):
        self.api.operador = None
        self._trocar_quadro(TelaLogin(self, self.api, self._entrar))

    def _entrar(self, operador):
        self.api.operador = operador
        quadro = ttk.Frame(self)
        topo = ttk.Frame(quadro, padding=6)
        topo.pack(fill="x")
        ttk.Label(topo, text=f"Operador: {operador['nome']}  |  Perfil: {operador['perfil']}  |  "
                             f"Zona: {operador['zona']}", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(topo, text="Trocar operador", command=self._mostrar_login).pack(side="right")

        self.abas = ttk.Notebook(quadro)
        self.abas.pack(fill="both", expand=True, padx=6, pady=6)
        telas = [("Sensores", TelaSensores), ("Leituras", TelaLeituras), ("Análise", TelaAnalise),
                 ("Manutenções", TelaManutencoes), ("Alertas", TelaAlertas), ("Operadores", TelaOperadores)]
        for nome, classe in telas:
            self.abas.add(classe(self.abas, self.api), text=nome)
        self._trocar_quadro(quadro)
        self.abas.bind("<<NotebookTabChanged>>", self._ao_trocar_aba)
        self.after(100, self._ao_trocar_aba)      # carrega a primeira aba

    def _ao_trocar_aba(self, _evento=None):
        aba = self.abas.nametowidget(self.abas.select())
        if hasattr(aba, "atualizar"):
            aba.atualizar()


if __name__ == "__main__":
    Aplicacao().mainloop()
