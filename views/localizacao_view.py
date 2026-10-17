import tkinter as tk
from tkinter import ttk, messagebox
from api_client import ApiCliente

class LocalizacaoView:
    def __init__(self, parent):
        self.parent = parent
        self.criar_componentes()
        self.carregar_dados()

    def criar_componentes(self):
        # Título
        lbl_titulo = tk.Label(self.parent, text="Gestão de Localizações", font=("Arial", 14, "bold"))
        lbl_titulo.pack(pady=10)

        # Frame de Formulário (Entrada de Dados)
        frame_form = tk.LabelFrame(self.parent, text="Registar / Atualizar Localização", padx=10, pady=10)
        frame_form.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_form, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_nome = tk.Entry(frame_form, width=20)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_form, text="Setor:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_setor = tk.Entry(frame_form, width=20)
        self.entry_setor.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(frame_form, text="Latitude:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_lat = tk.Entry(frame_form, width=20)
        self.entry_lat.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame_form, text="Longitude:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_lon = tk.Entry(frame_form, width=20)
        self.entry_lon.grid(row=1, column=3, padx=5, pady=2)

        # Botões de Ação CRUD
        frame_botoes = tk.Frame(self.parent)
        frame_botoes.pack(pady=5)

        btn_salvar = tk.Button(frame_botoes, text="Salvar Novo", bg="green", fg="white", command=self.salvar)
        btn_salvar.pack(side="left", padx=5)

        btn_editar = tk.Button(frame_botoes, text="Atualizar Selecionado", bg="orange", fg="white", command=self.atualizar)
        btn_editar.pack(side="left", padx=5)

        btn_excluir = tk.Button(frame_botoes, text="Excluir Selecionado", bg="red", fg="white", command=self.excluir)
        btn_excluir.pack(side="left", padx=5)

        btn_atualizar_lista = tk.Button(frame_botoes, text="Atualizar Lista", command=self.carregar_dados)
        btn_atualizar_lista.pack(side="left", padx=5)

        # Tabela (Treeview)
        self.tree = ttk.Treeview(self.parent, columns=("ID", "Nome", "Setor", "Latitude", "Longitude"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Setor", text="Setor")
        self.tree.heading("Latitude", text="Latitude")
        self.tree.heading("Longitude", text="Longitude")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Evento de clique na tabela para preencher os campos
        self.tree.bind("<<TreeviewSelect>>", self.preencher_campos)

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        resultado = ApiCliente.get("localizacoes")
        if resultado == "CONNECTION_ERROR":
            messagebox.showerror("Erro de Conexão", "Não foi possível ligar à API. Verifique se o servidor Flask está a correr.")
            return
        
        if resultado:
            for loc in resultado:
                self.tree.insert("", "end", values=(loc.get("id"), loc.get("nome"), loc.get("setor"), loc.get("latitude"), loc.get("longitude")))

    def salvar(self):
        try:
            dados = {
                "nome": self.entry_nome.get(),
                "setor": self.entry_setor.get(),
                "latitude": float(self.entry_lat.get()),
                "longitude": float(self.entry_lon.get())
            }
            resp = ApiCliente.post("localizacoes", dados)
            if resp and resp.status_code == 201:
                messagebox.showinfo("Sucesso", "Localização criada com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            else:
                erro = resp.json().get("erro", "Erro desconhecido") if resp else "Erro de comunicação"
                messagebox.showerror("Erro", f"Não foi possível salvar: {erro}")
        except ValueError:
            messagebox.showwarning("Aviso", "Latitude e Longitude devem ser números válidos.")

    def preencher_campos(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado)
            valores = item['values']
            self.id_selecionado = valores[0]
            
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, valores[1])
            
            self.entry_setor.delete(0, tk.END)
            self.entry_setor.insert(0, valores[2])
            
            self.entry_lat.delete(0, tk.END)
            self.entry_lat.insert(0, valores[3])
            
            self.entry_lon.delete(0, tk.END)
            self.entry_lon.insert(0, valores[4])

    def atualizar(self):
        if not hasattr(self, 'id_selecionado'):
            messagebox.showwarning("Aviso", "Selecione uma localização na tabela para atualizar.")
            return
        try:
            dados = {
                "nome": self.entry_nome.get(),
                "setor": self.entry_setor.get(),
                "latitude": float(self.entry_lat.get()),
                "longitude": float(self.entry_lon.get())
            }
            resp = ApiCliente.put(f"localizacoes/{self.id_selecionado}", dados)
            if resp and resp.status_code == 200:
                messagebox.showinfo("Sucesso", "Localização atualizada com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            else:
                erro = resp.json().get("erro", "Erro desconhecido") if resp else "Erro de comunicação"
                messagebox.showerror("Erro", f"Não foi possível atualizar: {erro}")
        except ValueError:
            messagebox.showwarning("Aviso", "Latitude e Longitude devem ser números válidos.")

    def excluir(self):
        if not hasattr(self, 'id_selecionado'):
            messagebox.showwarning("Aviso", "Selecione uma localização na tabela para excluir.")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta localização?"):
            resp = ApiCliente.delete(f"localizacoes/{self.id_selecionado}")
            if resp and resp.status_code == 200:
                messagebox.showinfo("Sucesso", "Localização excluída com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", "Não foi possível excluir a localização.")

    def limpar_campos(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_setor.delete(0, tk.END)
        self.entry_lat.delete(0, tk.END)
        self.entry_lon.delete(0, tk.END)
        if hasattr(self, 'id_selecionado'):
            del self.id_selecionado