
import mysql.connector
import requests
from database import connection_to_db
import streamlit as st


class Job:
    def __init__(self, api_job_id, title, company, location, url):
        self.api_job_id = api_job_id
        self.title = title
        self.company = company
        self.location = location
        self.url = url


def fetch_jobs_from_api():

    api_url = "https://jobsearch.api.jobtechdev.se/search"

    try:
        params = {
            "q": "",
            "limit": 100
        }

        response = requests.get(
            api_url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        return data

    except requests.exceptions.RequestException as error:
        print("Kunde inte hämta jobb från API:", error)
        return None


def convert_api_job_to_object(api_job):

    job = Job(
        api_job_id=api_job["id"],
        title=api_job["headline"],
        company=api_job["employer"]["name"],
        location=api_job["workplace_address"]["city"],
        url=api_job["webpage_url"]
    )

    return job


def commit_job_to_db(job):

    db_connection = None
    cursor = None

    try:
        db_connection = connection_to_db.connect_db()

        if db_connection and db_connection.is_connected():

            cursor = db_connection.cursor()

            # 1. Kontrollera om företaget redan finns
            company_query = """
                SELECT company_id
                FROM companies
                WHERE company_name = %s
            """

            cursor.execute(company_query, (job.company,))
            result = cursor.fetchone()

            # 2. Skapa företaget om det inte finns
            if result:
                company_id = result[0]

            else:
                insert_company_query = """
                    INSERT INTO companies (company_name)
                    VALUES (%s)
                """

                cursor.execute(
                    insert_company_query,
                    (job.company,)
                )

                company_id = cursor.lastrowid

            # 3. Kontrollera om jobbet redan finns
            check_job_query = """
                SELECT api_job_id
                FROM jobs
                WHERE api_job_id = %s
            """

            cursor.execute(check_job_query, (job.api_job_id,))
            existing_job = cursor.fetchone()

            # 4. Spara jobbet om det inte redan finns
            if not existing_job:

                insert_job_query = """
                    INSERT INTO jobs
                    (api_job_id, title, company_id, location, url)
                    VALUES (%s, %s, %s, %s, %s)
                """

                job_data = (
                    job.api_job_id,
                    job.title,
                    company_id,
                    job.location,
                    job.url
                )

                cursor.execute(insert_job_query, job_data)

                db_connection.commit()

                print("Jobb sparat:", job.title)

            else:
                print("Jobbet finns redan:", job.title)

        else:
            print("Kunde inte ansluta till databasen.")

    except mysql.connector.Error as error:

        if db_connection and db_connection.is_connected():
            db_connection.rollback()

        print("Fel vid databasoperation:", error)

    finally:

        if cursor:
            cursor.close()

        if db_connection and db_connection.is_connected():
            db_connection.close()


# Hämta jobb från API
data = fetch_jobs_from_api()

if data and "hits" in data:

    for api_job in data["hits"]:

        try:
            job = convert_api_job_to_object(api_job)
            commit_job_to_db(job)

        except (KeyError, TypeError) as error:
            print("Kunde inte behandla jobb:", error)

else:
    print("Kunde inte hämta jobb från API.")



def fetch_and_store_jobs(search_query):

    url = "https://jobsearch.api.jobtechdev.se/search"
    params = {"q": search_query, "limit": 100}
    response = requests.get(url, params=params)