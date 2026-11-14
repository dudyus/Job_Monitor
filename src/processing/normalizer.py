from datetime import datetime, timezone


def normalize_job(raw, searched_country):
    """Converte o objeto original da API em um formato interno padronizado."""
    restrictions = raw.get("locationRestrictions") or []
    timezone_restrictions = raw.get("timezoneRestrictions") or []

    if restrictions:
        availability = ", ".join(str(country) for country in restrictions)
    else:
        availability = "Worldwide (sem restrição de país informada)"

    pub_date = raw.get("pubDate")
    published_at = None
    if isinstance(pub_date, (int, float)):
        published_at = datetime.fromtimestamp(pub_date, tz=timezone.utc).isoformat()

    return {
        "guid": str(raw.get("guid") or "").strip(),
        "title": str(raw.get("title") or "Título não informado").strip(),
        "company": str(raw.get("companyName") or "Empresa não informada").strip(),
        "searched_country": searched_country,
        "availability": availability,
        "location_restrictions": restrictions,
        "timezone_restrictions": timezone_restrictions,
        "employment_type": raw.get("employmentType"),
        "min_salary": raw.get("minSalary"),
        "max_salary": raw.get("maxSalary"),
        "salary_period": raw.get("salaryPeriod"),
        "currency": raw.get("currency"),
        "application_link": str(raw.get("applicationLink") or "").strip(),
        "published_at": published_at,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }
