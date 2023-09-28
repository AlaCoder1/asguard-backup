import paramiko
import time
import matplotlib.pyplot as plt
# Initialize lists to store data
timestamps = []
cpu_percentages = []
memory_percentages = []

def convert_to_unix_timestamp(timestamp):
    try:
        # Parse the timestamp string into a struct_time
        parsed_time = time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

        # Convert the struct_time to a Unix timestamp
        unix_timestamp = int(time.mktime(parsed_time))
        return unix_timestamp
    except ValueError:
        return None
def execute_remote_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    return stdout.readlines()

def main():
    # Remote server details
    host = "10.1.12.98"
    username = "root"
    password = "root"

    # SSH client setup
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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
            unix_timestamp = convert_to_unix_timestamp(current_time)
            # Print the data with timestamp
            print(f"Timestamp: {unix_timestamp}")
            print(f"CPU Usage: {cpu_usage}%")
            print(f"Memory Usage: {memory_usage}%")
            print("=" * 40)
            # Append data to the lists
            timestamps.append(current_time)
            cpu_percentages.append(cpu_usage)
            memory_percentages.append(memory_usage)

            # Limit the number of data points (e.g., display the last 20 data points)
            if len(timestamps) > 20:
                timestamps.pop(0)
                cpu_percentages.pop(0)
                memory_percentages.pop(0)

            # Update the plots
            plt.clf()

            # Plot CPU usage
            plt.subplot(211)
            plt.plot(timestamps, cpu_percentages, marker='o', linestyle='-')
            plt.title('CPU Usage Over Time')
            plt.xlabel('Time')
            plt.ylabel('CPU Usage (%)')

            # Plot memory usage
            plt.subplot(212)
            plt.plot(timestamps, memory_percentages, marker='o', linestyle='-')
            plt.title('Memory Usage Over Time')
            plt.xlabel('Time')
            plt.ylabel('Memory Usage (%)')

            plt.tight_layout()
            plt.show()
            # Pause for 1 second between updates
            plt.pause(1)
               

    except paramiko.AuthenticationException:
        print("Authentication failed, please check your credentials.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except KeyboardInterrupt:
        print("Monitoring stopped.")
    finally:
        ssh_client.close()

if __name__ == "__main__":
    main()
