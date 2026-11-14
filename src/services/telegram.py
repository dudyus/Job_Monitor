import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TelegramClient:
    """Cliente simples para envio de mensagens pela Telegram Bot API."""

    BASE_URL = "https://api.telegram.org/bot{token}/sendMessage"

    def __init__(self, token="", chat_id=""):
        self.token = token.strip()
        self.chat_id = chat_id.strip()

    @property
    def is_configured(self):
        return bool(self.token and self.chat_id)

    @staticmethod
    def format_job(job):
        salary = "Não informado"
        currency = job.get("currency") or ""
        minimum = job.get("min_salary")
        maximum = job.get("max_salary")
        period = job.get("salary_period") or ""
        if minimum is not None or maximum is not None:
            if minimum is not None and maximum is not None:
                salary = f"{currency} {minimum} – {maximum} {period}".strip()
            else:
                value = minimum if minimum is not None else maximum
                salary = f"{currency} {value} {period}".strip()

        return (
            "🔎 NOVA VAGA DE DADOS\n\n"
            f"Cargo: {job.get('title') or 'Não informado'}\n"
            f"Empresa: {job.get('company') or 'Não informada'}\n"
            f"Localização: {job.get('availability') or 'Não informada'}\n"
            f"Tipo: {job.get('employment_type') or 'Não informado'}\n"
            f"Salário: {salary}\n\n"
            f"Candidatura: {job.get('application_link') or 'Link não informado'}\n"
            "Fonte: Himalayas (https://himalayas.app)"
        )

    def send_job(self, job):
        if not self.is_configured:
            raise RuntimeError("Telegram não configurado. Preencha TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.")

        payload = {
            "chat_id": self.chat_id,
            "text": self.format_job(job),
            "disable_web_page_preview": False,
        }
        response = requests.post(
            self.BASE_URL.format(token=self.token),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            raise RuntimeError(f"Telegram recusou a mensagem: {result}")

        logger.info("Notificação enviada pelo Telegram: %s", job.get("title"))
        return result
