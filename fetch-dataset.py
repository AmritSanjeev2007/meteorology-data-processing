# pyright: standard

""" This is a standalone executable for fetching the dataset from the API. Since the dataset musn't be fetch too often, a 
separate executable for fetching the dataset is more appropriate than fetching the dataset on every run. """


import cdsapi
import copy
import json
import os
import sys

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, NoReturn

from src.constants import TEMPERATURE_DATASET, TEMPERATURE_REQUEST, TEMPERATURE_SAVE_FILE


def fetch_datasets(url: str, api_key: str, date: datetime) -> None:
    """ Fetches data from the meteorological API. It requests the temperature and wind datasets. 
    
    The `url` is the specific API service url tied to your CDS account. Both,  the ``url`` and 
    the ``api_key`` can be viewed at https://cds.climate.copernicus.eu/profile (if you have an
    account). """
    
    client = cdsapi.Client(
        url=url,
        key=api_key,
    )

    current_time = datetime.now()

    if TEMPERATURE_SAVE_FILE.exists():
        _3_DAYS_IN_SECONDS = 259_200
        is_too_soon = (current_time.timestamp() - os.path.getmtime(TEMPERATURE_SAVE_FILE)) < _3_DAYS_IN_SECONDS

        if is_too_soon:
            should_download = "y" in input(
                f"A temperature dataset was already downloaded at {TEMPERATURE_SAVE_FILE},"
                "do you want to download a new one? (y/N): "
            )

            if not should_download:
                return

    temperature_request = copy.deepcopy(TEMPERATURE_REQUEST)
    temperature_request.update({
        "year": [f"{date.year}"],
        "month": [f"{date.month:02d}"],
    })

    print(f"Requesting the temperature dataset via the following request info: {json.dumps(temperature_request, indent=4)}")

    client.retrieve(
        name=TEMPERATURE_DATASET,
        request=temperature_request,
        target=str(TEMPERATURE_SAVE_FILE),
    )


def main(argv: list[str]) -> NoReturn:

    if len(argv) < 3:
        print("The usage is: py fetch-dataset.py <url> <api_key>")
        exit(-1)

    print(f"API service URL = {argv[1]}")
    print(f"Client API key = {argv[2]}")

    fetch_datasets(url=argv[1], api_key=argv[2], date=datetime(year=2026, month=5, day=1))
    exit(0)

if __name__ == "__main__":
    main(sys.argv)
