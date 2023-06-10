import requests
import asyncio
from typing import Dict


BASE_URL = "https://countriesnow.space/api/v0.1/countries/population"


def _http_get_sync(url: str):
    response = requests.get(url)
    return response.json()


def _http_post_sync(url: str, payload: Dict[str, str]):
    response = requests.post(url, data=payload)
    return response.json()


async def _http_get(url: str):
    return await asyncio.to_thread(_http_get_sync, url)


async def _http_post(url: str, payload: Dict[str, str]):
    return await asyncio.to_thread(_http_post_sync, url, payload)


async def get_data():
    return await _http_get(BASE_URL)


# async def get_population():
#     return await _http_get(f"{BASE_URL}/pop")


async def get_population_detail(country_code: str):
    json = await _http_post(BASE_URL, {"iso3": country_code})
    if json["error"]:
        json["data"]["iso3"] = country_code
    return json
