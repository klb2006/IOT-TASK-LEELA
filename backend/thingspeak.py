import requests
from typing import Optional, Dict, Any
from datetime import datetime

# ThingSpeak Configuration
THINGSPEAK_CHANNEL_ID = "3290444"
THINGSPEAK_API_KEY = "AWP8F08WA7SLO5EQ"
THINGSPEAK_BASE_URL = "https://api.thingspeak.com/channels"

class ThingSpeakClient:
    """Client to interact with ThingSpeak API"""
    
    def __init__(self, channel_id: str, api_key: str):
        self.channel_id = channel_id
        self.api_key = api_key
        self.base_url = f"{THINGSPEAK_BASE_URL}/{channel_id}"
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the latest data from ThingSpeak channel
        Returns a dictionary with field1, field2, field3, field4 and timestamp
        """
        try:
            url = f"{self.base_url}/feeds.json"
            params = {
                'api_key': self.api_key,
                'results': 1
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('feeds') and len(data['feeds']) > 0:
                feed = data['feeds'][0]
                return {
                    'distance': float(feed.get('field1', 0)),
                    'temperature': float(feed.get('field2', 0)),
                    'water_percentage': float(feed.get('field3', 0)),
                    'water_liters': float(feed.get('field4', 0)),
                    'timestamp': feed.get('created_at'),
                    'entry_id': feed.get('entry_id')
                }
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from ThingSpeak: {e}")
            return None
    
    def get_multiple_data(self, results: int = 100) -> Optional[list]:
        """
        Fetch multiple recent data points from ThingSpeak
        """
        try:
            url = f"{self.base_url}/feeds.json"
            params = {
                'api_key': self.api_key,
                'results': min(results, 1000)  # ThingSpeak max is 1000
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('feeds'):
                feeds = []
                for feed in data['feeds']:
                    feeds.append({
                        'distance': float(feed.get('field1', 0)),
                        'temperature': float(feed.get('field2', 0)),
                        'water_percentage': float(feed.get('field3', 0)),
                        'water_liters': float(feed.get('field4', 0)),
                        'timestamp': feed.get('created_at'),
                        'entry_id': feed.get('entry_id')
                    })
                return feeds
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from ThingSpeak: {e}")
            return None

def get_thingspeak_client() -> ThingSpeakClient:
    """Factory function to get ThingSpeak client"""
    return ThingSpeakClient(THINGSPEAK_CHANNEL_ID, THINGSPEAK_API_KEY)
