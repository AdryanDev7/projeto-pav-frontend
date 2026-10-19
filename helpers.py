"""
Funções auxiliares usadas por TODAS as views:
  1. Validação local dos campos (antes de chamar a API);
  2. Tratamento padronizado das respostas da API (sucesso e erro);
  3. Carregamento padronizado de listas (GET).
"""
from datetime import datetime
from tkinter import messagebox

from api_client import ApiCliente

MSG_CONEXAO = ("Não foi possível conectar à API.\n"
               "Verifique se o servidor (Docker / Flask) está em execução na porta 5000.")
MSG_INESPERADO = "Ocorreu um erro inesperado ao comunicar com a API."
FORMATO_DATA_HORA = "%Y-%m-%d %H:%M:%S"


# ---------------------------------------------------------------------------
# 1. VALIDAÇÕES LOCAIS (levantam ValidacaoError com mensagem pronta para o usuário)
# ---------------------------------------------------------------------------
class ValidacaoError(Exception):
    """Erro de validação detectado na própria interface, antes de qualquer requisição."""


def obrigatorio(valor, rotulo):
    """Campo de texto obrigatório: não pode estar vazio nem só com espaços."""
    valor = str(valor).strip()
    if not valor:
        raise ValidacaoError(f"O campo '{rotulo}' é obrigatório.")
    return valor


def inteiro(valor, rotulo):
    """Obrigatório + precisa ser número inteiro."""
    valor = obrigatorio(valor, rotulo)
    try:
        return int(valor)
    except ValueError:
        raise ValidacaoError(f"O campo '{rotulo}' deve ser um número inteiro.")


def decimal(valor, rotulo):
    """Obrigatório + precisa ser número (aceita vírgula como separador decimal)."""
    valor = obrigatorio(valor, rotulo).replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        raise ValidacaoError(f"O campo '{rotulo}' deve ser um número válido.")


def data_hora_opcional(valor, rotulo, fim_do_dia=False):
    """
    Campo de data/hora que pode ficar vazio (devolve None).
    Aceita 'AAAA-MM-DD' ou 'AAAA-MM-DD HH:MM:SS'. Se for só a data e `fim_do_dia`
    for True, completa com 23:59:59 (para o filtro 'fim' incluir o dia inteiro).
    """
    valor = str(valor).strip()
    if not valor:
        return None
    try:
        momento = datetime.fromisoformat(valor)
    except ValueError:
        raise ValidacaoError(f"O campo '{rotulo}' deve estar no formato AAAA-MM-DD HH:MM:SS "
                             f"(ex.: 2026-10-19 14:30:00).")
    if fim_do_dia and len(valor) <= 10:
        momento = momento.replace(hour=23, minute=59, second=59)
    return momento.strftime(FORMATO_DATA_HORA)


def montar_filtro_periodo(inicio_txt, fim_txt):
    """Valida o período e devolve o dicionário de parâmetros ({'inicio':..., 'fim':...})."""
    inicio = data_hora_opcional(inicio_txt, "Início")
    fim = data_hora_opcional(fim_txt, "Fim", fim_do_dia=True)
    if inicio and fim and inicio > fim:
        raise ValidacaoError("A data de início não pode ser posterior à data de fim.")
    params = {}
    if inicio:
        params["inicio"] = inicio
    if fim:
        params["fim"] = fim
    return params


# ---------------------------------------------------------------------------
# 2. TRATAMENTO DE RESPOSTAS DA API
# ---------------------------------------------------------------------------
def corpo_json(resp):
    """Lê o JSON da resposta; devolve {} se o corpo não for um JSON válido."""
    try:
        return resp.json()
    except ValueError:
        return {}


def extrair_erro(resp):
    """
    Extrai a mensagem de erro da API. Formatos possíveis:
      {"erro": "..."}     -> erros das regras de negócio / validações do backend
      {"message": "..."}  -> erros do próprio Flask-RESTful (ex.: rota inexistente, 404/405)
    """
    corpo = corpo_json(resp)
    if isinstance(corpo, dict):
        mensagem = corpo.get("erro") or corpo.get("message")
        if mensagem:
            return str(mensagem)
    return f"A API respondeu com um erro (HTTP {resp.status_code})."


def _titulo_do_erro(status):
    if status == 400:
        return "Dados inválidos ou operação não permitida"
    if status == 404:
        return "Registro não encontrado"
    if status >= 500:
        return "Erro no servidor"
    return "Erro"


def tratar_resposta(resp, status_ok=(200, 201), mensagem_padrao="Operação realizada com sucesso!"):
    """
    Helper padrão para POST / PUT / DELETE.
    Sucesso -> mostra a "mensagem" devolvida pela API e retorna o corpo (dict).
    Erro    -> mostra uma caixa de erro compreensível e retorna None.
    """
    if isinstance(resp, str):        # CONNECTION_ERROR
        messagebox.showerror("Erro de conexão", MSG_CONEXAO)
        return None
    if resp is None:
        messagebox.showerror("Erro", MSG_INESPERADO)
        return None
    if resp.status_code in status_ok:
        corpo = corpo_json(resp)
        corpo = corpo if isinstance(corpo, dict) else {}
        messagebox.showinfo("Sucesso", corpo.get("mensagem", mensagem_padrao))
        return corpo
    messagebox.showerror(_titulo_do_erro(resp.status_code), extrair_erro(resp))
    return None


def carregar_lista(endpoint, params=None):
    """
    Helper padrão para GET de listas. Retorna sempre uma tupla (lista, erro):
      sucesso -> (lista_de_dicts, None)
      falha   -> (None, "mensagem para o usuário")
    """
    resp = ApiCliente.get(endpoint, params)
    if isinstance(resp, str):
        return None, MSG_CONEXAO
    if resp is None:
        return None, MSG_INESPERADO
    if resp.status_code != 200:
        return None, extrair_erro(resp)
    corpo = corpo_json(resp)
    if not isinstance(corpo, list):
        return None, "Resposta inesperada da API."
    return corpo, None


def carregar_objeto(endpoint, params=None):
    """Igual a carregar_lista, mas para respostas que são um único objeto JSON (dict)."""
    resp = ApiCliente.get(endpoint, params)
    if isinstance(resp, str):
        return None, MSG_CONEXAO
    if resp is None:
        return None, MSG_INESPERADO
    if resp.status_code != 200:
        return None, extrair_erro(resp)
    corpo = corpo_json(resp)
    if not isinstance(corpo, dict):
        return None, "Resposta inesperada da API."
    return corpo, None
