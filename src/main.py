import pandas as pd
import requests 
import os
from pathlib import Path
from dotenv import load_dotenv


#Load environment

load_dotenv()

base_url = os.getenv("API_URL")

#Calling API
def get_info(url):
    
    
    try:
        response = requests.get(url, timeout=30)
        
        
        response.raise_for_status()

        api_data = response.json()
        return api_data

    except requests.exceptions.Timeout:
        print("The API request timed out.")
        raise

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise

get_data = get_info(base_url)

#Extracting data
rows = []
columns = ["date","base","quote","rate"]

for data in get_data:
    date = data["date"]
    base = data["base"]
    quote = data["quote"]
    rate = data["rate"]
    
    active_rows = (date,base,quote,rate)

    rows.append(active_rows)
    
#Pandas Dataframe
df = pd.DataFrame(rows,columns=columns)

#Formatting columns
df["date"] = pd.to_datetime(df["date"])
df["rate"] = pd.to_numeric(df["rate"])
df["base"] = df["base"].str.upper()
df["quote"] = df["quote"].str.upper()

#Sort by date

df = df.sort_values(by=["base", "date"])

df = df.reset_index(drop=True)

#Show results
print("\nExchange Rate Data:")
print(df.head(10))

print("\nDataset Information:")
df.info()

print("\nNumber of Records:", len(df))


#Checking for null values
print("\nMissing Values:")
print(df.isnull().sum())

#Checking for duplicate records 
print("\nNumber of Duplicates:")
print(df.duplicated().sum())

#Date Range
print("\nDate Coverage:")
print("Start Date:", df["date"].min())
print("End Date:", df["date"].max())

#Export to csv to raw data folder

output_folder = Path("data")

output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "exchange_rates.csv"

df.to_csv(output_file, index=False)

print("\n Data has been Exported to:",output_file)