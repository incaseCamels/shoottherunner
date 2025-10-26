```markdown
# My Queen

This project contains a Python script for collecting and categorizing malicious commands from honeypots into TTPs (Tactics, Techniques, and Procedures).

## Directory Structure

- `my_queen/`: Contains the main script and package files.
- `README.md`: This file.

## Usage

1. Place your honeypot log files in the specified directory.
2. Update the `honeypot_dir` in `collect_malicious_commands.py` with the path to your honeypots.
3. Run the script to collect and categorize commands:
   ```bash
   python my_queen/collect_malicious_commands.py
   ```
4. The categorized commands will be saved in `malicious_commands.json`.