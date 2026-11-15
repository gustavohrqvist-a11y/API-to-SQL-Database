import mysql.connector
import os
from dotenv import load_dotenv

# Hämta .env från samma mapp som denna fil
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, "Lösen.env")

load_dotenv(ENV_FILE, override=True)

# Läs in inställningarna
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "3306")


def connect_db():
    try:
      #  print("Använder databas:", DB_NAME)
       # print("Användare:", DB_USER)
        #print("Lösenord finns:", bool(DB_PASSWORD))

        connection = mysql.connector.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connection_timeout=10
        )

        print("Ansluten till databasen!")
        return connection

    except mysql.connector.Error as error:
        print("Databasfel:", error)
        return None