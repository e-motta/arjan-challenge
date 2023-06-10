import pandas as pd
import asyncio

import api
import models
import service
from json_mock import json


# def main() -> None:
#     # response = api.get_population_detail("BRA")
#     # json = response.json()
#     data = json["data"]
#     # keys = [key for key in data.keys()]
#     # print(keys)
#     df = pd.DataFrame(data)
#     print(df.head)
#     print(df.columns)
#     print(df.files.iloc[0])


async def main_two() -> None:
    countries = ["BRA", "USA", "RUS", "CAN", "AUS", "POL"]
    data = await asyncio.gather(
        *[api.get_population_detail(country) for country in countries]
    )
    print(data)


async def main_three() -> None:
    pop = await service.get_country_population("POL")
    print(pop)


def main_four() -> None:
    p = models.query_countries_by_codes(["BRA", "POL", "FRA"])
    print(p)


async def main_five() -> None:
    c = await service.get_countries(["BRA", "POL", "USA"])
    c_df = await service.get_countries_as_df(["BRA", "POL", "USA"])
    p = service.get_populations_as_df([country.id for country in c])
    print(c, c_df, p)


if __name__ == "__main__":
    # asyncio.run(main_two())
    # main()
    # asyncio.run(main_three())
    asyncio.run(main_five())
