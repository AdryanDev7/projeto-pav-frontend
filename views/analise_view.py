"""Aba "Análise / Estatísticas": consome GET /api/sensores/<id>/estatisticas."""
import tkinter as tk
from tkinter import ttk, messagebox

from helpers import ValidacaoError, montar_filtro_periodo, carregar_lista, carregar_objeto

SEM_DADO = "—"


class AnaliseView:
    # (chave no JSON, rótulo exibido)
    INDICADORES = [("total_leituras", "Total de leituras"), ("media", "Média"),
                   ("minimo", "Mínimo"), ("maximo", "Máximo"),
                   ("desvio_padrao", "Desvio padrão"), ("total_anomalias", "Total de anomalias")]

    def __init__(self, parent):
        self.parent = parent
        self.sensores = {}          # {texto do combobox: id do sensor}
        self.valores = {}           # {chave: Label com o valor}
        self.criar_componentes()
        self.carregar_sensores()

    def criar_componentes(self):
        tk.Label(self.parent, text="Análise Estatística de Sensores",
                 font=("Arial", 14, "bold")).pack(pady=10)

        # ---- filtros
        frame = tk.LabelFrame(self.parent, text="Sensor e período", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Sensor:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.combo_sensor = ttk.Combobox(frame, state="readonly", width=40)
        self.combo_sensor.grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=2)

        tk.Label(frame, text="Início (AAAA-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_inicio = tk.Entry(frame, width=22)
        self.entry_inicio.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame, text="Fim (AAAA-MM-DD):").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_fim = tk.Entry(frame, width=22)
        self.entry_fim.grid(row=1, column=3, padx=5, pady=2)

        botoes = tk.Frame(self.parent)
        botoes.pack(pady=5)
        tk.Button(botoes, text="Calcular Estatísticas", bg="green", fg="white",
                  command=self.calcular).pack(side="left", padx=5)
        tk.Button(botoes, text="Limpar Período", command=self.limpar_periodo).pack(side="left", padx=5)
        tk.Button(botoes, text="Recarregar Sensores",
                  command=lambda: self.carregar_sensores(mostrar_popup=True)).pack(side="left", padx=5)

        self.lbl_status = tk.Label(self.parent, text="", anchor="w")
        self.lbl_status.pack(fill="x", padx=10)

        # ---- resultados (um "cartão" por indicador)
        frame_res = tk.LabelFrame(self.parent, text="Resultado", padx=10, pady=10)
        frame_res.pack(fill="x", padx=10, pady=10)
        for indice, (chave, rotulo) in enumerate(self.INDICADORES):
            cartao = tk.Frame(frame_res, relief="groove", borderwidth=2, padx=15, pady=10)
            cartao.grid(row=indice // 3, column=indice % 3, padx=8, pady=8, sticky="nsew")
            frame_res.columnconfigure(indice % 3, weight=1)
            tk.Label(cartao, text=rotulo, font=("Arial", 10)).pack()
            lbl = tk.Label(cartao, text=SEM_DADO, font=("Arial", 18, "bold"))
            lbl.pack()
            self.valores[chave] = lbl

    # ------------------------------------------------------------------ sensores
    def ao_exibir(self):
        """Chamado pelo main sempre que a aba é aberta (mantém a lista de sensores atualizada)."""
        self.carregar_sensores()

    def carregar_sensores(self, mostrar_popup=False):
        lista, erro = carregar_lista("sensores")
        if erro:
            self.sensores = {}
            self.combo_sensor["values"] = ()
            self.combo_sensor.set("")
            self._status(erro.replace("\n", " "), erro=True)
            if mostrar_popup:
                messagebox.showerror("Erro ao carregar sensores", erro)
            return
        atual = self.combo_sensor.get()
        self.sensores = {f"{s['id']} - {s['codigo_serial']} ({s['tipo']})": s["id"] for s in lista}
        self.combo_sensor["values"] = list(self.sensores)
        if atual in self.sensores:
            self.combo_sensor.set(atual)
        else:
            self.combo_sensor.set("")
        self._status(f"{len(lista)} sensor(es) disponível(is)." if lista
                     else "Nenhum sensor cadastrado. Cadastre um sensor primeiro.")

    # ------------------------------------------------------------------ estatísticas
    def calcular(self):
        if not self.combo_sensor.get():
            messagebox.showwarning("Verifique os dados", "Selecione um sensor para analisar.")
            return
        try:
            params = montar_filtro_periodo(self.entry_inicio.get(), self.entry_fim.get())
        except ValidacaoError as erro:
            messagebox.showwarning("Verifique os dados", str(erro))
            return

        sensor_id = self.sensores[self.combo_sensor.get()]
        dados, erro = carregar_objeto(f"sensores/{sensor_id}/estatisticas", params or None)
        if erro:
            self._limpar_resultado()
            self._status(erro.replace("\n", " "), erro=True)
            messagebox.showerror("Não foi possível calcular", erro)
            return

        for chave, _ in self.INDICADORES:
            self.valores[chave].config(text=self._formatar(dados.get(chave)))
        if dados.get("total_leituras") == 0:
            self._status("Nenhuma leitura encontrada para este sensor no período informado.")
        else:
            self._status(f"Estatísticas do sensor {dados.get('codigo_serial', sensor_id)} calculadas.")

    @staticmethod
    def _formatar(valor):
        if valor is None:
            return SEM_DADO                 # sensor sem leituras no período
        if isinstance(valor, float):
            return f"{valor:.2f}"
        return str(valor)

    def _limpar_resultado(self):
        for lbl in self.valores.values():
            lbl.config(text=SEM_DADO)

    def limpar_periodo(self):
        self.entry_inicio.delete(0, tk.END)
        self.entry_fim.delete(0, tk.END)

    def _status(self, texto, erro=False):
        self.lbl_status.config(text=texto, fg="red" if erro else "gray25")
