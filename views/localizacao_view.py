import tkinter as tk

from helpers import obrigatorio, decimal
from views.base_view import BaseCrudView


class LocalizacaoView(BaseCrudView):
    TITULO = "Gestão de Localizações"
    TITULO_FORM = "Registar / Atualizar Localização"
    ENDPOINT = "localizacoes"
    COLUNAS = [("id", "ID", 50), ("nome", "Nome", 200), ("setor", "Setor", 150),
               ("latitude", "Latitude", 110), ("longitude", "Longitude", 110)]

    def criar_formulario(self, frame):
        tk.Label(frame, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_nome = tk.Entry(frame, width=22)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame, text="Setor:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_setor = tk.Entry(frame, width=22)
        self.entry_setor.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(frame, text="Latitude (-90 a 90):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_lat = tk.Entry(frame, width=22)
        self.entry_lat.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame, text="Longitude (-180 a 180):").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_lon = tk.Entry(frame, width=22)
        self.entry_lon.grid(row=1, column=3, padx=5, pady=2)

    def coletar_dados(self, editando=False):
        return {
            "nome": obrigatorio(self.entry_nome.get(), "Nome"),
            "setor": obrigatorio(self.entry_setor.get(), "Setor"),
            "latitude": decimal(self.entry_lat.get(), "Latitude"),
            "longitude": decimal(self.entry_lon.get(), "Longitude"),
        }

    def preencher_formulario(self, registro):
        self.definir_texto(self.entry_nome, registro.get("nome"))
        self.definir_texto(self.entry_setor, registro.get("setor"))
        self.definir_texto(self.entry_lat, registro.get("latitude"))
        self.definir_texto(self.entry_lon, registro.get("longitude"))

    def limpar_formulario(self):
        for entry in (self.entry_nome, self.entry_setor, self.entry_lat, self.entry_lon):
            entry.delete(0, tk.END)
