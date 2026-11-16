import pandas as pd
import requests 
import os
from pathlib import Path
from mysql import connector
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

#Server Connection
SQL_HOST = os.getenv("SQL_HOST")
SQL_PORT = os.getenv("SQL_PORT")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DATABASE = os.getenv("SQL_DB")

server_connection = connector.connect(
    host=SQL_HOST,
    port=SQL_PORT,
    user=SQL_USER,
    password=SQL_PASSWORD,
    connection_timeout=10,
    autocommit=False,
    raise_on_warnings=True
)

server_cursor = server_connection.cursor()
print(f"You have connected to MySQL server!")
server_cursor.close()
server_connection.close()

db_connection = connector.connect(
    host=SQL_HOST,
    port=SQL_PORT,
    user=SQL_USER,
    password=SQL_PASSWORD,
    database=SQL_DATABASE

)
db_cursor = db_connection.cursor()
print(f"You have connected to Database")

#Insert Data to MySQL

insert_query = """
INSERT INTO exchange_rates (date, base, quote, rate)
VALUES (%s, %s, %s, %s)
"""

records = [
    (
        row.date.to_pydatetime(),
        row.base,
        row.quote,
        float(row.rate)
    )
    for row in df.itertuples(index=False)
]

db_cursor.executemany(insert_query, records)

db_connection.commit()

print(f"{db_cursor.rowcount} records inserted successfully!")

# Close Database Connection

db_cursor.close()
db_connection.close()