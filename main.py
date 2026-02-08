import json
import sys
import os

from modules import loader, processor, visualizer
from GUI import app 

def load_config(file_path="config.json"):
    """Safely loads the configuration file."""
    if not os.path.exists(file_path):
        print(f"Error: Config file '{file_path}' not found.")
        sys.exit(1)
    with open(file_path, "r") as f:
        return json.load(f)

def main():
    print("Starting GDP Analysis System...")

    config = load_config()

    data_path = config.get('data_file', 'data/gdp_data.csv')
    app_mode = config.get('app_mode', 'gui')

    #CHECK MODE: GUI vs SCRIPT
    if app_mode == 'gui':
        print(f"... Launching Interactive Dashboard (GUI)")
        print(f"... Data Source: {data_path}")

        root = app.GDPApp(config)
        root.mainloop()
        
    else:
        print("...Running in Batch Script Mode (No Window)")
        print(f"...Loading Data from: {data_path}")
        
        try:
            raw_data = loader.load_data(data_path)
        except Exception as e:
            print(f"Critical Error in Loader: {e}")
            sys.exit(1)

        if not raw_data:
            print("Error: Data loaded is empty. Check your CSV path.")
            sys.exit(1)

        target_region = config['filters']['region']
        target_year = config['filters']['year']
        
        print(f"...Filtering for Region: '{target_region}' | Year: {target_year}")

        comp_data = processor.filter_data(raw_data, region=target_region, year=target_year)

        trend_data = []
        if comp_data:
            largest_country = sorted(comp_data, key=lambda x: x['GDP'], reverse=True)[0]['Country']
            print(f"...Fetching historical trend for: {largest_country}")
            trend_data = processor.filter_data(raw_data, country=largest_country)
        else:
            print(f"Warning: No data found for {target_region} in {target_year}")

        visualizer.create_dashboard(comp_data, trend_data, config)
        print("Analysis saved to output folder.")

if __name__ == "__main__":
    main()