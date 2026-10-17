import tkinter as tk
from tkinter import ttk, messagebox
from api_client import ApiCliente

class AnomaliaView:
    def __init__(self, parent):
        self.parent = parent
        self.criar_componentes()
        self.carregar_dados()

    def criar_componentes(self):
        # Título
        lbl_titulo = tk.Label(self.parent, text="Registo de Anomalias e Alertas Críticos", font=("Arial", 14, "bold"))
        lbl_titulo.pack(pady=10)

        # Botões de Ação
        frame_botoes = tk.Frame(self.parent)
        frame_botoes.pack(pady=5)

        btn_excluir = tk.Button(frame_botoes, text="Excluir Anomalia Selecionada", bg="red", fg="white", command=self.excluir)
        btn_excluir.pack(side="left", padx=5)

        btn_atualizar_lista = tk.Button(frame_botoes, text="Atualizar Lista", command=self.carregar_dados)
        btn_atualizar_lista.pack(side="left", padx=5)

        # Tabela (Treeview)
        self.tree = ttk.Treeview(self.parent, columns=("ID", "Leitura ID", "Descrição", "Severidade"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Leitura ID", text="ID Leitura")
        self.tree.heading("Descrição", text="Descrição do Alerta")
        self.tree.heading("Severidade", text="Severidade")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.selecionar_linha)

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        resultado = ApiCliente.get("anomalias")
        if resultado and resultado != "CONNECTION_ERROR":
            for anom in resultado:
                self.tree.insert("", "end", values=(
                    anom.get("id"),
                    anom.get("leitura_id"),
                    anom.get("descricao_alerta"),
                    anom.get("severidade")
                ))

    def selecionar_linha(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado)
            valores = item['values']
            self.id_selecionado = valores[0]

    def excluir(self):
        if not hasattr(self, 'id_selecionado'):
            messagebox.showwarning("Aviso", "Selecione uma anomalia na tabela para excluir.")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este registo de anomalia?"):
            resp = ApiCliente.delete(f"anomalias/{self.id_selecionado}")
            if resp and resp.status_code == 200:
                messagebox.showinfo("Sucesso", "Anomalia excluída com sucesso!")
                if hasattr(self, 'id_selecionado'):
                    del self.id_selecionado
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", "Não foi possível excluir a anomalia.")