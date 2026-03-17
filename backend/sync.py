"""
Integration script to fetch data from ThingSpeak and store in PostgreSQL database
"""
from thingspeak import get_thingspeak_client
from main import insert_sensor_data, create_sensor_data_table, get_latest_sensor_data
import time

def fetch_and_store_latest():
    """
    Fetch the latest data from ThingSpeak and store it in the database
    Only stores if it's NEW data (different entry_id or different values)
    """
    from main import get_latest_sensor_data
    
    print("Fetching latest data from ThingSpeak...")
    
    client = get_thingspeak_client()
    data = client.get_latest_data()
    
    if data:
        # Get last stored data from database
        last_stored = get_latest_sensor_data()
        
        # Check if this is NEW data (different entry_id or different values)
        is_new_data = False
        
        if last_stored is None:
            is_new_data = True
        elif last_stored['entry_id'] != data['entry_id']:
            is_new_data = True
        elif (last_stored['distance'] != data['distance'] or 
              last_stored['temperature'] != data['temperature'] or
              last_stored['water_percentage'] != data['water_percentage'] or
              last_stored['water_liters'] != data['water_liters']):
            is_new_data = True
        
        if is_new_data:
            print("[NEW] NEW data from ThingSpeak (entry_id: " + str(data['entry_id']) + "):")
            print("  - Distance: " + str(data['distance']))
            print("  - Temperature: " + str(data['temperature']) + "C")
            print("  - Water %: " + str(data['water_percentage']) + "%")
            print("  - Water Liters: " + str(data['water_liters']) + "L")
            print("  - Timestamp: " + str(data['timestamp']))
            
            # Insert into database
            success = insert_sensor_data(
                distance=data['distance'],
                temperature=data['temperature'],
                water_percentage=data['water_percentage'],
                water_liters=data['water_liters'],
                timestamp=data['timestamp'],
                entry_id=data['entry_id']
            )
            
            if success:
                print("[OK] Data stored successfully!")
                return True
            else:
                print("[ERROR] Failed to store data")
                return False
        else:
            print("[SKIP] No new data (same as last sync)")
            return True
    else:
        print("[ERROR] Failed to fetch data from ThingSpeak")
        return False

def fetch_and_store_bulk(count: int = 100):
    """
    Fetch multiple recent data points from ThingSpeak and store them
    """
    print(f"Fetching {count} data points from ThingSpeak...")
    
    client = get_thingspeak_client()
    feeds = client.get_multiple_data(count)
    
    if feeds:
        print("[OK] Got " + str(len(feeds)) + " data points from ThingSpeak")
        
        success_count = 0
        for data in feeds:
            success = insert_sensor_data(
                distance=data['distance'],
                temperature=data['temperature'],
                water_percentage=data['water_percentage'],
                water_liters=data['water_liters'],
                timestamp=data['timestamp'],
                entry_id=data['entry_id']
            )
            if success:
                success_count += 1
        
        print("[OK] Successfully stored " + str(success_count) + "/" + str(len(feeds)) + " records")
        return True
    else:
        print("[ERROR] Failed to fetch data from ThingSpeak")
        return False

def continuous_sync(interval: int = 300):
    """
    Continuously fetch data from ThingSpeak and store in database
    interval: time in seconds between fetches (default 5 minutes)
    """
    print(f"Starting continuous sync (interval: {interval}s)...")
    
    # Create table on first run
    create_sensor_data_table()
    
    try:
        while True:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print("\n[" + timestamp + "] Syncing data...")
            fetch_and_store_latest()
            print("Next sync in " + str(interval) + "s...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[OK] Sync stopped by user")

if __name__ == "__main__":
    # Create table
    create_sensor_data_table()
    
    print("\n" + "=" * 60)
    print("[START] STARTING AUTO-UPLOAD SERVER")
    print("=" * 60)
    print("Will fetch new data every 60 seconds (1 minute)")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    # Run continuous sync - fetches data every 60 seconds
    continuous_sync(interval=60)
