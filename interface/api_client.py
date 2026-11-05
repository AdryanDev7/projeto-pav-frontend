"""Único ponto de comunicação com a API. Todas as telas usam esta classe.
Converte QUALQUER falha (rede, 404, 405, 422...) em ApiError com mensagem compreensível."""
import os

import requests

URL_PADRAO = os.getenv("API_URL", "http://localhost:8000")

# Tradução das mensagens de validação do Pydantic (que vêm em inglês)
TRADUCOES = {
    "missing": "campo obrigatório",
    "string_too_short": "texto muito curto",
    "string_too_long": "texto muito longo",
    "literal_error": "valor não permitido",
    "greater_than": "deve ser maior que zero",
    "float_parsing": "deve ser um número",
    "int_parsing": "deve ser um número inteiro",
    "datetime_parsing": "data/hora inválida",
    "datetime_from_date_parsing": "data/hora inválida",
    "bool_parsing": "valor verdadeiro/falso inválido",
}

MENSAGENS_PADRAO = {
    401: "Operador não identificado. Faça login novamente.",
    403: "Você não tem permissão para esta ação.",
    404: "Registro não encontrado.",
    405: "Operação não permitida para este registro.",
    409: "Conflito: a operação não pode ser concluída.",
    422: "Dados inválidos.",
}


class ApiError(Exception):
    def __init__(self, mensagem: str, status: int = None):
        super().__init__(mensagem)
        self.status = status


class ApiClient:
    def __init__(self, url_base: str = URL_PADRAO, timeout: int = 8):
        self._url_base = url_base.rstrip("/")
        self._timeout = timeout
        self.operador = None          # dict do operador logado (id, nome, perfil, zona)

    # ------------------------------------------------------------ métodos HTTP
    def get(self, caminho, params=None):
        return self._requisitar("GET", caminho, params=params)

    def post(self, caminho, json=None):
        return self._requisitar("POST", caminho, json=json)

    def put(self, caminho, json=None):
        return self._requisitar("PUT", caminho, json=json)

    def delete(self, caminho):
        return self._requisitar("DELETE", caminho)

    # --------------------------------------------------------------- interno
    def _requisitar(self, metodo, caminho, **kwargs):
        cabecalhos = {}
        if self.operador:
            cabecalhos["X-Operador-Id"] = str(self.operador["id"])
        try:
            resposta = requests.request(metodo, self._url_base + caminho, headers=cabecalhos,
                                        timeout=self._timeout, **kwargs)
        except requests.exceptions.ConnectionError:
            raise ApiError("Não foi possível conectar à API. Verifique se ela está em execução "
                           f"({self._url_base}).")
        except requests.exceptions.Timeout:
            raise ApiError("A API demorou demais para responder. Tente novamente.")
        except requests.exceptions.RequestException as erro:
            raise ApiError(f"Erro de comunicação com a API: {erro}")

        if resposta.status_code >= 400:
            raise ApiError(self._traduzir_erro(resposta), resposta.status_code)
        if resposta.status_code == 204 or not resposta.content:
            return None
        return resposta.json()

    @staticmethod
    def _traduzir_erro(resposta) -> str:
        try:
            detalhe = resposta.json().get("detail")
        except ValueError:
            detalhe = None

        if isinstance(detalhe, str):                 # erros de negócio da API
            return detalhe
        if isinstance(detalhe, list):                # erros de validação do Pydantic
            linhas = []
            for item in detalhe:
                campo = str(item.get("loc", ["?"])[-1])
                motivo = TRADUCOES.get(item.get("type"), item.get("msg", "valor inválido"))
                linhas.append(f"• {campo}: {motivo}")
            return "Dados inválidos:\n" + "\n".join(linhas)
        if resposta.status_code >= 500:
            return "Erro interno na API. Tente novamente em instantes."
        return MENSAGENS_PADRAO.get(resposta.status_code, f"Erro {resposta.status_code} na API.")
