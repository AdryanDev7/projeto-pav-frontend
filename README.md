# 🖥️ Painel de Controlo - Sistema IoT (Frontend PAV)

Interface gráfica em **Python (Tkinter)** que consome a API REST (Flask-RESTful) do backend. Projeto separado da API; roda **fora** do Docker.

## Estrutura
* `main.py` – janela principal com abas (`ttk.Notebook`).
* `api_client.py` – único módulo que usa `requests`. Todas as chamadas têm `timeout=5`; devolve `Response`, `"CONNECTION_ERROR"` (API fora do ar/timeout) ou `None`.
* `helpers.py` – validações locais (`obrigatorio`, `inteiro`, `decimal`, datas) e tratamento padronizado das respostas (`tratar_resposta`, `carregar_lista`, `carregar_objeto`). Lê erros em `{"erro": ...}` e `{"message": ...}` e sucesso em `{"mensagem", "id", "dados"}`.
* `views/base_view.py` – `BaseCrudView`: classe-base (herança) com tabela, seleção, listar, excluir, cadastrar e editar.
* `views/localizacao_view.py`, `sensor_view.py`, `leitura_view.py`, `anomalia_view.py` – herdam de `BaseCrudView` e definem só formulário, validação e colunas.
* `views/analise_view.py` – aba **Análise / Estatísticas** (`GET /api/sensores/<id>/estatisticas`).

## Funcionalidades
* CRUD completo (cadastro, consulta, edição, exclusão) em Localizações, Sensores, Leituras e Anomalias.
* **Sensores:** status escolhido em Combobox (Ativo, Inativo, Em Manutenção).
* **Leituras:** edição (PUT) e filtros por sensor e período (`sensor_id`, `inicio`, `fim`).
* **Anomalias:** cadastro (POST), edição (PUT) e exclusão; severidade em Combobox.
* **Análise:** total de leituras, média, mínimo, máximo, desvio padrão e total de anomalias por sensor/período.
* Campos obrigatórios e tipos validados antes de enviar a requisição.
* Falha de conexão: mensagem na linha de status de cada aba ao carregar (sem pop-ups em cascata na abertura) e pop-up ao atualizar manualmente.
* Regras de negócio do backend (ex.: RN10 – localização com sensores) aparecem como mensagens claras.

## Como executar
1. Suba a API e o banco: `docker compose up` (API na porta 5000).
2. `pip install -r requirements.txt`
3. `python main.py`

Datas nos filtros: `AAAA-MM-DD` ou `AAAA-MM-DD HH:MM:SS` (no campo "Fim", só a data inclui o dia inteiro).
