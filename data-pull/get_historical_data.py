# Built from a program found on the page of github.com/mickbransfield
# 05/29/2025
# github.com/drakesprojects

import os
import sys
from pathlib import Path
import requests
import pandas as pd
from datetime import date, timedelta
from tqdm import tqdm

def main():
    # Parse directory for dataset
    my_path = Path(os.environ["DATASET_DIRECTORY"])
    
    # ensure directory exists
    if not my_path.is_dir():
        print(f"Directory does not exist: {my_path}")
        sys.exit(1)

    # If kalshi-historical exists, find the latest date stored and that +1 day is where we start our query
    sdate = date(2021, 6, 30)
    my_path = my_path / "kalshi-historical"
    try:
        if my_path.is_dir():
            years = [int(d.name) for d in my_path.iterdir() if d.is_dir() and d.name.isdigit()]
            my_path2 = my_path / str(max(years))
            months = [int(d.name) for d in my_path2.iterdir() if d.is_dir() and d.name.isdigit()]
            my_path3 = my_path2 / str(max(months))
            files = list(my_path3.glob("*.csv"))
            if files:
                latest = max(files, key=lambda p: int(p.stem.rsplit("-", 1)[-1]))
                sdate = date(max(years), max(months), int(latest.stem.rsplit("-", 1)[-1])) + timedelta(days=1)
            else:
                raise Exception("Month directory has no files")
    except Exception as e:
        print(f"Error parsing historical data: {e}", file=sys.stderr)
        sys.exit(2)

    # Set dates to be collected
    yesterday = date.today() - timedelta(days=1)
    if (yesterday <= sdate):
        print("All up to date")
        sys.exit(0)
    daterange = pd.date_range(sdate, yesterday).strftime('%Y-%m-%d').tolist()

    # Loop through list of dates
    for ds in tqdm(daterange):
        # Pull in market data 
        base_url = "https://kalshi-public-docs.s3.amazonaws.com/reporting/market_data_"
        end_url = ".json"
        URL = base_url + str(ds) + end_url
        response = requests.get(URL)
        if not response.ok:
            print(f"Error fetching {URL}, terminating program...")
            sys.exit(3)
        jsondata = response.json()

        # Convert JSON to dataframe
        df = pd.DataFrame(jsondata)

        # Create location for data to be stored
        outdir = my_path / str(ds.split("-")[0]) / str(ds.split("-")[1])
        outdir.mkdir(parents=True, exist_ok=True)

        # Write out to local directory
        filepath = outdir / f"kalshi_{ds}.csv"
        df.to_csv(filepath, sep=',', encoding='utf-8', header=True)

if __name__ == "__main__":
    main()
