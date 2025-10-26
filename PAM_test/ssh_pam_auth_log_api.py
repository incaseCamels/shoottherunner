```python
import paramiko
import os

def fetch_failed_auth_logs(hostname, username, password):
    # Create the PAM_test directory if it doesn't exist
    os.makedirs('PAM_test', exist_ok=True)
    
    # SSH client setup
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the Raspberry Pi
        client.connect(hostname, username=username, password=password)
        
        # Command to grep failed PAM authentication logs
        command = "grep 'authentication failure' /var/log/auth.log"
        
        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
        
        # Read the output
        failed_auth_logs = stdout.read().decode()
        
        # Write the output to a file in PAM_test directory
        with open('PAM_test/failed_auth_logs.txt', 'w') as f:
            f.write(failed_auth_logs)
        
        print("Failed authentication logs have been written to PAM_test/failed_auth_logs.txt")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        client.close()

# Example usage
if __name__ == "__main__":
    HOSTNAME = "your_raspberry_pi_ip"
    USERNAME = "your_username"
    PASSWORD = "your_password"
    
    fetch_failed_auth_logs(HOSTNAME, USERNAME, PASSWORD)