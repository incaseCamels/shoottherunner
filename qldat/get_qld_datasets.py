```python
import requests
import pandas as pd

def fetch_datasets():
    # Queensland Open Data API endpoint
    url = "https://data.qld.gov.au/api/3/action/package_list"
    
    # Make a GET request to the API
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        datasets = response.json().get('result', [])
        return datasets
    else:
        print(f"Error fetching datasets: {response.status_code}")
        return []

def save_datasets_to_csv(datasets):
    # Create a DataFrame from the datasets list
    df = pd.DataFrame(datasets, columns=['Dataset ID'])
    
    # Save the DataFrame to a CSV file
    df.to_csv('qld_datasets.csv', index=False)
    print("Datasets saved to qld_datasets.csv")

if __name__ == "__main__":
    datasets = fetch_datasets()
    if datasets:
        save_datasets_to_csv(datasets)