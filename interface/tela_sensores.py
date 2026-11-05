from tela_crud import Campo, TelaCrud


class TelaSensores(TelaCrud):
    titulo = "Sensores"
    recurso = "/sensores"
    colunas = [
        ("id", "ID", 40), ("nome", "Nome", 160), ("tipo", "Tipo", 100), ("zona", "Zona", 80),
        ("status", "Status", 110), ("ativo", "Ativo", 50), ("intervalo_segundos", "Intervalo (s)", 85),
        ("limite_seguranca", "Limite", 60), ("ultimo_valor", "Último valor", 85),
        ("leituras_acima_limite", "Acima limite", 85),
        ("atuador_tipo", "Atuador", 70), ("atuador_estado", "Estado atuador", 100),
    ]
    campos = [
        Campo("nome", "Nome"),
        Campo("tipo", "Tipo", tipo="combo", opcoes=["TEMPERATURA", "UMIDADE", "PRESSAO"]),
        Campo("zona", "Zona"),
        Campo("limite_seguranca", "Limite de segurança", tipo="float"),
        Campo("intervalo_segundos", "Intervalo de envio (s)", tipo="int", padrao="300"),
        Campo("atuador_tipo", "Tipo de atuador", tipo="combo", opcoes=["RELE", "VALVULA"]),
        Campo("atuador_estado", "Estado do atuador", tipo="combo", obrigatorio=False,
              opcoes=["", "LIGADO", "DESLIGADO", "ABERTA", "FECHADA"]),
        Campo("ativo", "Ativo", tipo="bool", padrao=True),
        Campo("instalado_em", "Instalado em (AAAA-MM-DD HH:MM:SS)", tipo="datetime", obrigatorio=False),
    ]
