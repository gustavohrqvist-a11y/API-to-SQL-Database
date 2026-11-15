import mysql.connector
import datetime
from database import connection_to_db
import Jobbtech_api
import tests







conection = tests.test_connection_db()

print(f"kontrollera om databasen är ansluten: {conection}")
print("Kontrollerar API-anslutning...")

tests.test_connection_db()

tests.test_api_connection()


