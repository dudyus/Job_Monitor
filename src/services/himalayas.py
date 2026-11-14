import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)


class HimalayasClient:
    """Cliente para a API pública de vagas remotas da Himalayas."""

    BASE_URL = "https://himalayas.app/jobs/api/search"

    def __init__(self, session=None):
        self.session = session or requests.Session()

    def search(self, term, country, max_pages=2):
        """Busca por termo e país, percorrendo páginas até o limite configurado."""
        collected = []
        seen_guids = set()

        for page in range(1, max_pages + 1):
            params = {
                "q": term,
                "country": country,
                "sort": "recent",
                "page": page,
            }

            try:
                response = self.session.get(self.BASE_URL, params=params, timeout=30)

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "não informado")
                    raise RuntimeError(
                        f"Limite de requisições da Himalayas atingido (429). "
                        f"Retry-After: {retry_after}"
                    )

                response.raise_for_status()
                payload = response.json()

                if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
                    raise ValueError("Resposta inesperada da Himalayas: campo 'jobs' ausente.")

                jobs = payload["jobs"]
                if not jobs:
                    break

                for job in jobs:
                    guid = str(job.get("guid") or "").strip()
                    if guid and guid not in seen_guids:
                        seen_guids.add(guid)
                        collected.append(job)

                # A API informa até 20 resultados por página; página menor encerra a busca.
                if len(jobs) < 20:
                    break

            except requests.Timeout as exc:
                logger.error("Timeout consultando Himalayas (termo=%s, país=%s)", term, country)
                raise RuntimeError("A API da Himalayas demorou demais para responder.") from exc
            except requests.HTTPError:
                logger.exception("Resposta HTTP de erro da Himalayas.")
                raise
            except requests.RequestException as exc:
                logger.error("Erro de conexão com Himalayas: %s", exc)
                raise
            except ValueError:
                logger.exception("Não foi possível interpretar o JSON da Himalayas.")
                raise

        return collected
