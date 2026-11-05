from tela_crud import Campo, TelaCrud


class TelaOperadores(TelaCrud):
    titulo = "Operadores"
    recurso = "/operadores"
    colunas = [("id", "ID", 50), ("nome", "Nome", 250), ("perfil", "Perfil", 130), ("zona", "Zona", 150)]
    campos = [
        Campo("nome", "Nome"),
        Campo("perfil", "Perfil", tipo="combo", opcoes=["OPERADOR", "SUPERVISOR"]),
        Campo("zona", "Zona"),
    ]
