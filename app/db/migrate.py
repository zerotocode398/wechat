from app.database import get_connection
from app.db.schema import CREATE_TABLES


def init_database():

    conn = get_connection()

    cursor = conn.cursor()

    for sql in CREATE_TABLES:
        cursor.execute(sql)

    conn.commit()

    conn.close()


if __name__ == "__main__":
    init_database()
