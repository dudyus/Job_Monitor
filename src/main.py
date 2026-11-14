from dotenv import load_dotenv

from src.config import settings
from src.database.repository import JobRepository
from src.processing.filters import is_relevant
from src.processing.normalizer import normalize_job
from src.services.himalayas import HimalayasClient
from src.services.telegram import TelegramClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_check():
    """Busca vagas na Himalayas, filtra, salva as inéditas e notifica."""
    client = HimalayasClient()
    repo = JobRepository(settings.database_path)
    telegram = TelegramClient(
        token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )

    new_jobs = []
    try:
        for country in settings.countries:
            for term in settings.search_terms:
                logger.info("Consultando Himalayas: termo='%s', país=%s", term, country)
                raw_jobs = client.search(
                    term=term,
                    country=country,
                    max_pages=settings.max_pages_per_search,
                )

                for raw_job in raw_jobs:
                    job = normalize_job(raw_job, country)
                    if not is_relevant(job):
                        continue
                    if repo.insert_if_new(job):
                        new_jobs.append(job)

        logger.info("Coleta finalizada. Vagas inéditas encontradas: %d", len(new_jobs))

        # Também tenta enviar vagas antigas que ficaram pendentes quando o Telegram
        # ainda não estava configurado. Assim, a primeira execução sem credenciais
        # não faz as vagas serem perdidas para notificações futuras.
        if not telegram.is_configured:
            logger.info(
                "Telegram não configurado. As vagas ficam salvas como pendentes; "
                "configure o bot para receber as notificações."
            )
        else:
            pending_jobs = repo.get_pending_notifications()
            logger.info("Vagas aguardando notificação: %d", len(pending_jobs))
            for job in pending_jobs:
                try:
                    telegram.send_job(job)
                    repo.mark_notified(job["guid"])
                except Exception:
                    logger.exception("Falha ao notificar vaga: %s", job["title"])

        return new_jobs
    finally:
        repo.close()


def main():
    load_dotenv()
    if not settings.countries:
        raise ValueError("Configure ao menos um país em COUNTRIES no arquivo .env.")
    run_check()


if __name__ == "__main__":
    main()
