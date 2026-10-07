import json
import urllib.request

class IndicadorService:
    @staticmethod
    def obtener_valor_dolar(valor_por_defecto: int = 950) -> int:
        """
        Consulta la API de mindicador.cl para obtener el valor oficial del dólar observado en CLP.
        Si la API no responde o no hay conexión, retorna un valor de referencia por defecto.
        """
        try:
            url = "https://mindicador.cl/api/dolar"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    serie = data.get("serie", [])
                    if serie:
                        return int(round(serie[0]["valor"]))
        except Exception as e:
            print(f"[Aviso API] No se pudo obtener el valor del dólar en línea ({e}). Usando valor por defecto: ${valor_por_defecto} CLP.")
        
        return valor_por_defecto
