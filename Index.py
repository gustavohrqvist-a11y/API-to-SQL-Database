import mysql.connector
import connection_to_db


def test_connection():
    db_connection = None

    try:
        db_connection = connection_to_db.connect_db()

        if db_connection and db_connection.is_connected():
            print("Databasanslutningen fungerar!")

            cursor = db_connection.cursor()
            cursor.execute("SELECT 1")

            result = cursor.fetchone()
            print("SQL-test lyckades:", result)

            cursor.close()
            return True

        else:
            print("Kunde inte ansluta till databasen.")
            return False

    except mysql.connector.Error as error:
        print("Fel vid databastest:", error)
        return False

    finally:
        if db_connection and db_connection.is_connected():
            db_connection.close()


# Testa anslutningen
test_connection()