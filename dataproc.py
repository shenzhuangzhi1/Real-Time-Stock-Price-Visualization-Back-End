import requests
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from operator import itemgetter

# API Configuration
API_KEY = 'JNUH9JAUELBAPS9S'  
BASE_URL = 'https://www.alphavantage.co/query'

# Cache Configuration
CACHE_DIR = "./resources/cache"  # Directory to store cache files
CACHE_TTL = timedelta(minutes=60)  # Time-to-live for cache

# Ensure the cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def fetchStockData(symbol, interval='5min'):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': interval,
        'apikey': API_KEY,
        'outputsize': 'compact'  # 'compact' or 'full'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        # Check for API errors
        if "Error Message" in data:
            raise ValueError(f"Error fetching data: {data['Error Message']}")
        elif "Note" in data:
            raise ValueError(f"API limit reached: {data['Note']}")
        return data
    else:
        raise Exception(f"API call failed: {response.status_code}")

def dataCacher(symbol, interval, data):
    filename = os.path.join(CACHE_DIR, f"{symbol}_{interval}_data.json")
    cache_entry = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    with open(filename, "w") as file:
        json.dump(cache_entry, file)

def cachedDataLoader(symbol, interval):
    filename = os.path.join(CACHE_DIR, f"{symbol}_{interval}_data.json")
    if not os.path.exists(filename):
        return None

    with open(filename, "r") as file:
        cache_entry = json.load(file)

    # Check if cache is still valid
    cache_time = datetime.fromisoformat(cache_entry["timestamp"])
    if datetime.now() - cache_time < CACHE_TTL:
        return cache_entry["data"]  # Return cached data if valid
    else:
        return None  # Cache expired

def retrieveStockData(symbol, interval='5min'):
    cached_data = cachedDataLoader(symbol, interval)
    if cached_data:
        print(f"Using cached data for {symbol} at interval {interval}")
        data = cached_data
    else:
        print(f"Fetching fresh data for {symbol} at interval {interval}")
        data = fetchStockData(symbol, interval)
        dataCacher(symbol, interval, data)
    return data

