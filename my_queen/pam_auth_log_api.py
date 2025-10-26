```python
import paramiko
import os
import re

class PAMAuthLogAPI:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        self.ssh_client.connect(self.hostname, username=self.username, password=self.password)

    def fetch_failed_auths(self):
        stdin, stdout, stderr = self.ssh_client.exec_command("grep 'failed' /var/log/auth.log")
        failed_auths = stdout.read().decode()
        return failed_auths

    def write_to_file(self, data, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file_path = os.path.join(output_folder, 'failed_auths.log')
        with open(output_file_path, 'w') as file:
            file.write(data)

    def close(self):
        self.ssh_client.close()

def main():
    hostname = 'your_raspberry_pi_ip'
    username = 'your_username'
    password = 'your_password'
    output_folder = 'PAM_test'

    pam_api = PAMAuthLogAPI(hostname, username, password)
    pam_api.connect()
    failed_auths = pam_api.fetch_failed_auths()
    pam_api.write_to_file(failed_auths, output_folder)
    pam_api.close()

if __name__ == "__main__":
    main()