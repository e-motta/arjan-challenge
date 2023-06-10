import sqlite3
from contextlib import contextmanager
from typing import Any
from dataclasses import dataclass, field


@contextmanager
def db_manager(database: str, *args: Any, **kwargs: Any):
    conn = sqlite3.connect(database, *args, **kwargs)
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


@dataclass
class Model:
    id: int = field(repr=False, init=False)
    table_name: str = field(repr=False, init=False)

    def save(self):
        values = [attr for attr in vars(self).values()]
        fields = ", ".join(vars(self).keys())
        placeholders = ", ".join(["?"] * len(vars(self).keys()))

        with db_manager("database.db") as cursor:
            # TODO: add condition: insert only swhen not exists
            cursor.execute(
                f"""--sql
                INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders});
                """,
                (values),
            )
            self.id = cursor.lastrowid


@dataclass
class Population(Model):
    country_id: int = field(repr=False, init=False)

    year: int
    population: int

    table_name = "populations"


@dataclass
class Country(Model):
    name: str
    iso3: str

    # populations: list[Population] = field(repr=False, init=False)

    table_name = "countries"


def migrate():
    with db_manager("database.db") as cursor:
        cursor.execute(
            """--sql
            CREATE TABLE IF NOT EXISTS countries (
                id INTEGER PRIMARY KEY,
                name TEXT,
                iso3 TEXT
            );
            """
        )

    with db_manager("database.db") as cursor:
        cursor.execute(
            """--sql
            CREATE TABLE IF NOT EXISTS populations (
                id INTEGER PRIMARY KEY,
                country_id INTEGER,
                year INTEGER,
                population INTEGER,
                FOREIGN KEY (country_id) REFERENCES countries(id)
            );
            """
        )


def query_country_by_code(country_code: str):
    with db_manager("database.db") as cursor:
        query = cursor.execute(
            f"""--sql
            SELECT * FROM countries WHERE iso3 = '{country_code}';
            """
        )
        data = query.fetchone()
        if data:
            country = Country(*data[1:])
            country.id = data[0]
            return country


def query_countries_by_codes(country_codes: list[str]):
    country_codes = [code.upper() for code in country_codes]

    with db_manager("database.db") as cursor:
        placeholders = ", ".join(["?"] * len(country_codes))

        query = cursor.execute(
            f"""--sql
            SELECT * FROM countries WHERE iso3 in ({placeholders});
            """,
            (country_codes),
        )

        data = query.fetchall()

        countries = []

        for row in data:
            country = Country(*row[1:])
            country.id = row[0]
            countries.append(country)

        not_found = [
            code
            for code in country_codes
            if code not in [country.iso3 for country in countries]
        ]

        return countries, not_found


def query_populations_by_country_ids(country_ids: list[int]):
    with db_manager("database.db") as cursor:
        placeholders = ", ".join(["?"] * len(country_ids))

        query = cursor.execute(
            f"""--sql
            SELECT * FROM populations WHERE country_id IN ({placeholders});
            """,
            country_ids,
        )

        data = query.fetchall()
        populations = []

        for row in data:
            population = Population(*row[2:])
            population.id = row[0]
            population.country_id = row[1]
            populations.append(population)

        return populations


def delete_country_by_id(id: int):
    with db_manager("database.db") as cursor:
        cursor.execute(
            f"""--sql
            DELETE FROM countries WHERE id = '{id}';
            """
        )


if __name__ == "__main__":
    migrate()
