import sqlite3
from pathlib import Path


class JobRepository:
    def __init__(self, database_path):
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                guid TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT,
                searched_country TEXT,
                availability TEXT,
                employment_type TEXT,
                min_salary REAL,
                max_salary REAL,
                salary_period TEXT,
                currency TEXT,
                application_link TEXT,
                published_at TEXT,
                collected_at TEXT,
                notified INTEGER NOT NULL DEFAULT 0
            )
        """)
        self.connection.commit()

    def insert_if_new(self, job):
        if not job["guid"]:
            return False

        cursor = self.connection.execute(
            """INSERT OR IGNORE INTO jobs
            (guid, title, company, searched_country, availability,
             employment_type, min_salary, max_salary, salary_period,
             currency, application_link, published_at, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job["guid"], job["title"], job["company"],
                job["searched_country"], job["availability"],
                job["employment_type"], job["min_salary"], job["max_salary"],
                job["salary_period"], job["currency"], job["application_link"],
                job["published_at"], job["collected_at"],
            ),
        )
        self.connection.commit()
        return cursor.rowcount == 1


    def get_pending_notifications(self):
        """Retorna vagas já armazenadas que ainda não foram notificadas."""
        cursor = self.connection.execute(
            """SELECT guid, title, company, searched_country, availability,
                      employment_type, min_salary, max_salary, salary_period,
                      currency, application_link, published_at, collected_at
               FROM jobs WHERE notified = 0 ORDER BY collected_at ASC"""
        )
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def mark_notified(self, guid):
        self.connection.execute(
            "UPDATE jobs SET notified = 1 WHERE guid = ?", (guid,)
        )
        self.connection.commit()

    def close(self):
        self.connection.close()
