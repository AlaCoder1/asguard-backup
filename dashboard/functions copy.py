import asyncio
import websockets
import paramiko
import time
import sqlite3
from functions import *
import json
# ... Other parts of your code ...

# Initialize WebSocket server
async def data_websocket(websocket, path):
    while True:
        try:
            # Execute the command to monitor CPU and memory usage
            command = "top -bn 1 | awk 'NR==3{print $2}' && free | awk '/Mem/{printf \"%.2f\", $3/$2*100}'"
            output = execute_remote_command(ssh_client, command)
            print("output==",output)
            # Parse the output
            cpu_usage, memory_usage = map(float, output)
            
            # Get the current timestamp
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            unix_timestamp = int(time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")))
            
            # Insert data into the database with removal of old data logic
            insert_data_into_database(unix_timestamp, cpu_usage, memory_usage)
            
            # Broadcast the data to connected WebSocket clients
            data = {
                "timestamp": unix_timestamp,
                "cpu_percentage": cpu_usage,
                "memory_percentage": memory_usage,
            }
            await websocket.send(json.dumps(data))
            
            # Sleep for a while before collecting and broadcasting again
            await asyncio.sleep(5)  # Adjust the interval as needed
            
        except Exception as e:
            print(f"Error: {str(e)}")

# ... Rest of your code ...

if __name__ == "__main__":
    # ... Rest of your main() function ...
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(data_websocket, "0.0.0.0", 8765)
    )
    asyncio.get_event_loop().run_forever()