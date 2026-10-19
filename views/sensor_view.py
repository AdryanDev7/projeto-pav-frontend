import tkinter as tk
from tkinter import ttk

from helpers import obrigatorio, inteiro
from views.base_view import BaseCrudView

# Mesmos valores aceitos pela regra de negócio RN05 do backend
STATUS_VALIDOS = ("Ativo", "Inativo", "Em Manutenção")


class SensorView(BaseCrudView):
    TITULO = "Gestão de Sensores IoT"
    TITULO_FORM = "Cadastrar / Atualizar Sensor"
    ENDPOINT = "sensores"
    COLUNAS = [("id", "ID", 50), ("codigo_serial", "Código Serial", 140), ("tipo", "Tipo", 120),
               ("status", "Status", 110), ("localizacao_id", "ID Localização", 100),
               ("nivel_bateria", "Bateria (%)", 90)]

    def criar_formulario(self, frame):
        tk.Label(frame, text="Código Serial:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_serial = tk.Entry(frame, width=22)
        self.entry_serial.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame, text="Tipo:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_tipo = tk.Entry(frame, width=22)
        self.entry_tipo.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(frame, text="Status:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        # readonly: o usuário só consegue escolher um dos status válidos
        self.combo_status = ttk.Combobox(frame, values=STATUS_VALIDOS, state="readonly", width=19)
        self.combo_status.set(STATUS_VALIDOS[0])
        self.combo_status.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame, text="ID Localização:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_loc_id = tk.Entry(frame, width=22)
        self.entry_loc_id.grid(row=1, column=3, padx=5, pady=2)

        tk.Label(frame, text="Bateria (0 a 100 %):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_bateria = tk.Entry(frame, width=22)
        self.entry_bateria.grid(row=2, column=1, padx=5, pady=2)

    def coletar_dados(self, editando=False):
        return {
            "codigo_serial": obrigatorio(self.entry_serial.get(), "Código Serial"),
            "tipo": obrigatorio(self.entry_tipo.get(), "Tipo"),
            "status": obrigatorio(self.combo_status.get(), "Status"),
            "localizacao_id": inteiro(self.entry_loc_id.get(), "ID Localização"),
            "nivel_bateria": inteiro(self.entry_bateria.get(), "Bateria"),
        }

    def preencher_formulario(self, registro):
        self.definir_texto(self.entry_serial, registro.get("codigo_serial"))
        self.definir_texto(self.entry_tipo, registro.get("tipo"))
        self.combo_status.set(registro.get("status") or STATUS_VALIDOS[0])
        self.definir_texto(self.entry_loc_id, registro.get("localizacao_id"))
        self.definir_texto(self.entry_bateria, registro.get("nivel_bateria"))

    def limpar_formulario(self):
        for entry in (self.entry_serial, self.entry_tipo, self.entry_loc_id, self.entry_bateria):
            entry.delete(0, tk.END)
        self.combo_status.set(STATUS_VALIDOS[0])
