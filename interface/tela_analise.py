"""Análise de dados: estatísticas e detecção de anomalias (consome os endpoints de análise)."""
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from api_client import ApiError


class TelaAnalise(ttk.Frame):
    def __init__(self, master, api):
        super().__init__(master, padding=8)
        self.api = api
        self._sensores = {}
        moldura = ttk.LabelFrame(self, text="Parâmetros da análise", padding=8)
        moldura.pack(fill="x")

        ttk.Label(moldura, text="Sensor *").grid(row=0, column=0, sticky="e")
        self.sensor = ttk.Combobox(moldura, state="readonly", width=40)
        self.sensor.grid(row=0, column=1, padx=4, pady=3)
        ttk.Label(moldura, text="Início (AAAA-MM-DD HH:MM:SS)").grid(row=1, column=0, sticky="e")
        self.inicio = tk.StringVar()
        ttk.Entry(moldura, textvariable=self.inicio, width=25).grid(row=1, column=1, sticky="w", padx=4)
        ttk.Label(moldura, text="Fim").grid(row=1, column=2, sticky="e")
        self.fim = tk.StringVar()
        ttk.Entry(moldura, textvariable=self.fim, width=25).grid(row=1, column=3, sticky="w", padx=4)
        ttk.Label(moldura, text="Limiar z-score").grid(row=0, column=2, sticky="e")
        self.limiar = tk.StringVar(value="2.0")
        ttk.Entry(moldura, textvariable=self.limiar, width=8).grid(row=0, column=3, sticky="w", padx=4)

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", pady=6)
        ttk.Button(botoes, text="Calcular estatísticas", command=self.estatisticas).pack(side="left", padx=3)
        ttk.Button(botoes, text="Detectar anomalias", command=self.anomalias).pack(side="left", padx=3)

        self.saida = tk.Text(self, state="disabled", wrap="word")
        self.saida.pack(fill="both", expand=True)

    def atualizar(self):
        try:
            sensores = self.api.get("/sensores")
        except ApiError as erro:
            messagebox.showerror("Erro ao carregar sensores", str(erro))
            return
        self._sensores = {f"{s['id']} - {s['nome']}": s["id"] for s in sensores}
        self.sensor["values"] = list(self._sensores)

    def _sensor_id(self):
        if self.sensor.get() not in self._sensores:
            messagebox.showwarning("Dados inválidos", "O campo 'Sensor' é obrigatório.")
            return None
        return self._sensores[self.sensor.get()]

    @staticmethod
    def _data(texto):
        texto = texto.strip()
        return datetime.fromisoformat(texto).isoformat() if texto else None

    def estatisticas(self):
        sensor_id = self._sensor_id()
        if sensor_id is None:
            return
        try:
            params = {"inicio": self._data(self.inicio.get()), "fim": self._data(self.fim.get())}
            params = {k: v for k, v in params.items() if v}
        except ValueError:
            messagebox.showwarning("Dados inválidos", "Use datas no formato AAAA-MM-DD HH:MM:SS.")
            return
        try:
            r = self.api.get(f"/sensores/{sensor_id}/estatisticas", params=params)
        except ApiError as erro:
            messagebox.showerror("Erro na análise", str(erro))
            return
        u = r["unidade"]
        if r["media"] is None:
            corpo = "Nenhuma leitura válida encontrada no período."
        else:
            corpo = (f"Média: {r['media']} {u}\nMínimo: {r['minimo']} {u}\n"
                     f"Máximo: {r['maximo']} {u}\nDesvio padrão: {r['desvio_padrao']} {u}")
        self._mostrar(f"ESTATÍSTICAS - {r['sensor_nome']} ({r['tipo']})\n"
                      f"Leituras válidas: {r['leituras_validas']}\n"
                      f"Ruído descartado (SUSPEITA_RUIDO): {r['ruido_descartado']}\n\n{corpo}")

    def anomalias(self):
        sensor_id = self._sensor_id()
        if sensor_id is None:
            return
        try:
            limiar = float(self.limiar.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Dados inválidos", "O limiar deve ser um número.")
            return
        try:
            r = self.api.get(f"/sensores/{sensor_id}/anomalias", params={"limiar": limiar})
        except ApiError as erro:
            messagebox.showerror("Erro na análise", str(erro))
            return
        linhas = [f"ANOMALIAS (|z| > {r['limiar']}) - {r['amostras']} amostras",
                  f"Média: {r['media']} | Desvio padrão: {r['desvio_padrao']}", ""]
        if r["amostras"] < 3:
            linhas.append("Amostras insuficientes (mínimo 3).")
        elif not r["anomalias"]:
            linhas.append("Nenhuma anomalia encontrada.")
        for a in r["anomalias"]:
            linhas.append(f"Leitura #{a['leitura_id']}: valor={a['valor']} z={a['z_score']} "
                          f"em {a['registrada_em'][:19].replace('T', ' ')}")
        self._mostrar("\n".join(linhas))

    def _mostrar(self, texto):
        self.saida.configure(state="normal")
        self.saida.delete("1.0", "end")
        self.saida.insert("end", texto)
        self.saida.configure(state="disabled")
