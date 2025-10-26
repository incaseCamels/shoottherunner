```python
import os
import json
from collections import defaultdict

class MaliciousCommandCollector:
    def __init__(self, honeypot_dir):
        self.honeypot_dir = honeypot_dir
        self.commands = defaultdict(list)

    def collect_commands(self):
        for filename in os.listdir(self.honeypot_dir):
            if filename.endswith('.log'):
                self._process_log_file(os.path.join(self.honeypot_dir, filename))

    def _process_log_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                command, ttp = self._extract_command_and_ttp(line)
                if command and ttp:
                    self.commands[ttp].append(command)

    def _extract_command_and_ttp(self, line):
        # Placeholder for actual extraction logic
        parts = line.strip().split(' ')
        if len(parts) < 2:
            return None, None
        command = parts[0]
        ttp = parts[1]  # This should be replaced with actual TTP extraction logic
        return command, ttp

    def save_to_json(self, output_file):
        with open(output_file, 'w') as json_file:
            json.dump(self.commands, json_file, indent=4)

if __name__ == "__main__":
    collector = MaliciousCommandCollector(honeypot_dir='path/to/honeypots')
    collector.collect_commands()
    collector.save_to_json(output_file='malicious_commands.json')