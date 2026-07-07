from sqlalchemy import text

from database.postgres import engine


def check_database():

    try:

        with engine.connect() as conn:

            conn.execute(text("SELECT 1"))

        return True

    except Exception:

        return False