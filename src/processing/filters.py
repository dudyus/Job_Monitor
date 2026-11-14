"""Filtros iniciais para oportunidades de Dados/BI em nível júnior ou inicial."""

POSITIVE_TERMS = (
    "data analyst",
    "junior data",
    "jr data",
    "bi analyst",
    "business intelligence",
    "reporting analyst",
    "analytics analyst",
    "analyst, data",
)

SENIOR_TERMS = (
    "senior", "sr.", "sr ", "lead", "manager", "director",
    "principal", "staff", "head of", "coordinator",
)


def is_relevant(job):
    title = (job.get("title") or "").lower().strip()
    if not any(term in title for term in POSITIVE_TERMS):
        return False
    if any(term in title for term in SENIOR_TERMS):
        return False
    return True
