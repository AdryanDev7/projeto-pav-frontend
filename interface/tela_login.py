from tkinter import ttk

from api_client import ApiError


class TelaLogin(ttk.Frame):
    """Login simplificado: escolhe quem é o operador (a API usa o id no cabeçalho X-Operador-Id)."""

    def __init__(self, master, api, ao_entrar):
        super().__init__(master, padding=40)
        self.api = api
        self._ao_entrar = ao_entrar
        self._operadores = {}
        ttk.Label(self, text="Monitoramento de Sensores IoT", font=("Segoe UI", 18, "bold")).pack(pady=10)
        ttk.Label(self, text="Selecione o operador:").pack()
        self.combo = ttk.Combobox(self, state="readonly", width=45)
        self.combo.pack(pady=6)
        ttk.Button(self, text="Entrar", command=self.entrar).pack(pady=4)
        ttk.Button(self, text="Recarregar lista", command=self.carregar).pack()
        self.aviso = ttk.Label(self, foreground="red", wraplength=500)
        self.aviso.pack(pady=10)
        self.carregar()

    def carregar(self):
        self.aviso.config(text="")
        try:
            lista = self.api.get("/operadores/login")
        except ApiError as erro:
            self.aviso.config(text=str(erro))
            self.combo["values"] = []
            return
        self._operadores = {f"{o['nome']} - {o['perfil']} ({o['zona']})": o for o in lista}
        self.combo["values"] = list(self._operadores)

    def entrar(self):
        escolhido = self._operadores.get(self.combo.get())
        if escolhido is None:
            self.aviso.config(text="Selecione um operador para continuar.")
            return
        self._ao_entrar(escolhido)
