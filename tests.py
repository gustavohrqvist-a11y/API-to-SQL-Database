import requests
import mysql.connector
from database.connection_to_db import connect_db





def fetch_jobs_from_api(search_query):
    api_url = "https://jobsearch.api.jobtechdev.se/search"

    params = {
        "q": search_query,
        "limit": 20
    }

    try:
        response = requests.get(api_url, params=params, timeout=15)

        # Kontrollera om svaret är OK
        response.raise_for_status()

        # Omvandla JSON till Python-data
        data = response.json()

        return data

    except requests.exceptions.RequestException as error:
        print("Kunde inte hämta jobb från API:", error)
        return None
    



def test_connection_db():
    try:
        connection = connect_db()
        if connection.is_connected():
            print("Anslutning till databasen lyckades!")
            return True
        else:
            print("Anslutning till databasen misslyckades.")
            return False
    except mysql.connector.Error as error:
        print("Fel vid anslutning till databasen:", error)
        return False





def test_api_connection():
    search_query = "Python"
    jobs_data = fetch_jobs_from_api(search_query)

    if jobs_data is not None:
        print("API-anslutningen fungerar! Antal jobb hämtade:", len(jobs_data.get("hits", [])))
        return True
    else:
        print("Kunde inte hämta jobb från API.")
        return False

# Testa anslutningen
test_connection_db()

# Testa API-anslutningen
test_api_connection()
