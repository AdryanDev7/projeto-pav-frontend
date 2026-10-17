import requests

API_URL = "http://127.0.0.1:5000/api"

class ApiCliente:
    @staticmethod
    def get(endpoint):
        try:
            response = requests.get(f"{API_URL}/{endpoint}")
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except requests.exceptions.ConnectionError:
            return "CONNECTION_ERROR"
        except Exception:
            return None

    @staticmethod
    def post(endpoint, dados):
        try:
            response = requests.post(f"{API_URL}/{endpoint}", json=dados)
            return response
        except requests.exceptions.ConnectionError:
            return "CONNECTION_ERROR"
        except Exception:
            return None

    @staticmethod
    def put(endpoint, dados):
        try:
            response = requests.put(f"{API_URL}/{endpoint}", json=dados)
            return response
        except requests.exceptions.ConnectionError:
            return "CONNECTION_ERROR"
        except Exception:
            return None

    @staticmethod
    def delete(endpoint):
        try:
            response = requests.delete(f"{API_URL}/{endpoint}")
            return response
        except requests.exceptions.ConnectionError:
            return "CONNECTION_ERROR"
        except Exception:
            return None