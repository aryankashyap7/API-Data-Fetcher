import requests
import json
import pandas as pd
import os
from datetime import datetime, timedelta
import argparse

def fetch_data(api_config):
    headers = api_config.get('headers', {})
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.102 Safari/537.36'
    
    params = api_config.get('params', {})
    if 'start_date' in api_config and 'end_date' in api_config:
        for key, value in params.items():
            if isinstance(value, str):
                if api_config.get('includes_end_date', 'true').lower() == 'false' and api_config.get('precise_timestamp')=='true':
                    end_date = (datetime.strptime(api_config['end_date'], '%Y-%m-%dT%H:%M:%S') + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
                elif api_config.get('includes_end_date', 'true').lower() == 'false':
                    end_date = (datetime.strptime(api_config['end_date'], '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                else:
                    end_date = api_config['end_date']
                params[key] = value.replace("{start_date}", api_config['start_date']).replace("{end_date}", end_date)

    url = api_config['url']
    all_data = []
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=5)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    if api_config.get("pagination") == 'true':
        page = 1
        while True:
            print(f"Fetching data from page {page}...")
            params['page'] = page
            try:
                response = session.get(url, headers=headers, params=params)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 500:
                    print(f"500 Server Error on page {page}. Assuming no data.")
                    break
                else:
                    raise

            try:
                data = response.json()
            except ValueError:
                print(f"Invalid JSON response: {response.text}")
                break

            # Process data based on its type
            if isinstance(data, dict):
                results = data.get('results', [])
            elif isinstance(data, list):
                results = data
            else:
                print(f"Unexpected response format: {type(data)}")
                break

            if not results:
                print(f"No more data on page {page}.")
                break
            
            all_data.extend(results)
            page += 1

    else:
        print(f"Fetching data without pagination...")
        response = session.get(url, headers=headers, params=params)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            print(f"Invalid JSON response: {response.text}")
            return []

        # Process data based on its type
        if isinstance(data, dict):
            results = data.get('results', [])
        elif isinstance(data, list):
            results = data
        else:
            print(f"Unexpected response format: {type(data)}")
            return []

        all_data.extend(results)

    return all_data


def parse_dates(dates_arg, precise_timestamp):
    if len(dates_arg) == 2:
        # Convert startdate and enddate to 'yyyy-mm-dd' format
        start_date = datetime.strptime(dates_arg[0], '%d-%m-%Y').strftime('%Y-%m-%d')
        end_date = datetime.strptime(dates_arg[1], '%d-%m-%Y').strftime('%Y-%m-%d')
    elif len(dates_arg) == 1:
        if dates_arg[0].lower() == "today":
            start_date = end_date = datetime.now().strftime('%Y-%m-%d')
        elif dates_arg[0].lower() == "yesterday":
            start_date = end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            raise ValueError(f"Unrecognized date argument: {dates_arg[0]}")
    else:
        raise ValueError("Invalid number of arguments for --dates. Provide either 1 or 2 arguments.")
    
    # Add precise timestamps if required
    if precise_timestamp == 'true':
        start_date += 'T00:00:00'
        end_date += 'T23:59:59'

    return start_date, end_date

def main(config_file, dates):
    # Load configuration
    with open(config_file) as config_file:
        config = json.load(config_file)

    # Parse and overwrite start_date and end_date if provided
    start_date, end_date = parse_dates(dates, config.get('precise_timestamp', 'false'))
    config['start_date'] = start_date
    config['end_date'] = end_date
    
    # Create data directory
    data_directory = 'data'
    os.makedirs(data_directory, exist_ok=True)

    print(f"\nProcessing {config['name']}...")
    date_range_str = f"{config['start_date']}_to_{config['end_date']}".replace(':', '_').strip('_')
    data = fetch_data(config)

    if data:
        json_file_name = f"{config['name']}_orders_{date_range_str}.json".strip('_')
        csv_file_name = f"{config['name']}_orders_{date_range_str}.csv".strip('_')
        json_file_path = os.path.join(data_directory, json_file_name)
        csv_file_path = os.path.join(data_directory, csv_file_name)
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data saved to {json_file_path}")
        df = pd.DataFrame(data)
        df.to_csv(csv_file_path, index=False)
        print(f"Data saved to {csv_file_path}")
    else:
        print(f"No data for {config['name']}.")
    print("\nData processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch data from an API based on a configuration file.")
    parser.add_argument('--config', type=str, required=True, help="Path to the configuration file")
    parser.add_argument('--dates', nargs='+', required=True, help="Provide dates as 'startdate enddate' in 'dd-mm-yyyy' format, or use 'today' or 'yesterday'.")

    args = parser.parse_args()

    main(args.config, args.dates)
