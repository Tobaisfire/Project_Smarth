import requests
import pandas as pd
import dotenv
import os
import logging
from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv("DATA_GOV_API_KEY")
print(API_KEY)
RESOURCE_ID_RAINFALL = os.getenv("RESOURCE_ID_RAINFALL")
RESOURCE_ID_CROP_PRODUCTION = os.getenv("RESOURCE_ID_CROP_PRODUCTION")

class DataFetchAPI: 
    def __init__(self, api_key, resource_id_rainfall, resource_id_crop_production):
        self.api_key = api_key
        self.resource_id_rainfall = resource_id_rainfall
        self.resource_id_crop_production = resource_id_crop_production

    def get_rainfall_data(self,limit=100):
        url = f"https://api.data.gov.in/resource/{self.resource_id_rainfall}?api-key={self.api_key}&format=json&offset=0&limit={limit}"
        logging.info(f"Fetching rainfall data with limit {limit}")
        r = requests.get(url)
        if r.status_code != 200:
            logging.error(f"Failed to fetch rainfall data with limit {limit}")
            return None
        logging.info(f"Successfully fetched rainfall data with limit {limit}")
        data = r.json()
        df = pd.DataFrame(data['records'])
        return df
    
    def get_crop_production_data(self,limit=100):
        url = f"https://api.data.gov.in/resource/{self.resource_id_crop_production}?api-key={API_KEY}&format=json&offset=0&limit={limit}"
        logging.info(f"Fetching crop production data with limit {limit}")
        r = requests.get(url)
        if r.status_code != 200:
            logging.error(f"Failed to fetch crop production data with limit {limit}")
            return None
        logging.info(f"Successfully fetched crop production data with limit {limit}")
        data = r.json()
        df = pd.DataFrame(data['records'])
        return df
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    data_fetch_api = DataFetchAPI(API_KEY, RESOURCE_ID_RAINFALL, RESOURCE_ID_CROP_PRODUCTION)
    print("Fecth rain fall data press 1 and for crop production press 2")
    choice = input("Enter your choice: ")
    if choice == "1":
        limit = input("Enter the limit: ")
        rainfall_data = data_fetch_api.get_rainfall_data(limit=10)
        logging.info(f"Rainfall data: {rainfall_data.head()}")
    elif choice == "2":
        limit = input("Enter the limit: ")
        crop_production_data = data_fetch_api.get_crop_production_data(limit=10)
        logging.info(f"Crop production data: {crop_production_data.head()}")
    else:
        logging.error("Invalid choice")