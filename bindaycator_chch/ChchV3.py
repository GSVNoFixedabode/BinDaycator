import requests
import os
import json
import machine
import time
import ntptime
import network


def query_api():
    # API URL
    url = 'https://www.ccc.govt.nz/services/rubbish-and-recycling/collections/getProperty?ID=82918'
    
    response = requests.get(url).text
    
    if response.status_code == 200:
        data = response.json()
        
        # Filter upcoming collections
        upcoming_collections = [collection for collection in data['bins']['collections'] if collection['out_of_date'] == 'False']
        
        # Initialize a variable to track the earliest date and type
        earliest_date = '9999-12-31'  # Placeholder for comparison
        earliest_collection_type = None
        
        for collection in upcoming_collections:
            if collection['next_planned_date'] < earliest_date:
                earliest_date = collection['next_planned_date']
                earliest_collection_type = collection['material']
        
        if earliest_collection_type:
            print(f"The next bin to be collected is for {earliest_collection_type} on {earliest_date}.")
        else:
            print("No upcoming collections found.")
        
        response.close()
    else:
        print("Failed to retrieve data from the API.")

if __name__ == "__main__":
    query_api()