
import mysql.connector
import requests
import json
from database.connection_to_db import connect_db


class Company:
    def __init__(self, company_name, company_website=None):
        self.company_name = company_name
        self.company_website = company_website

    def display_info(self):
        print(f"Company: {self.company_name}")
        print(f"Website: {self.company_website}")


def add_company():

    answer_name = input("Register Company: ")
    answer_website = input("Company Website (optional): ")

    company = Company(answer_name, answer_website or None)

    conn = connect_db()

    if conn is None:
        print("Could not connect to Database")
        return

    cursor = None

    try:
        cursor = conn.cursor()

        sql = """
        INSERT INTO companies (company_name, company_website)
        VALUES (%s, %s)
        """

        cursor.execute(
            sql,
            (company.company_name, company.company_website)
        )

        conn.commit()

        print("Company has been added to the database.")

    except mysql.connector.Error as error:
        print("Database error:", error)
        conn.rollback()

    finally:
        if cursor:
            cursor.close()
        conn.close()


add_company()
