import paramiko
import time
import sqlite3
import matplotlib.pyplot as plt
import mysql.connector

# # Connect to the MySQL database
# db = mysql.connector.connect(
#     host="localhost", 
#     user="root",
#     password="",
#     database="amouna"
# )
# cursor = db.cursor()
# Initialize SQLite database connection
conn = sqlite3.connect("monitoring_data.db")
cursor = conn.cursor()

# Create a table to store monitoring data if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS monitoring_data (
        timestamp INTEGER,
        cpu_percentage REAL,
        memory_percentage REAL
    )
""")
conn.commit()

def execute_remote_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    return stdout.readlines()

def insert_data_into_database(timestamp, cpu_usage, memory_usage):
    # Remove old data if the number of entries exceeds 20
    cursor.execute("SELECT COUNT(*) FROM monitoring_data")
    count = cursor.fetchone()[0]
    if count >= 20:
        cursor.execute("DELETE FROM monitoring_data WHERE timestamp = (SELECT MIN(timestamp) FROM monitoring_data)")
    cursor.execute("INSERT INTO monitoring_data (timestamp, cpu_percentage, memory_percentage) VALUES (?, ?, ?)",
                   (timestamp, cpu_usage, memory_usage))
    conn.commit()


def plot_data():
    cursor.execute("SELECT timestamp, cpu_percentage, memory_percentage FROM monitoring_data ORDER BY timestamp DESC")
    data = cursor.fetchall()
    data = data[:100]  # Get the last 20 data points
    timestamps, cpu_percentages, memory_percentages = zip(*data)

    # Create the CPU and memory usage plot
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, cpu_percentages, marker='o', linestyle='-', label='CPU Usage (%)')
    plt.plot(timestamps, memory_percentages, marker='o', linestyle='-', label='Memory Usage (%)')
    plt.title('CPU and Memory Usage Over Time')
    plt.xlabel('Time')
    plt.ylabel('Usage (%)')
    plt.tight_layout()
    plt.show()
    
    # Show the plot interactively
    # plt.pause(1)
   
    plt.savefig('monitoring_plot.png')
# # Call the plot_data function periodically to update the plot in real-time
# while True:
#     plot_data()
host = "10.1.12.110"
username = "root"
password = "root"
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
 # Connect to the remote server
ssh_client.connect(host, username=username, password=password)
def main():
    # Remote server details
    host = "10.1.12.98"
    username = "root"
    password = "root"

    # SSH client setup
    

    try:
        # Connect to the remote server
        ssh_client.connect(host, username=username, password=password)

        while True:
            # Execute the command to monitor CPU and memory usage
            command = "top -bn 1 | awk 'NR==3{print $2}' && free | awk '/Mem/{printf \"%.2f\", $3/$2*100}'"
            output = execute_remote_command(ssh_client, command)

            # Parse the output
            cpu_usage, memory_usage = map(float, output)

            # Get the current timestamp
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            # Convert the formatted timestamp to a Unix timestamp
            unix_timestamp = int(time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")))

            # Insert data into the database with removal of old data logic
            insert_data_into_database(unix_timestamp, cpu_usage, memory_usage)

            # Print the data with timestamp
            print(f"Timestamp: {unix_timestamp}")
            print(f"CPU Usage: {cpu_usage}%")
            print(f"Memory Usage: {memory_usage}%")
            print("=" * 40)

            plot_data()


    except paramiko.AuthenticationException:
        print("Authentication failed, please check your credentials.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except KeyboardInterrupt:
        print("Monitoring stopped.")
    finally:
        ssh_client.close()
        conn.close()
# if __name__ == "__main__":
#     main()
