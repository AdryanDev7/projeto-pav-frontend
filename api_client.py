"""
Cliente HTTP centralizado: é o ÚNICO módulo que conhece o `requests`.

Todos os métodos devolvem uma destas três coisas:
  * um objeto `requests.Response`  -> a API respondeu (com sucesso ou com erro HTTP);
  * a string CONNECTION_ERROR      -> API fora do ar, recusou a conexão ou demorou demais;
  * None                           -> qualquer outro erro inesperado.

ATENÇÃO: `bool(Response)` é False para status 4xx/5xx. Por isso, nunca use
`if resp:` para saber se a API respondeu; use `resp is None` / `isinstance(resp, str)`.
"""
import requests
from requests.exceptions import ConnectionError as ErroDeConexao, Timeout

API_URL = "http://127.0.0.1:5000/api"
TIMEOUT = 5                       # segundos; evita a interface "congelar" se a API cair
CONNECTION_ERROR = "CONNECTION_ERROR"


class ApiCliente:
    @staticmethod
    def _enviar(funcao_http, endpoint, **argumentos):
        """Executa requests.get/post/put/delete com timeout e tratamento de erros comum."""
        try:
            return funcao_http(f"{API_URL}/{endpoint}", timeout=TIMEOUT, **argumentos)
        except (ErroDeConexao, Timeout):
            return CONNECTION_ERROR
        except requests.exceptions.RequestException:
            return None

    @staticmethod
    def get(endpoint, params=None):
        return ApiCliente._enviar(requests.get, endpoint, params=params)

    @staticmethod
    def post(endpoint, dados):
        return ApiCliente._enviar(requests.post, endpoint, json=dados)

    @staticmethod
    def put(endpoint, dados):
        return ApiCliente._enviar(requests.put, endpoint, json=dados)

    @staticmethod
    def delete(endpoint):
        return ApiCliente._enviar(requests.delete, endpoint)
