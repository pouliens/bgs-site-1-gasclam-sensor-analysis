#!/usr/bin/env python3
"""
Process BGS sensor data and prepare for analysis
"""

import pandas as pd
import json
from pathlib import Path

# Raw data from MCP fetch (truncated for brevity - full data will be loaded from JSON)
temperature_data = {
    "datastream_id": 94,
    "datastream_name": "GGS01_01 Temperature",
    "unit_symbol": "C",
    "unit_name": "Degrees Celsius",
    "observations": []  # Will load from full dataset
}

barometric_pressure_data = {
    "datastream_id": 102,
    "datastream_name": "GGS01_01 Barometric Pressure",
    "unit_symbol": "mbar",
    "unit_name": "Millibar",
    "observations": []
}

oxygen_data = {
    "datastream_id": 109,
    "datastream_name": "GGS01_01 Oxygen",
    "unit_symbol": "%",
    "unit_name": "Percentage",
    "observations": []
}

co2_data = {
    "datastream_id": 110,
    "datastream_name": "GGS01_01 Carbon Dioxide",
    "unit_symbol": "%",
    "unit_name": "Percentage",
    "observations": []
}

def process_sensor_data():
    """Process and merge all sensor datastreams"""

    # Note: In actual implementation, we'll load the full JSON data
    # For now, creating empty dataframes as placeholders

    # Create individual dataframes for each parameter
    dfs = []

    for data in [temperature_data, barometric_pressure_data, oxygen_data, co2_data]:
        if data['observations']:
            df = pd.DataFrame(data['observations'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.rename(columns={'value': data['datastream_name'].split()[-1]})
            df = df[['timestamp', data['datastream_name'].split()[-1], 'quality_status']]
            dfs.append(df)

    # Merge all dataframes on timestamp
    if dfs:
        combined = dfs[0]
        for df in dfs[1:]:
            combined = combined.merge(df, on='timestamp', how='outer', suffixes=('', '_dup'))

        # Sort by timestamp
        combined = combined.sort_values('timestamp')
        combined = combined.reset_index(drop=True)

        return combined

    return None

if __name__ == "__main__":
    df = process_sensor_data()
    if df is not None:
        output_path = Path(__file__).parent / "raw_sensor_data.csv"
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
        print(f"Shape: {df.shape}")
        print(f"\nFirst few rows:\n{df.head()}")
    else:
        print("No data to process")
