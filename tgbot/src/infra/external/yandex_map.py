from typing import (
    Any,
    Tuple,
)

import aiohttp

from .exceptions import (
    InvalidKey,
    NothingFound,
    UnexpectedResponse,
)


class Client:
    __slots__ = ("api_key",)
    api_key: str

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def _request(self, address: str) -> Any:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url="https://geocode-maps.yandex.ru/1.x/",
                    params=dict(format="json", apikey=self.api_key, geocode=address),
            ) as response:
                if response.status == 200:
                    a = await response.json()
                    return a["response"]
                elif response.status == 403:
                    raise InvalidKey()
                else:
                    raise UnexpectedResponse(
                        f"status_code={response.status}, body={response.content}"
                    )

    async def coordinates(self, address: str) -> tuple:
        d = await self._request(address)
        data = d["GeoObjectCollection"]["featureMember"]

        if not data:
            raise NothingFound(f'Nothing found for "{address}" not found')

        coordinates = data[0]["GeoObject"]["Point"]["pos"]
        longitude, latitude = tuple(coordinates.split(" "))
        return longitude, latitude

    async def address(self, longitude, latitude) -> Any:
        response = await self._request(f"{longitude},{latitude}")
        data = response.get("GeoObjectCollection", {}).get("featureMember", [])

        if not data:
            raise NothingFound(f'Nothing found for "{longitude} {latitude}"')

        try:
            address_details = data[0]["GeoObject"]["metaDataProperty"][
                "GeocoderMetaData"
            ]["AddressDetails"]["Country"]
            try:
                locality = address_details["AdministrativeArea"]["Locality"][
                    "LocalityName"
                ]
            except KeyError:
                locality = address_details["AdministrativeArea"][
                    "SubAdministrativeArea"
                ]["Locality"]["LocalityName"]

            return locality
        except KeyError:
            return None
