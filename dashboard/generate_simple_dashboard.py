#!/usr/bin/env python3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
import numpy as np

# Load data
data_file = Path(__file__).parent.parent / 'data' / 'raw_sensor_data.csv'
df = pd.read_csv(data_file)
df['timestamp'] = pd.to_datetime(df['timestamp'])

analysis_file = Path(__file__).parent.parent / 'analysis' / 'eda_analysis.json'
with open(analysis_file, 'r') as f:
    analysis = json.load(f)

stats = analysis['summary_statistics']

# BGS Brand Colors
BGS_PRIMARY = '#002E40'
BGS_SECONDARY = '#AD9C70'
BGS_ACCENT = '#4A90E2'

# Create plots and save directly
from plotly import offline

# Create comprehensive figure with subplots
fig = make_subplots(
    rows=5, cols=1,
    row_heights=[0.25, 0.25, 0.25, 0.25, 0.05],
    subplot_titles=('Temperature (°C)', 'Barometric Pressure (mbar)',
                    'Oxygen (%)', 'Carbon Dioxide (%)', ''),
    shared_xaxes=True,
    vertical_spacing=0.03
)

# Add traces
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature_c'],
                         name='Temperature', line=dict(color=BGS_ACCENT, width=2)),
              row=1, col=1)
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['pressure_mbar'],
                         name='Pressure', line=dict(color='#ff7f0e', width=2)),
              row=2, col=1)
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['oxygen_pct'],
                         name='Oxygen', line=dict(color='#2ca02c', width=2)),
              row=3, col=1)
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['co2_pct'],
                         name='CO₂', line=dict(color='#d62728', width=2)),
              row=4, col=1)

fig.update_xaxes(title_text='Date', row=4, col=1)
fig.update_layout(
    height=1000,
    showlegend=False,
    title_text=f'<b>BGS Site 1 GasClam Environmental Monitoring Dashboard</b><br>' +
               f'<sub>Data Period: {df["timestamp"].min().strftime("%Y-%m-%d")} to {df["timestamp"].max().strftime("%Y-%m-%d")} ({len(df)} observations)</sub>',
    title_font=dict(size=24, color=BGS_PRIMARY),
    hovermode='x unified',
    template='plotly_white'
)

# Save main dashboard
print('Creating dashboard...')
offline.plot(fig, filename='index.html', auto_open=False)
print(f'Dashboard created: {Path(__file__).parent / "index.html"}')
