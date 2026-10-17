# 🖥️ Painel de Controlo - Sistema IoT (Frontend PAV)

Interface gráfica desenvolvida em **Python (Tkinter)** para a unidade curricular de **Programação de Aplicações Visuais (PAV)**. Esta aplicação atua como camada de apresentação visual, comunicando-se de forma totalmente modularizada com a API REST do backend através de requisições HTTP (`requests`).

---

## 🚀 Tecnologias Utilizadas
* **Linguagem:** Python 3.13+
* **Interface Gráfica (GUI):** Tkinter & TTK (Themed Tkinter)
* **Comunicação HTTP:** Biblioteca `requests`
* **Arquitetura:** Projeto separado do backend, organizado por domínios/views.

---

## 📂 Estrutura do Frontend
* **`main.py`**: Ponto de entrada principal da aplicação gráfica com janelas em abas (*Notebook*).
* **`api_client.py`**: Cliente HTTP centralizado responsável por gerir as requisições (GET, POST, PUT, DELETE) com a API Flask.
* **`views/`**: Módulos visuais independentes para a gestão de cada entidade:
  * `localizacao_view.py`: Gestão de fábricas e coordenadas geográficas.
  * `sensor_view.py`: Controlo de dispositivos IoT e níveis de bateria.
  * `leitura_view.py`: Registo temporal de medições com simulação de alertas.
  * `anomalia_view.py`: Monitorização de alertas críticos gerados automaticamente.

---

## 📋 Funcionalidades da Interface
1. **Gestão Completa (CRUD):** Cada aba possui ecrãs dedicados para Cadastro, Consulta em tabela dinâmica (`Treeview`), Edição de registos selecionados e Exclusão segura.
2. **Atualização Dinâmica:** Botões de sincronização com a API para recarregar dados em tempo real.
3. **Tratamento Robusto de Erros:** Validações visuais integradas (`messagebox`) para campos obrigatórios, tipos de dados incorretos e falhas de comunicação com o servidor backend.

---

## ⚙️ Como Executar o Frontend

1. **Garantir que a API Backend e o Docker estão a rodar:**
   * Certifica-te de que o PostgreSQL está ativo via Docker e a API Flask (`app.py`) está a escutar na porta `5000`.

2. **Instalar as Dependências:**
   ```bash
   pip install requests

3. **Executar a Aplicação:**
    python main.py