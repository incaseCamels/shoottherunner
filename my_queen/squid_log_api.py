```python
import paramiko
import re

def get_squid_logs(hostname, port, username, password):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the remote server
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # Execute the command to get the last 100 POST requests from Squid logs
        command = "tail -n 100 /var/log/squid/access.log | grep 'POST' | grep '200'"
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Read the output
        output = stdout.read().decode('utf-8')
        return output.splitlines()
    
    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        # Close the SSH connection
        ssh.close()

if __name__ == "__main__":
    # Example usage
    hostname = "your_remote_host"
    port = 22
    username = "your_username"
    password = "your_password"

    logs = get_squid_logs(hostname, port, username, password)
    for log in logs:
        print(log)