import tkinter as tk
from tkinter import ttk, messagebox
from api_client import ApiCliente

class LeituraView:
    def __init__(self, parent):
        self.parent = parent
        self.criar_componentes()
        self.carregar_dados()

    def criar_componentes(self):
        # Título
        lbl_titulo = tk.Label(self.parent, text="Histórico de Leituras de Sensores", font=("Arial", 14, "bold"))
        lbl_titulo.pack(pady=10)

        # Frame de Formulário (Registar Leitura)
        frame_form = tk.LabelFrame(self.parent, text="Registar Nova Leitura (Gera Anomalia se > 90.0)", padx=10, pady=10)
        frame_form.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_form, text="ID do Sensor:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_sensor_id = tk.Entry(frame_form, width=18)
        self.entry_sensor_id.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_form, text="Valor da Medição:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_valor = tk.Entry(frame_form, width=18)
        self.entry_valor.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(frame_form, text="Nível de Bateria (%):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_bateria = tk.Entry(frame_form, width=18)
        self.entry_bateria.grid(row=1, column=1, padx=5, pady=2)

        # Botões de Ação
        frame_botoes = tk.Frame(self.parent)
        frame_botoes.pack(pady=5)

        btn_salvar = tk.Button(frame_botoes, text="Registar Leitura", bg="green", fg="white", command=self.salvar)
        btn_salvar.pack(side="left", padx=5)

        btn_excluir = tk.Button(frame_botoes, text="Excluir Selecionada", bg="red", fg="white", command=self.excluir)
        btn_excluir.pack(side="left", padx=5)

        btn_atualizar_lista = tk.Button(frame_botoes, text="Atualizar Lista", command=self.carregar_dados)
        btn_atualizar_lista.pack(side="left", padx=5)

        # Tabela (Treeview)
        self.tree = ttk.Treeview(self.parent, columns=("ID", "Sensor ID", "Valor", "Bateria", "Data/Hora"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Sensor ID", text="ID Sensor")
        self.tree.heading("Valor", text="Valor")
        self.tree.heading("Bateria", text="Bateria (%)")
        self.tree.heading("Data/Hora", text="Data e Hora")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.selecionar_linha)

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        resultado = ApiCliente.get("leituras")
        if resultado and resultado != "CONNECTION_ERROR":
            for leit in resultado:
                self.tree.insert("", "end", values=(
                    leit.get("id"),
                    leit.get("sensor_id"),
                    leit.get("valor"),
                    leit.get("nivel_bateria"),
                    leit.get("data_hora")
                ))

    def salvar(self):
        try:
            dados = {
                "sensor_id": int(self.entry_sensor_id.get()),
                "valor": float(self.entry_valor.get()),
                "nivel_bateria": int(self.entry_bateria.get())
            }
            resp = ApiCliente.post("leituras", dados)
            if resp and resp.status_code == 201:
                messagebox.showinfo("Sucesso", "Leitura registada com sucesso! (Verifique as anomalias se o valor for superior a 90.0)")
                self.limpar_campos()
                self.carregar_dados()
            else:
                erro = resp.json().get("erro", "Erro desconhecido") if resp else "Erro de comunicação"
                messagebox.showerror("Erro", f"Não foi possível registar leitura: {erro}")
        except ValueError:
            messagebox.showwarning("Aviso", "O ID do sensor e a bateria devem ser inteiros, e o valor deve ser numérico.")

    def selecionar_linha(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado)
            valores = item['values']
            self.id_selecionado = valores[0]

    def excluir(self):
        if not hasattr(self, 'id_selecionado'):
            messagebox.showwarning("Aviso", "Selecione uma leitura na tabela para excluir.")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta leitura?"):
            resp = ApiCliente.delete(f"leituras/{self.id_selecionado}")
            if resp and resp.status_code == 200:
                messagebox.showinfo("Sucesso", "Leitura excluída com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", "Não foi possível excluir a leitura.")

    def limpar_campos(self):
        self.entry_sensor_id.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)
        self.entry_bateria.delete(0, tk.END)
        if hasattr(self, 'id_selecionado'):
            del self.id_selecionado