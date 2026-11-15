
import mysql.connector
import requests
import json
from database import connection_to_db


class Job:
    def __init__(self, api_job_id, title, company, location, url):
        self.api_job_id = api_job_id
        self.title = title
        self.company = company
        self.location = location
        self.url = url




import requests


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




def convert_api_job_to_object(api_job):
    # Omvandla API-data till ett Job-objekt
    return Job(
        api_job_id=api_job["id"],
        title=api_job["headline"],
        company=api_job["employer"]["name"],
        location=api_job["workplace_address"]["city"],
        url=api_job["webpage_url"]
    )














def save_job_to_db(job):
    connection = connection_to_db.connect_db()

    if connection is None:
        print("Kunde inte ansluta till databasen.")
        return

    cursor = None

    try:
        cursor = connection.cursor()

        # 1. Kontrollera om företaget redan finns
        company_query = """
            SELECT company_id
            FROM companies
            WHERE company_name = %s
        """

        cursor.execute(company_query, (job.company,))
        company_result = cursor.fetchone()

        # 2. Skapa företaget om det inte finns
        if company_result is None:

            insert_company = """
                INSERT INTO companies (company_name)
                VALUES (%s)
            """

            cursor.execute(insert_company, (job.company,))

            company_id = cursor.lastrowid

            print(f"Företaget {job.company} har skapats!")

        else:
            company_id = company_result[0]

            print(f"Företaget finns redan. ID: {company_id}")

        # 3. Kontrollera om jobbet redan finns
        check_query = """
            SELECT job_id
            FROM jobs
            WHERE api_job_id = %s
        """

        cursor.execute(check_query, (job.api_job_id,))
        existing_job = cursor.fetchone()

        if existing_job is not None:
            print("Jobbet finns redan i databasen.")
            return

        # 4. Spara jobbet med rätt company_id
        insert_job = """
            INSERT INTO jobs
            (api_job_id, title, location, url, company_id)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            job.api_job_id,
            job.title,
            job.location,
            job.url,
            company_id
        )

        cursor.execute(insert_job, values)

        # 5. Spara ändringarna
        connection.commit()

        print(f"Jobbet '{job.title}' har sparats!")
        print(f"Företag: {job.company}")
        print(f"Company ID: {company_id}")

    except mysql.connector.Error as error:
        connection.rollback()
        print("Fel vid databasoperation:", error)

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()






jobs_data = fetch_jobs_from_api("python")

if jobs_data:

    first_job = jobs_data["hits"][0]

    print("Jobb-ID:", first_job["id"])
    print("Titel:", first_job["headline"])
    print("Företag:", first_job["employer"]["name"])
    print("Plats:", first_job["workplace_address"]["city"])
    print("Länk:", first_job["webpage_url"])




save_job_to_db()




