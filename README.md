i# API Data Fetcher

![API Data Fetcher Banner](./assets/banner2.jpg)

This Python script is designed to fetch data from an API based on a provided configuration file. The script handles pagination, date formatting, and saves the retrieved data into both JSON and CSV formats.

## Features

- Fetch data from an API with support for pagination.
- Handle custom date ranges and formats.
- Save data into JSON and CSV files.
- Flexible configuration through a JSON file.

## Prerequisites

- Python 3.6 or higher
- Install required Python packages using the following command:


## Usage

### Command-Line Arguments

- `--config` (required): Path to the JSON configuration file.
- `--dates` (required): Dates in the format `'dd-mm-yyyy'` for start and end dates, or use `'today'` or `'yesterday'`.

### Example Command


This command fetches data based on the configuration in `config.json` for the date range from August 1, 2023, to August 7, 2023.

### JSON Configuration File

The configuration file should be in JSON format and include the following fields:

- `url`: The API endpoint URL.
- `headers`: (Optional) Dictionary of headers to be sent with the request.
- `params`: (Optional) Dictionary of query parameters for the API request. Supports placeholders `{start_date}` and `{end_date}`.
- `includes_end_date`: (Optional) Set to `'false'` if the end date should not be included.
- `precise_timestamp`: (Optional) Set to `'true'` if the start and end dates should include precise timestamps.
- `pagination`: (Optional) Set to `'true'` if the API supports pagination.
- `name`: A descriptive name for the dataset being fetched.

#### Example `config.json`
```
{
    "name": "example_data",
    "url": "https://api.example.com/data",
    "headers": {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Accept": "application/json"
    },
    "params": {
        "start_date": "{start_date}",
        "end_date": "{end_date}",
        "limit": "100",
        "sort": "desc"
    },
    "includes_end_date": "true",
    "precise_timestamp": "false",
    "pagination": "true"
}
```


### Script Overview

#### `fetch_data(api_config)`

Fetches data from the API based on the provided configuration.

- **Parameters:**
  - `api_config` (dict): Configuration dictionary containing API details and parameters.
  
- **Returns:**
  - `list`: List of data records retrieved from the API.

#### `parse_dates(dates_arg, precise_timestamp)`

Parses the date arguments and formats them according to the requirements.

- **Parameters:**
  - `dates_arg` (list): List of date strings.
  - `precise_timestamp` (str): Indicates if precise timestamps should be used.
  
- **Returns:**
  - `tuple`: Start and end dates in the correct format.

#### `main(config_file, dates)`

Main function to load configuration, fetch data, and save it.

- **Parameters:**
  - `config_file` (str): Path to the JSON configuration file.
  - `dates` (list): List of date strings.

### Output

The script saves the fetched data in the `data` directory with filenames based on the dataset's name and the date range.

- JSON file: `{name}_orders_{start_date}_to_{end_date}.json`
- CSV file: `{name}_orders_{start_date}_to_{end_date}.csv`

### Error Handling

- The script retries API requests up to 5 times in case of transient errors.
- It raises exceptions for invalid configurations or API responses.

## License

This project is licensed under the MIT License.


