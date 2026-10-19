import tkinter as tk
from tkinter import ttk

from helpers import obrigatorio, inteiro
from views.base_view import BaseCrudView

SEVERIDADES = ("Baixa", "Média", "Alta", "Crítica")


class AnomaliaView(BaseCrudView):
    TITULO = "Registo de Anomalias e Alertas"
    TITULO_FORM = "Registar / Atualizar Anomalia (manual)"
    ENDPOINT = "anomalias"
    COLUNAS = [("id", "ID", 50), ("leitura_id", "ID Leitura", 80),
               ("descricao_alerta", "Descrição do Alerta", 450), ("severidade", "Severidade", 100)]

    def criar_formulario(self, frame):
        tk.Label(frame, text="ID da Leitura:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_leitura_id = tk.Entry(frame, width=22)
        self.entry_leitura_id.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame, text="Severidade:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.combo_severidade = ttk.Combobox(frame, values=SEVERIDADES, state="readonly", width=19)
        self.combo_severidade.set(SEVERIDADES[0])
        self.combo_severidade.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_descricao = tk.Entry(frame, width=70)
        self.entry_descricao.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=2)

    def coletar_dados(self, editando=False):
        return {
            "leitura_id": inteiro(self.entry_leitura_id.get(), "ID da Leitura"),
            "descricao_alerta": obrigatorio(self.entry_descricao.get(), "Descrição"),
            "severidade": obrigatorio(self.combo_severidade.get(), "Severidade"),
        }

    def preencher_formulario(self, registro):
        self.definir_texto(self.entry_leitura_id, registro.get("leitura_id"))
        self.definir_texto(self.entry_descricao, registro.get("descricao_alerta"))
        self.combo_severidade.set(registro.get("severidade") or SEVERIDADES[0])

    def limpar_formulario(self):
        self.entry_leitura_id.delete(0, tk.END)
        self.entry_descricao.delete(0, tk.END)
        self.combo_severidade.set(SEVERIDADES[0])
