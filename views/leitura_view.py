import tkinter as tk

from helpers import (ValidacaoError, obrigatorio, inteiro, decimal,
                     data_hora_opcional, montar_filtro_periodo)
from views.base_view import BaseCrudView


class LeituraView(BaseCrudView):
    TITULO = "Histórico de Leituras de Sensores"
    TITULO_FORM = "Registar / Editar Leitura (valor > 90 gera anomalia; bateria < 15% também)"
    ENDPOINT = "leituras"
    COLUNAS = [("id", "ID", 50), ("sensor_id", "ID Sensor", 80), ("valor", "Valor", 100),
               ("nivel_bateria", "Bateria (%)", 90), ("data_hora", "Data e Hora", 160)]

    # ------------------------------------------------------------ filtros (GET /leituras?...)
    def criar_filtros(self):
        frame = tk.LabelFrame(self.parent, text="Filtros (deixe em branco para listar tudo)",
                              padx=10, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="ID Sensor:").grid(row=0, column=0, padx=5)
        self.filtro_sensor = tk.Entry(frame, width=8)
        self.filtro_sensor.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Início (AAAA-MM-DD):").grid(row=0, column=2, padx=5)
        self.filtro_inicio = tk.Entry(frame, width=20)
        self.filtro_inicio.grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Fim (AAAA-MM-DD):").grid(row=0, column=4, padx=5)
        self.filtro_fim = tk.Entry(frame, width=20)
        self.filtro_fim.grid(row=0, column=5, padx=5)

        tk.Button(frame, text="Filtrar", command=lambda: self.carregar_dados(mostrar_popup=True)
                  ).grid(row=0, column=6, padx=5)
        tk.Button(frame, text="Limpar filtros", command=self.limpar_filtros).grid(row=0, column=7, padx=5)

    def parametros_consulta(self):
        params = montar_filtro_periodo(self.filtro_inicio.get(), self.filtro_fim.get())
        if self.filtro_sensor.get().strip():
            params["sensor_id"] = inteiro(self.filtro_sensor.get(), "ID Sensor (filtro)")
        return params or None

    def limpar_filtros(self):
        for entry in (self.filtro_sensor, self.filtro_inicio, self.filtro_fim):
            entry.delete(0, tk.END)
        self.carregar_dados()

    # ------------------------------------------------------------ formulário
    def criar_formulario(self, frame):
        tk.Label(frame, text="ID do Sensor:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_sensor_id = tk.Entry(frame, width=22)
        self.entry_sensor_id.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame, text="Valor da Medição:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_valor = tk.Entry(frame, width=22)
        self.entry_valor.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(frame, text="Bateria (0 a 100 %):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_bateria = tk.Entry(frame, width=22)
        self.entry_bateria.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame, text="Data/Hora (opcional):").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_data_hora = tk.Entry(frame, width=22)
        self.entry_data_hora.grid(row=1, column=3, padx=5, pady=2)
        tk.Label(frame, text="Formato: AAAA-MM-DD HH:MM:SS",
                 fg="gray40").grid(row=2, column=2, columnspan=2, sticky="w", padx=5)

    def coletar_dados(self, editando=False):
        dados = {
            "sensor_id": inteiro(self.entry_sensor_id.get(), "ID do Sensor"),
            "valor": decimal(self.entry_valor.get(), "Valor da Medição"),
            "nivel_bateria": inteiro(self.entry_bateria.get(), "Bateria"),
        }
        data_hora = data_hora_opcional(self.entry_data_hora.get(), "Data/Hora")
        if data_hora:
            dados["data_hora"] = data_hora
        elif editando:
            # Na edição, a data/hora vazia faria a API regravar "agora" e perder a data original.
            raise ValidacaoError("Para editar, a Data/Hora precisa estar preenchida "
                                 "(selecione a leitura na tabela para trazer a data original).")
        return dados

    def preencher_formulario(self, registro):
        self.definir_texto(self.entry_sensor_id, registro.get("sensor_id"))
        self.definir_texto(self.entry_valor, registro.get("valor"))
        self.definir_texto(self.entry_bateria, registro.get("nivel_bateria"))
        self.definir_texto(self.entry_data_hora, registro.get("data_hora"))

    def limpar_formulario(self):
        for entry in (self.entry_sensor_id, self.entry_valor, self.entry_bateria, self.entry_data_hora):
            entry.delete(0, tk.END)
