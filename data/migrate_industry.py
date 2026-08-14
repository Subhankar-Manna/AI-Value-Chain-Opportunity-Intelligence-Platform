import sqlite3

DB_PATH = "database/retail_ai.db"


def migrate_database():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # ----------------------------------------------
    # 1. Create industries table
    # ----------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS industries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL UNIQUE,
            description TEXT
        )
    """)

    # ----------------------------------------------
    # 2. Check whether industry_id already exists
    # ----------------------------------------------

    cursor.execute("""
        PRAGMA table_info(value_chain_stages)
    """)

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    # ----------------------------------------------
    # 3. Add industry_id if it does not exist
    # ----------------------------------------------

    if "industry_id" not in columns:

        cursor.execute("""
            ALTER TABLE value_chain_stages
            ADD COLUMN industry_id INTEGER
        """)

        print("industry_id column added successfully!")

    else:

        print("industry_id column already exists.")

    connection.commit()
    connection.close()

    print("Industry database migration completed successfully!")


if __name__ == "__main__":
    migrate_database()