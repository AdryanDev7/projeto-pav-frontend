"""
BaseCrudView: classe-base (HERANÇA) com tudo o que é comum às telas de CRUD:
título, formulário, botões, tabela, seleção de linha, carregar/excluir.

Cada tela concreta (Localizacao, Sensor, Leitura, Anomalia) só precisa definir:
  * constantes de classe (ENDPOINT, COLUNAS, ...);
  * criar_formulario / coletar_dados / preencher_formulario / limpar_formulario.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from api_client import ApiCliente
from helpers import ValidacaoError, tratar_resposta, carregar_lista


class BaseCrudView:
    TITULO = ""
    TITULO_FORM = "Cadastrar / Atualizar"
    ENDPOINT = ""
    # Lista de (chave_no_json, título_da_coluna, largura)
    COLUNAS = []

    def __init__(self, parent):
        self.parent = parent
        self.id_selecionado = None   # id do registro escolhido na tabela
        self.registros = {}          # {id: dict completo} -> usado para preencher o formulário
        self.criar_componentes()
        self.carregar_dados()

    # ------------------------------------------------------------------ layout
    def criar_componentes(self):
        tk.Label(self.parent, text=self.TITULO, font=("Arial", 14, "bold")).pack(pady=10)

        self.criar_filtros()   # opcional (as filhas podem sobrescrever)

        self.frame_form = tk.LabelFrame(self.parent, text=self.TITULO_FORM, padx=10, pady=10)
        self.frame_form.pack(fill="x", padx=10, pady=5)
        self.criar_formulario(self.frame_form)

        frame_botoes = tk.Frame(self.parent)
        frame_botoes.pack(pady=5)
        tk.Button(frame_botoes, text="Cadastrar", bg="green", fg="white",
                  command=self.salvar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Atualizar Selecionado", bg="orange", fg="white",
                  command=self.atualizar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Excluir Selecionado", bg="red", fg="white",
                  command=self.excluir).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Limpar Formulário",
                  command=self.limpar_tudo).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Atualizar Lista",
                  command=lambda: self.carregar_dados(mostrar_popup=True)).pack(side="left", padx=5)

        # Linha de status: mostra "N registros" ou a mensagem de erro de conexão
        self.lbl_status = tk.Label(self.parent, text="", anchor="w")
        self.lbl_status.pack(fill="x", padx=10)

        frame_tabela = tk.Frame(self.parent)
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        chaves = [c[0] for c in self.COLUNAS]
        self.tree = ttk.Treeview(frame_tabela, columns=chaves, show="headings")
        for chave, titulo, largura in self.COLUNAS:
            self.tree.heading(chave, text=titulo)
            self.tree.column(chave, width=largura, anchor="w")
        barra = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=barra.set)
        self.tree.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.selecionar_linha)

    # ----------------------------------------- métodos que as filhas implementam
    def criar_filtros(self):
        """(Opcional) barra de filtros acima do formulário."""

    def parametros_consulta(self):
        """(Opcional) parâmetros de query string para o GET da lista."""
        return None

    def criar_formulario(self, frame):
        raise NotImplementedError

    def coletar_dados(self, editando=False):
        """Lê os campos, VALIDA localmente (levanta ValidacaoError) e devolve o dict para a API."""
        raise NotImplementedError

    def preencher_formulario(self, registro):
        raise NotImplementedError

    def limpar_formulario(self):
        raise NotImplementedError

    # ------------------------------------------------------------------ helpers de UI
    @staticmethod
    def definir_texto(entry, valor):
        """Troca o conteúdo de um Entry/Combobox."""
        entry.delete(0, tk.END)
        entry.insert(0, "" if valor is None else str(valor))

    def limpar_tudo(self):
        self.limpar_formulario()
        self.id_selecionado = None
        self.tree.selection_remove(self.tree.selection())

    def _mostrar_status(self, texto, erro=False):
        self.lbl_status.config(text=texto, fg="red" if erro else "gray25")

    # ------------------------------------------------------------------ READ
    def carregar_dados(self, mostrar_popup=False):
        """GET da lista. Erros de conexão aparecem na linha de status (e em popup se pedido)."""
        try:
            params = self.parametros_consulta()
        except ValidacaoError as erro:
            messagebox.showwarning("Filtro inválido", str(erro))
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.registros = {}

        lista, erro = carregar_lista(self.ENDPOINT, params)
        if erro:
            self._mostrar_status(erro.replace("\n", " "), erro=True)
            if mostrar_popup:
                messagebox.showerror("Erro ao carregar dados", erro)
            return

        for registro in lista:
            self.registros[registro["id"]] = registro
            valores = [registro.get(chave) for chave, _, _ in self.COLUNAS]
            self.tree.insert("", "end", iid=str(registro["id"]), values=valores)
        self._mostrar_status(f"{len(lista)} registro(s) carregado(s).")

    def selecionar_linha(self, _evento=None):
        selecionado = self.tree.selection()
        if not selecionado:
            return
        self.id_selecionado = int(selecionado[0])             # o iid da linha é o id do registro
        registro = self.registros.get(self.id_selecionado)
        if registro:
            # Preenche a partir do dict (e não do Treeview): o Treeview converte "007" em 7!
            self.preencher_formulario(registro)

    # ------------------------------------------------------------------ CREATE
    def salvar(self):
        try:
            dados = self.coletar_dados(editando=False)
        except ValidacaoError as erro:
            messagebox.showwarning("Verifique os dados", str(erro))
            return
        resp = ApiCliente.post(self.ENDPOINT, dados)
        if tratar_resposta(resp, status_ok=(201,)) is not None:
            self.limpar_tudo()
            self.carregar_dados()

    # ------------------------------------------------------------------ UPDATE
    def atualizar(self):
        if self.id_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um registro na tabela para atualizar.")
            return
        try:
            dados = self.coletar_dados(editando=True)
        except ValidacaoError as erro:
            messagebox.showwarning("Verifique os dados", str(erro))
            return
        resp = ApiCliente.put(f"{self.ENDPOINT}/{self.id_selecionado}", dados)
        if tratar_resposta(resp, status_ok=(200,)) is not None:
            self.limpar_tudo()
            self.carregar_dados()

    # ------------------------------------------------------------------ DELETE
    def excluir(self):
        if self.id_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um registro na tabela para excluir.")
            return
        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir este registro?"):
            return
        resp = ApiCliente.delete(f"{self.ENDPOINT}/{self.id_selecionado}")
        if tratar_resposta(resp, status_ok=(200,)) is not None:
            self.limpar_tudo()
        # Recarrega sempre: se o registro já tinha sido removido (404), a lista se corrige sozinha
        self.carregar_dados()
