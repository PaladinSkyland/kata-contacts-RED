import sys
import sqlite3
from pathlib import Path
from datetime import datetime


class Contacts:
    def __init__(self, db_path):
        self.db_path = db_path
        if not db_path.exists():
            print("Migrating db")
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE contacts(
                  id INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL
                )
              """
            )
            cursor.execute("CREATE UNIQUE INDEX index_contacts_email ON contacts(email);")
            connection.commit()
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row

    def find_contact_with_email(self, email):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT * FROM contacts
            WHERE email = ?
            """,
            (email,),
        )
        return cursor.fetchone()


def insert_many_contacts(num_contacts):
    print("Inserting {num_contacts} contacts ...")
    db_path = Path("contacts.sqlite3")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM contacts")
    contacts = [(f"Name-{i}", f"email-{i}@domain.tld") for i in range(1, num_contacts + 1)]
    cursor.executemany(
        "INSERT INTO contacts (name, email) VALUES (?, ?)", contacts
    )
    connection.commit()
    print("Done")


def main():
    if len(sys.argv) < 2:
        sys.exit("Not enough arguments")
    num_contacts = int(sys.argv[1])
    db_path = Path("contacts.sqlite3")
    

    last_mail = f"email-{num_contacts}@domain.tld"
    contacts = Contacts(db_path)
    insert_many_contacts(num_contacts)
    print("Looking for email", last_mail)

    start = datetime.now()
    result = contacts.find_contact_with_email(f"email-{num_contacts}@domain.tld")
    end = datetime.now()
    elapsed = end - start
    print(f"find_contact_with_email took {elapsed.total_seconds() * 1000:.0f} ms")
    if not result:
        sys.exit(f"contact with email {last_mail} not found")


if __name__ == "__main__":
    main()
