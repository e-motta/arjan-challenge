import asyncio
import pandas as pd
from typing import Any, Dict, List
import json

from api import get_population_detail
from models import (
    Country,
    Population,
    query_countries_by_codes,
    query_populations_by_country_ids,
)


async def parse_api_data(json: Dict[Any, Any]):
    data = json["data"]
    errors: List[str] = []

    if json["error"]:
        errors.append(data["iso3"])

    country = Country(data["country"], data["iso3"])
    country.save()

    populations: List[Population] = []
    for count in data["populationCounts"]:
        population = Population(count["year"], count["value"])
        population.country_id = country.id
        population.save()
        populations.append(population)

    return {"country": country, "populations": populations, "errors": errors}


async def get_countries(country_codes: List[str]):
    db_countries, db_not_found = query_countries_by_codes(country_codes)

    api_data = await asyncio.gather(
        *[get_population_detail(code) for code in db_not_found]
    )

    api_countries: List[Country] = []
    for country in api_data:
        data = await parse_api_data(country)
        country_data = data["country"]
        api_countries.append(country_data)  # type: ignore

    return db_countries + api_countries


async def get_countries_as_df(country_codes: List[str]):
    countries_list = await get_countries(country_codes)
    countries_dict = {
        "id": [country.id for country in countries_list],
        "name": [country.name for country in countries_list],
        "iso3": [country.iso3 for country in countries_list],
    }
    return pd.DataFrame(countries_dict)


def get_populations(country_ids: List[int]):
    return query_populations_by_country_ids(country_ids)


def get_populations_as_df(country_ids: List[int]):
    populations_list = get_populations(country_ids)
    populations_dict = {
        "id": [pop.id for pop in populations_list],
        "country_id": [pop.country_id for pop in populations_list],
        "year": [pop.year for pop in populations_list],
        "population": [pop.population for pop in populations_list],
    }
    return pd.DataFrame(populations_dict)


def join_population_and_countries_for_plotting_df(
    countries_df: pd.DataFrame, populations_df: pd.DataFrame
):
    df = pd.merge(countries_df, populations_df, left_on="id", right_on="country_id")
    df["Country"] = df["name"]
    return df


def get_countries_rel():
    with open("countries_iso3.json", "r") as file:
        countries = json.load(file)
        countries_rel = [
            {"label": country["name"], "value": country["code"]}
            for country in countries
        ]
    return countries_rel
