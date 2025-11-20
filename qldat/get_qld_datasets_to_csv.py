```python
import requests
import pandas as pd

def fetch_datasets():
    url = "https://data.qld.gov.au/api/3/action/package_list"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()['result']
    else:
        print(f"Failed to fetch datasets: {response.status_code}")
        return []

def save_datasets_to_csv(datasets):
    df = pd.DataFrame(datasets, columns=['Dataset ID'])
    df.to_csv('qld_datasets.csv', index=False)
    print("Datasets saved to qld_datasets.csv")

if __name__ == "__main__":
    datasets = fetch_datasets()
    if datasets:
        save_datasets_to_csv(datasets)
```