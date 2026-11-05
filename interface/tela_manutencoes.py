from tela_crud import Campo, TelaCrud


class TelaManutencoes(TelaCrud):
    titulo = "Manutenções / Aferições"
    recurso = "/manutencoes"
    colunas = [("id", "ID", 50), ("sensor_id", "Sensor", 70),
               ("data_afericao", "Data da aferição", 160), ("descricao", "Descrição", 400)]
    campos = [
        Campo("sensor_id", "Sensor", tipo="ref", recurso_ref="/sensores"),
        Campo("data_afericao", "Data (AAAA-MM-DD HH:MM:SS)", tipo="datetime", obrigatorio=False),
        Campo("descricao", "Descrição", obrigatorio=False),
    ]
