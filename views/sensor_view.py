import tkinter as tk
from tkinter import ttk, messagebox
from api_client import ApiCliente

class SensorView:
    def __init__(self, parent):
        self.parent = parent
        self.criar_componentes()
        self.carregar_dados()

    def criar_componentes(self):
        # Título
        lbl_titulo = tk.Label(self.parent, text="Gestão de Sensores IoT", font=("Arial", 14, "bold"))
        lbl_titulo.pack(pady=10)

        # Frame de Formulário
        frame_form = tk.LabelFrame(self.parent, text="Cadastrar / Atualizar Sensor", padx=10, pady=10)
        frame_form.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_form, text="Código Serial:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_serial = tk.Entry(frame_form, width=18)
        self.entry_serial.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_form, text="Tipo:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_tipo = tk.Entry(frame_form, width=18)
        self.entry_tipo.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(frame_form, text="Status:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_status = tk.Entry(frame_form, width=18)
        self.entry_status.insert(0, "Ativo")
        self.entry_status.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame_form, text="ID Localização:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_loc_id = tk.Entry(frame_form, width=18)
        self.entry_loc_id.grid(row=1, column=3, padx=5, pady=2)

        tk.Label(frame_form, text="Bateria (%):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_bateria = tk.Entry(frame_form, width=18)
        self.entry_bateria.grid(row=2, column=1, padx=5, pady=2)

        # Botões de Ação CRUD
        frame_botoes = tk.Frame(self.parent)
        frame_botoes.pack(pady=5)

        btn_salvar = tk.Button(frame_botoes, text="Cadastrar Sensor", bg="green", fg="white", command=self.salvar)
        btn_salvar.pack(side="left", padx=5)

        btn_atualizar = tk.Button(frame_botoes, text="Atualizar Selecionado", bg="orange", fg="white", command=self.atualizar)
        btn_atualizar.pack(side="left", padx=5)

        btn_excluir = tk.Button(frame_botoes, text="Excluir Selecionado", bg="red", fg="white", command=self.excluir)
        btn_excluir.pack(side="left", padx=5)

        btn_atualizar_lista = tk.Button(frame_botoes, text="Atualizar Lista", command=self.carregar_dados)
        btn_atualizar_lista.pack(side="left", padx=5)

        # Tabela (Treeview)
        self.tree = ttk.Treeview(self.parent, columns=("ID", "Serial", "Tipo", "Status", "Loc ID", "Bateria"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Serial", text="Código Serial")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Loc ID", text="ID Localização")
        self.tree.heading("Bateria", text="Bateria (%)")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.preencher_campos)

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        resultado = ApiCliente.get("sensores")
        if resultado and resultado != "CONNECTION_ERROR":
            for sens in resultado:
                self.tree.insert("", "end", values=(
                    sens.get("id"), 
                    sens.get("codigo_serial"), 
                    sens.get("tipo"), 
                    sens.get("status"), 
                    sens.get("localizacao_id"), 
                    sens.get("nivel_bateria")
                ))

    def salvar(self):
        try:
            dados = {
                "codigo_serial": self.entry_serial.get(),
                "tipo": self.entry_tipo.get(),
                "status": self.entry_status.get(),
                "localizacao_id": int(self.entry_loc_id.get()),
                "nivel_bateria": int(self.entry_bateria.get())
            }
            resp = ApiCliente.post("sensores", dados)
            if resp and resp.status_code == 201:
                messagebox.showinfo("Sucesso", "Sensor cadastrado com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            else:
                erro = resp.json().get("erro", "Erro desconhecido") if resp else "Erro de comunicação"
                messagebox.showerror("Erro", f"Não foi possível cadastrar: {erro}")
        except ValueError:
            messagebox.showwarning("Aviso", "ID da Localização e Nível de Bateria devem ser números inteiros válidos.")

    def atualizar(self):
        if not hasattr(self, 'id_selecionado'):
            messagebox.showwarning("Aviso", "Selecione um sensor na tabela para atualizar.")
            return
        try:
            dados = {
                "codigo_serial": self.entry_serial.get(),
                "tipo": self.entry_tipo.get(),
                "status": self.entry_status.get(),
                "localizacao_id": int(self.entry_loc_id.get()),
                "nivel_bateria": int(self.entry_bateria.get())
            }
            resp = ApiCliente.put(f"sensores/{self.id_selecionado}", dados)
            if resp and resp.status_code == 200:
                messagebox.showinfo("Sucesso", "Sensor atualizado com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            else:
                erro = resp.json().get("erro", "Erro desconhecido") if resp else "Erro de comunicação"
                messagebox.showerror("Erro", f"Não foi possível atualizar: {erro}")
        except ValueError:
            messagebox.showwarning("Aviso", "ID da Localização e Nível de Bateria devem ser números inteiros válidos.")

    def preencher_campos(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado)
            valores = item['values']
            self.id_selecionado = valores[0]
            
            self.entry_serial.delete(0, tk.END)
            self.entry_serial.insert(0, valores[1])
            
            self.entry_tipo.delete(0, tk.END)
            self.entry_tipo.insert(0, valores[2])
            
            self.entry_status.delete(0, tk.END)
            self.entry_status.insert(0, valores[3])
            
            self.entry_loc_id.delete(0, tk.END)
            self.entry_loc_id.insert(0, valores[4])
            
            self.entry_bateria.delete(0, tk.END)
            self.entry_bateria.insert(0, valores[5])

    def excluir(self):
        if not hasattr(self, 'id_selecionado'):
            messagebox.showwarning("Aviso", "Selecione um sensor na tabela para excluir.")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este sensor?"):
            resp = ApiCliente.delete(f"sensores/{self.id_selecionado}")
            if resp and resp.status_code == 200:
                messagebox.showinfo("Sucesso", "Sensor excluído com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", "Não foi possível excluir o sensor.")

    def limpar_campos(self):
        self.entry_serial.delete(0, tk.END)
        self.entry_tipo.delete(0, tk.END)
        self.entry_status.delete(0, tk.END)
        self.entry_loc_id.delete(0, tk.END)
        self.entry_bateria.delete(0, tk.END)
        if hasattr(self, 'id_selecionado'):
            del self.id_selecionado