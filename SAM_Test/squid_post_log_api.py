```python
import paramiko

def get_last_100_post_requests(hostname, username, password, log_file_path):
    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the remote server
        ssh_client.connect(hostname, username=username, password=password)
        
        # Command to get the last 100 POST requests with response in the 200 range
        command = f"tail -n 100 {log_file_path} | grep 'POST' | grep '200'"
        
        # Execute the command
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Read the output
        post_requests = stdout.readlines()
        
        return post_requests
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
    finally:
        # Close the SSH connection
        ssh_client.close()

if __name__ == "__main__":
    # Example usage
    hostname = "your_squid_proxy_host"
    username = "your_username"
    password = "your_password"
    log_file_path = "/var/log/squid/access.log"
    
    post_requests = get_last_100_post_requests(hostname, username, password, log_file_path)
    
    for request in post_requests:
        print(request.strip())