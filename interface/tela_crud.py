"""Tela genérica de CRUD (tabela + formulário + botões). Cada entidade HERDA desta classe
e só informa: recurso da API, colunas da tabela e campos do formulário."""
import tkinter as tk
from dataclasses import dataclass, field
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Any, List

from api_client import ApiError


@dataclass
class Campo:
    chave: str                       # nome do campo no JSON da API
    rotulo: str                      # texto mostrado ao usuário
    tipo: str = "str"                # str | int | float | bool | combo | ref | datetime
    obrigatorio: bool = True
    opcoes: List[str] = field(default_factory=list)   # para tipo combo
    recurso_ref: str = ""            # para tipo ref: de onde carregar as opções (ex.: /sensores)
    padrao: Any = ""


class TelaCrud(ttk.Frame):
    titulo = ""
    recurso = ""
    colunas: list = []               # (chave, titulo, largura)
    campos: List[Campo] = []

    def __init__(self, master, api):
        super().__init__(master, padding=8)
        self.api = api
        self._registros = {}
        self._id_atual = None
        self._vars = {}
        self._widgets = {}
        self._refs = {}              # chave -> {rótulo exibido: id}
        self._montar_tabela()
        self._montar_formulario()
        self._montar_botoes()

    # ---------------------------------------------------------- construção
    def _montar_tabela(self):
        quadro = ttk.Frame(self)
        quadro.pack(fill="both", expand=True)
        chaves = [c[0] for c in self.colunas]
        self.tree = ttk.Treeview(quadro, columns=chaves, show="headings", selectmode="browse", height=10)
        for chave, titulo, largura in self.colunas:
            self.tree.heading(chave, text=titulo)
            self.tree.column(chave, width=largura, anchor="w")
        barra = ttk.Scrollbar(quadro, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=barra.set)
        self.tree.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar)

    def _montar_formulario(self):
        moldura = ttk.LabelFrame(self, text=f"{self.titulo} - formulário (* obrigatório)", padding=8)
        moldura.pack(fill="x", pady=8)
        for indice, campo in enumerate(self.campos):
            linha, coluna = divmod(indice, 2)
            ttk.Label(moldura, text=campo.rotulo + (" *" if campo.obrigatorio else "")).grid(
                row=linha, column=coluna * 2, sticky="e", padx=4, pady=3)
            if campo.tipo == "bool":
                var = tk.BooleanVar(value=bool(campo.padrao))
                widget = ttk.Checkbutton(moldura, variable=var)
            elif campo.tipo in ("combo", "ref"):
                var = tk.StringVar()
                widget = ttk.Combobox(moldura, textvariable=var, values=campo.opcoes,
                                      state="readonly", width=32)
            else:
                var = tk.StringVar()
                widget = ttk.Entry(moldura, textvariable=var, width=35)
            widget.grid(row=linha, column=coluna * 2 + 1, sticky="w", padx=4, pady=3)
            self._vars[campo.chave] = var
            self._widgets[campo.chave] = widget

    def _montar_botoes(self):
        self.barra_botoes = ttk.Frame(self)
        self.barra_botoes.pack(fill="x")
        ttk.Button(self.barra_botoes, text="Novo", command=self.novo).pack(side="left", padx=3)
        ttk.Button(self.barra_botoes, text="Salvar", command=self.salvar).pack(side="left", padx=3)
        ttk.Button(self.barra_botoes, text="Excluir", command=self.excluir).pack(side="left", padx=3)
        ttk.Button(self.barra_botoes, text="Atualizar lista", command=self.carregar).pack(side="left", padx=3)
        self._botoes_extras(self.barra_botoes)

    def _botoes_extras(self, barra):
        """Gancho: telas filhas podem adicionar botões."""

    # ------------------------------------------------------------ operações
    def atualizar(self):
        self.carregar()

    def carregar(self):
        try:
            self._carregar_referencias()
            dados = self.api.get(self.recurso)
        except ApiError as erro:
            messagebox.showerror("Erro ao carregar", str(erro))
            return
        self._registros = {item["id"]: item for item in dados}
        self.tree.delete(*self.tree.get_children())
        for item in dados:
            valores = [self._formatar(item.get(chave)) for chave, _, _ in self.colunas]
            self.tree.insert("", "end", iid=str(item["id"]), values=valores)
        self.novo()

    def _carregar_referencias(self):
        """Para campos do tipo 'ref', busca na API as opções (ex.: lista de sensores)."""
        for campo in self.campos:
            if campo.tipo != "ref":
                continue
            itens = self.api.get(campo.recurso_ref)
            self._refs[campo.chave] = {f"{i['id']} - {i['nome']}": i["id"] for i in itens}
            self._widgets[campo.chave]["values"] = list(self._refs[campo.chave].keys())

    def novo(self):
        self._id_atual = None
        self.tree.selection_remove(self.tree.selection())
        for campo in self.campos:
            var = self._vars[campo.chave]
            if campo.tipo == "bool":
                var.set(bool(campo.padrao))
            elif campo.tipo == "combo":
                var.set(campo.padrao or (campo.opcoes[0] if campo.opcoes else ""))
            elif campo.tipo == "ref":
                var.set("")
            else:
                var.set(str(campo.padrao))

    def _ao_selecionar(self, _evento=None):
        selecao = self.tree.selection()
        if not selecao:
            return
        registro = self._registros.get(int(selecao[0]))
        if registro is None:
            return
        self._id_atual = registro["id"]
        for campo in self.campos:
            valor = registro.get(campo.chave)
            var = self._vars[campo.chave]
            if campo.tipo == "bool":
                var.set(bool(valor))
            elif campo.tipo == "ref":
                rotulo = next((r for r, i in self._refs.get(campo.chave, {}).items() if i == valor), "")
                var.set(rotulo)
            elif campo.tipo == "datetime":
                var.set("" if valor is None else str(valor)[:19].replace("T", " "))
            else:
                var.set("" if valor is None else str(valor))

    def registro_selecionado(self):
        """Devolve o registro (dict) da linha selecionada ou avisa o usuário."""
        if self._id_atual is None:
            messagebox.showwarning("Seleção necessária", "Selecione um registro na tabela primeiro.")
            return None
        return self._registros.get(self._id_atual)

    def salvar(self):
        try:
            carga = self._coletar()
        except ValueError as erro:
            messagebox.showwarning("Dados inválidos", str(erro))
            return
        try:
            if self._id_atual is None:
                self.api.post(self.recurso, json=carga)
                messagebox.showinfo("Sucesso", "Registro cadastrado com sucesso.")
            else:
                self.api.put(f"{self.recurso}/{self._id_atual}", json=carga)
                messagebox.showinfo("Sucesso", "Registro atualizado com sucesso.")
        except ApiError as erro:
            messagebox.showerror("Não foi possível salvar", str(erro))
            return
        self.carregar()

    def excluir(self):
        registro = self.registro_selecionado()
        if registro is None:
            return
        if not messagebox.askyesno("Confirmar exclusão", f"Excluir o registro {registro['id']}?"):
            return
        try:
            self.api.delete(f"{self.recurso}/{registro['id']}")
            messagebox.showinfo("Sucesso", "Registro excluído.")
        except ApiError as erro:
            messagebox.showerror("Não foi possível excluir", str(erro))
            return
        self.carregar()

    # ----------------------------------------------------------- utilitários
    def _coletar(self) -> dict:
        """Lê o formulário, valida obrigatórios e converte tipos. Levanta ValueError amigável."""
        carga = {}
        for campo in self.campos:
            bruto = self._vars[campo.chave].get()
            if campo.tipo == "bool":
                carga[campo.chave] = bool(bruto)
                continue
            texto = str(bruto).strip()
            if not texto:
                if campo.obrigatorio:
                    raise ValueError(f"O campo '{campo.rotulo}' é obrigatório.")
                continue
            try:
                if campo.tipo == "int":
                    carga[campo.chave] = int(texto)
                elif campo.tipo == "float":
                    carga[campo.chave] = float(texto.replace(",", "."))
                elif campo.tipo == "ref":
                    carga[campo.chave] = self._refs[campo.chave][texto]
                elif campo.tipo == "datetime":
                    carga[campo.chave] = datetime.fromisoformat(texto).isoformat()
                else:
                    carga[campo.chave] = texto
            except (ValueError, KeyError):
                dica = " (formato AAAA-MM-DD HH:MM:SS)" if campo.tipo == "datetime" else ""
                raise ValueError(f"Valor inválido no campo '{campo.rotulo}'{dica}.")
        return carga

    @staticmethod
    def _formatar(valor):
        if valor is None:
            return ""
        if isinstance(valor, bool):
            return "Sim" if valor else "Não"
        if isinstance(valor, str) and "T" in valor and len(valor) >= 19 and valor[4] == "-":
            return valor[:19].replace("T", " ")
        return valor
