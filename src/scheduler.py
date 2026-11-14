from apscheduler.schedulers.blocking import BlockingScheduler

from src.config import settings
from src.main import run_check
from src.utils.logger import get_logger

logger = get_logger(__name__)


def start():
    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        run_check,
        trigger="interval",
        hours=settings.schedule_hours,
        id="daily_job_search",
        max_instances=1,
        coalesce=True,
    )
    logger.info(
        "Monitor iniciado. A primeira consulta será executada agora; "
        "as próximas ocorrerão a cada %s hora(s).",
        settings.schedule_hours,
    )
    run_check()
    scheduler.start()


if __name__ == "__main__":
    start()
