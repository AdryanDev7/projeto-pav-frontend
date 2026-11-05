from tkinter import messagebox, ttk

from api_client import ApiError
from tela_crud import Campo, TelaCrud


class TelaAlertas(TelaCrud):
    titulo = "Alertas"
    recurso = "/alertas"
    colunas = [("id", "ID", 40), ("sensor_id", "Sensor", 60), ("prioridade", "Prioridade", 80),
               ("status", "Status", 100), ("mensagem", "Mensagem", 330),
               ("criado_em", "Criado em", 140), ("reconhecido_por", "Reconhecido por", 110)]
    campos = [
        Campo("sensor_id", "Sensor", tipo="ref", recurso_ref="/sensores"),
        Campo("prioridade", "Prioridade", tipo="combo", opcoes=["ALTA", "MEDIA", "BAIXA"]),
        Campo("status", "Status", tipo="combo", opcoes=["ABERTO", "RECONHECIDO", "ESCALONADO"]),
        Campo("mensagem", "Mensagem", obrigatorio=False),
    ]

    def _botoes_extras(self, barra):
        ttk.Button(barra, text="Reconhecer alerta selecionado", command=self.reconhecer).pack(side="left", padx=12)

    def reconhecer(self):
        registro = self.registro_selecionado()
        if registro is None:
            return
        try:
            self.api.post(f"/alertas/{registro['id']}/reconhecer")
            messagebox.showinfo("Sucesso", "Alerta reconhecido. O escalonamento foi evitado.")
        except ApiError as erro:
            messagebox.showerror("Não foi possível reconhecer", str(erro))
            return
        self.carregar()
