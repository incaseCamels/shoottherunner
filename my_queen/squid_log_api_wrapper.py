```python
import paramiko
import json

def get_last_post_requests(hostname, username, password):
    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the server
        client.connect(hostname, username=username, password=password)

        # Command to get the last 100 POST requests from the Squid logs
        command = "tail -n 100 /var/log/squid/access.log | grep 'POST' | grep '200'"

        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')

        # Process the output into a list
        logs = output.strip().split('\n')
        return logs

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        client.close()

if __name__ == "__main__":
    # Example usage
    hostname = "your_squid_server_ip"
    username = "your_username"
    password = "your_password"

    logs = get_last_post_requests(hostname, username, password)
    print(json.dumps(logs, indent=4))