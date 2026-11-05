"""Leituras: consulta + simulador de sensor. Não herda de TelaCrud porque telemetria é
imutável (regra 8): aqui só existe cadastro (POST) e consulta (GET)."""
import tkinter as tk
from tkinter import messagebox, ttk

from api_client import ApiError


class TelaLeituras(ttk.Frame):
    def __init__(self, master, api):
        super().__init__(master, padding=8)
        self.api = api
        self._sensores = {}      # rótulo -> id
        self._montar_filtro()
        self._montar_tabela()
        self._montar_simulador()

    def _montar_filtro(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x")
        ttk.Label(barra, text="Sensor:").pack(side="left")
        self.filtro = ttk.Combobox(barra, state="readonly", width=40)
        self.filtro.pack(side="left", padx=4)
        ttk.Button(barra, text="Atualizar", command=self.atualizar).pack(side="left", padx=4)
        ttk.Button(barra, text="Tentar editar selecionada", command=self.tentar_editar).pack(side="left", padx=12)
        ttk.Button(barra, text="Tentar excluir selecionada", command=self.tentar_excluir).pack(side="left")

    def _montar_tabela(self):
        colunas = [("id", "ID", 60), ("sensor_id", "Sensor", 70), ("valor", "Valor", 90),
                   ("flag", "Flag", 150), ("agregada", "Média 5 min", 90), ("registrada_em", "Registrada em", 180)]
        quadro = ttk.Frame(self)
        quadro.pack(fill="both", expand=True, pady=6)
        self.tree = ttk.Treeview(quadro, columns=[c[0] for c in colunas], show="headings", height=9)
        for chave, titulo, largura in colunas:
            self.tree.heading(chave, text=titulo)
            self.tree.column(chave, width=largura)
        barra = ttk.Scrollbar(quadro, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=barra.set)
        self.tree.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def _montar_simulador(self):
        moldura = ttk.LabelFrame(self, text="Simulador de sensor (envia leituras para POST /leituras)", padding=8)
        moldura.pack(fill="x")
        ttk.Label(moldura, text="Sensor *").grid(row=0, column=0, sticky="e")
        self.sim_sensor = ttk.Combobox(moldura, state="readonly", width=40)
        self.sim_sensor.grid(row=0, column=1, padx=4, pady=3)
        ttk.Label(moldura, text="Valor *").grid(row=0, column=2, sticky="e")
        self.sim_valor = tk.StringVar()
        ttk.Entry(moldura, textvariable=self.sim_valor, width=10).grid(row=0, column=3, padx=4)
        ttk.Label(moldura, text="Repetições").grid(row=0, column=4, sticky="e")
        self.sim_repeticoes = tk.StringVar(value="1")
        ttk.Spinbox(moldura, from_=1, to=20, textvariable=self.sim_repeticoes, width=5).grid(row=0, column=5, padx=4)
        ttk.Button(moldura, text="Enviar leitura", command=self.enviar).grid(row=0, column=6, padx=8)

        self.saida = tk.Text(self, height=9, state="disabled", wrap="word")
        self.saida.pack(fill="both", expand=False, pady=6)

    # --------------------------------------------------------------- ações
    def atualizar(self):
        try:
            sensores = self.api.get("/sensores")
            self._sensores = {f"{s['id']} - {s['nome']} ({s['tipo']}, {s['zona']})": s["id"] for s in sensores}
            rotulos = list(self._sensores)
            self.filtro["values"] = ["Todos"] + rotulos
            self.sim_sensor["values"] = rotulos
            if not self.filtro.get():
                self.filtro.set("Todos")
            parametros = {"limite": 200}
            if self.filtro.get() in self._sensores:
                parametros["sensor_id"] = self._sensores[self.filtro.get()]
            leituras = self.api.get("/leituras", params=parametros)
        except ApiError as erro:
            messagebox.showerror("Erro ao carregar leituras", str(erro))
            return
        self.tree.delete(*self.tree.get_children())
        for l in leituras:
            self.tree.insert("", "end", iid=str(l["id"]), values=(
                l["id"], l["sensor_id"], l["valor"], l["flag"],
                "Sim" if l["agregada"] else "Não", l["registrada_em"][:19].replace("T", " ")))

    def enviar(self):
        rotulo = self.sim_sensor.get()
        if rotulo not in self._sensores:
            messagebox.showwarning("Dados inválidos", "O campo 'Sensor' é obrigatório.")
            return
        try:
            valor = float(self.sim_valor.get().replace(",", "."))
            repeticoes = int(self.sim_repeticoes.get())
        except ValueError:
            messagebox.showwarning("Dados inválidos", "Informe um valor numérico e um número de repetições válido.")
            return
        for i in range(repeticoes):
            try:
                r = self.api.post("/leituras", json={"sensor_id": self._sensores[rotulo], "valor": valor})
            except ApiError as erro:
                self._escrever(f"[{i + 1}] valor {valor} REJEITADO: {erro}")
                messagebox.showerror("Leitura rejeitada pela API", str(erro))
                break
            linhas = [f"[{i + 1}] valor {valor} -> flag={r['flag']} | status do sensor={r['status_sensor']} | {r['mensagem']}"]
            linhas += [f"      * {e}" for e in r["eventos"]]
            self._escrever("\n".join(linhas))
        self.atualizar()

    def tentar_editar(self):
        self._tentar("PUT")

    def tentar_excluir(self):
        self._tentar("DELETE")

    def _tentar(self, metodo):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Seleção necessária", "Selecione uma leitura na tabela primeiro.")
            return
        caminho = f"/leituras/{selecao[0]}"
        try:
            if metodo == "PUT":
                self.api.put(caminho, json={})
            else:
                self.api.delete(caminho)
            messagebox.showinfo("Resultado", "Operação executada.")   # nunca deve acontecer
        except ApiError as erro:
            messagebox.showerror("Operação proibida", str(erro))

    def _escrever(self, texto):
        self.saida.configure(state="normal")
        self.saida.insert("end", texto + "\n")
        self.saida.see("end")
        self.saida.configure(state="disabled")
