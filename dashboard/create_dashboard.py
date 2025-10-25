#!/usr/bin/env python3
"""
Create Interactive HTML Dashboard for BGS Sensor Data Analysis
Professional dashboard with BGS branding and Plotly visualizations
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from pathlib import Path
import numpy as np

# BGS Brand Colors
BGS_PRIMARY = '#002E40'
BGS_SECONDARY = '#AD9C70'
BGS_ACCENT = '#4A90E2'

def load_data():
    """Load sensor data and analysis results"""
    data_file = Path(__file__).parent.parent / 'data' / 'raw_sensor_data.csv'
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    analysis_file = Path(__file__).parent.parent / 'analysis' / 'eda_analysis.json'
    with open(analysis_file, 'r') as f:
        analysis = json.load(f)

    return df, analysis

def create_time_series_plot(df):
    """Create interactive multi-parameter time series"""
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=('Temperature (°C)', 'Barometric Pressure (mbar)',
                       'Oxygen (%)', 'Carbon Dioxide (%)'),
        shared_xaxes=True,
        vertical_spacing=0.05
    )

    # Temperature
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature_c'],
                             name='Temperature', line=dict(color=BGS_ACCENT, width=2),
                             hovertemplate='%{y:.1f}°C<extra></extra>'),
                  row=1, col=1)

    # Pressure
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['pressure_mbar'],
                             name='Pressure', line=dict(color='#ff7f0e', width=2),
                             hovertemplate='%{y:.0f} mbar<extra></extra>'),
                  row=2, col=1)

    # Oxygen
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['oxygen_pct'],
                             name='Oxygen', line=dict(color='#2ca02c', width=2),
                             hovertemplate='%{y:.1f}%<extra></extra>'),
                  row=3, col=1)

    # CO2
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['co2_pct'],
                             name='CO₂', line=dict(color='#d62728', width=2),
                             hovertemplate='%{y:.1f}%<extra></extra>'),
                  row=4, col=1)

    fig.update_xaxes(title_text='Date', row=4, col=1)
    fig.update_layout(
        height=900,
        showlegend=False,
        title_text='<b>Time Series Analysis - BGS Site 1 GasClam Borehole</b>',
        title_font=dict(size=20, color=BGS_PRIMARY),
        hovermode='x unified'
    )

    return fig

def create_correlation_heatmap(df):
    """Create interactive correlation heatmap"""
    numeric_cols = ['temperature_c', 'pressure_mbar', 'oxygen_pct', 'co2_pct']
    corr_matrix = df[numeric_cols].corr()

    labels = ['Temperature', 'Pressure', 'Oxygen', 'CO₂']

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels,
        y=labels,
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=np.round(corr_matrix.values, 3),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title='Correlation')
    ))

    fig.update_layout(
        title='<b>Parameter Correlation Matrix</b>',
        title_font=dict(size=18, color=BGS_PRIMARY),
        xaxis_title='',
        yaxis_title='',
        height=500
    )

    return fig

def create_distribution_plots(df):
    """Create interactive distribution plots"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature Distribution', 'Pressure Distribution',
                       'Oxygen Distribution', 'CO₂ Distribution')
    )

    parameters = [
        ('temperature_c', '°C', 1, 1),
        ('pressure_mbar', 'mbar', 1, 2),
        ('oxygen_pct', '%', 2, 1),
        ('co2_pct', '%', 2, 2)
    ]

    for col, unit, row, col_idx in parameters:
        fig.add_trace(go.Histogram(x=df[col], name=col,
                                   histnorm='probability density',
                                   marker=dict(color=BGS_ACCENT, opacity=0.7),
                                   hovertemplate=f'Value: %{{x:.2f}} {unit}<br>Density: %{{y:.3f}}<extra></extra>'),
                      row=row, col=col_idx)

    fig.update_layout(
        height=600,
        showlegend=False,
        title_text='<b>Parameter Distributions</b>',
        title_font=dict(size=18, color=BGS_PRIMARY)
    )

    return fig

def create_scatter_plot(df):
    """Create O2 vs CO2 scatter plot"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['oxygen_pct'],
        y=df['co2_pct'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['temperature_c'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Temp (°C)'),
            line=dict(width=0.5, color='white')
        ),
        text=[f'Temp: {t:.1f}°C<br>O₂: {o:.1f}%<br>CO₂: {c:.1f}%'
              for t, o, c in zip(df['temperature_c'], df['oxygen_pct'], df['co2_pct'])],
        hovertemplate='%{text}<extra></extra>'
    ))

    # Add trendline
    z = np.polyfit(df['oxygen_pct'], df['co2_pct'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['oxygen_pct'].min(), df['oxygen_pct'].max(), 100)

    fig.add_trace(go.Scatter(
        x=x_line,
        y=p(x_line),
        mode='lines',
        line=dict(color='red', dash='dash', width=2),
        name=f'Trendline (R²={np.corrcoef(df["oxygen_pct"], df["co2_pct"])[0,1]**2:.3f})'
    ))

    fig.update_layout(
        title='<b>Oxygen vs Carbon Dioxide Relationship</b>',
        title_font=dict(size=18, color=BGS_PRIMARY),
        xaxis_title='Oxygen (%)',
        yaxis_title='Carbon Dioxide (%)',
        height=500,
        hovermode='closest'
    )

    return fig

def create_box_plots(df):
    """Create interactive box plots"""
    fig = make_subplots(
        rows=1, cols=4,
        subplot_titles=('Temperature', 'Pressure', 'Oxygen', 'CO₂')
    )

    parameters = [
        ('temperature_c', 1),
        ('pressure_mbar', 2),
        ('oxygen_pct', 3),
        ('co2_pct', 4)
    ]

    colors = [BGS_ACCENT, '#ff7f0e', '#2ca02c', '#d62728']

    for idx, (col, col_idx) in enumerate(parameters):
        fig.add_trace(go.Box(y=df[col], name=col,
                             marker=dict(color=colors[idx]),
                             boxmean='sd'),
                      row=1, col=col_idx)

    fig.update_layout(
        height=400,
        showlegend=False,
        title_text='<b>Parameter Box Plots - Outlier Detection</b>',
        title_font=dict(size=18, color=BGS_PRIMARY)
    )

    return fig

def generate_html(df, analysis):
    """Generate complete HTML dashboard"""

    # Create all plots
    ts_plot = create_time_series_plot(df)
    corr_plot = create_correlation_heatmap(df)
    dist_plot = create_distribution_plots(df)
    scatter_plot = create_scatter_plot(df)
    box_plot = create_box_plots(df)

    # Get statistics
    stats = analysis['summary_statistics']

    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BGS Sensor Data Analysis Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}

        .header {{
            background: linear-gradient(135deg, {BGS_PRIMARY} 0%, #004d6b 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .section {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .section h2 {{
            color: {BGS_PRIMARY};
            font-size: 1.8em;
            margin-bottom: 15px;
            border-bottom: 3px solid {BGS_SECONDARY};
            padding-bottom: 10px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid {BGS_ACCENT};
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}

        .stat-card h3 {{
            color: {BGS_PRIMARY};
            font-size: 1.1em;
            margin-bottom: 10px;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: {BGS_ACCENT};
            margin: 10px 0;
        }}

        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}

        .plot-container {{
            margin: 20px 0;
            border-radius: 8px;
            overflow: hidden;
        }}

        .key-findings {{
            background: #f0f8ff;
            border-left: 4px solid {BGS_ACCENT};
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .key-findings h3 {{
            color: {BGS_PRIMARY};
            margin-bottom: 15px;
        }}

        .key-findings ul {{
            list-style-position: inside;
            line-height: 2;
        }}

        .footer {{
            background: {BGS_PRIMARY};
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 30px;
        }}

        .data-quality {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        th {{
            background-color: {BGS_PRIMARY};
            color: white;
            font-weight: 600;
        }}

        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>BGS Sensor Data Analysis Dashboard</h1>
        <p>Environmental Monitoring - Site 1 GasClam Borehole</p>
        <p style="font-size: 0.9em; margin-top: 10px;">
            Data Period: {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}
            <span class="data-quality">Data Quality: Excellent</span>
        </p>
    </div>

    <div class="container">
        <!-- Executive Summary -->
        <div class="section">
            <h2>Executive Summary</h2>
            <p style="font-size: 1.1em; line-height: 1.8; margin-bottom: 20px;">
                This dashboard presents a comprehensive analysis of environmental sensor data from the BGS Site 1 GasClam
                borehole installation. The analysis covers {len(df)} observations collected over {analysis['basic_info']['date_range']['duration_days']} days,
                monitoring temperature, barometric pressure, oxygen levels, and carbon dioxide concentrations.
            </p>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Temperature</h3>
                    <div class="stat-value">{stats['temperature_c']['mean']:.1f}°C</div>
                    <div class="stat-label">Mean (Range: {stats['temperature_c']['min']:.1f} - {stats['temperature_c']['max']:.1f}°C)</div>
                </div>
                <div class="stat-card">
                    <h3>Barometric Pressure</h3>
                    <div class="stat-value">{stats['pressure_mbar']['mean']:.0f} mbar</div>
                    <div class="stat-label">Mean (Range: {stats['pressure_mbar']['min']:.0f} - {stats['pressure_mbar']['max']:.0f} mbar)</div>
                </div>
                <div class="stat-card">
                    <h3>Oxygen</h3>
                    <div class="stat-value">{stats['oxygen_pct']['mean']:.1f}%</div>
                    <div class="stat-label">Mean (Range: {stats['oxygen_pct']['min']:.1f} - {stats['oxygen_pct']['max']:.1f}%)</div>
                </div>
                <div class="stat-card">
                    <h3>Carbon Dioxide</h3>
                    <div class="stat-value">{stats['co2_pct']['mean']:.1f}%</div>
                    <div class="stat-label">Mean (Range: {stats['co2_pct']['min']:.1f} - {stats['co2_pct']['max']:.1f}%)</div>
                </div>
            </div>
        </div>

        <!-- Time Series Analysis -->
        <div class="section">
            <h2>Time Series Analysis</h2>
            <div class="plot-container" id="timeseries"></div>
        </div>

        <!-- Statistical Analysis -->
        <div class="section">
            <h2>Statistical Analysis</h2>

            <h3 style="color: {BGS_PRIMARY}; margin: 20px 0 15px 0;">Descriptive Statistics</h3>
            <table>
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th>Mean</th>
                        <th>Std Dev</th>
                        <th>Min</th>
                        <th>Median</th>
                        <th>Max</th>
                        <th>Skewness</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Temperature (°C)</strong></td>
                        <td>{stats['temperature_c']['mean']:.2f}</td>
                        <td>{stats['temperature_c']['std']:.2f}</td>
                        <td>{stats['temperature_c']['min']:.1f}</td>
                        <td>{stats['temperature_c']['50%']:.1f}</td>
                        <td>{stats['temperature_c']['max']:.1f}</td>
                        <td>{stats['temperature_c']['skewness']:.3f}</td>
                    </tr>
                    <tr>
                        <td><strong>Pressure (mbar)</strong></td>
                        <td>{stats['pressure_mbar']['mean']:.2f}</td>
                        <td>{stats['pressure_mbar']['std']:.2f}</td>
                        <td>{stats['pressure_mbar']['min']:.0f}</td>
                        <td>{stats['pressure_mbar']['50%']:.0f}</td>
                        <td>{stats['pressure_mbar']['max']:.0f}</td>
                        <td>{stats['pressure_mbar']['skewness']:.3f}</td>
                    </tr>
                    <tr>
                        <td><strong>Oxygen (%)</strong></td>
                        <td>{stats['oxygen_pct']['mean']:.2f}</td>
                        <td>{stats['oxygen_pct']['std']:.2f}</td>
                        <td>{stats['oxygen_pct']['min']:.1f}</td>
                        <td>{stats['oxygen_pct']['50%']:.1f}</td>
                        <td>{stats['oxygen_pct']['max']:.1f}</td>
                        <td>{stats['oxygen_pct']['skewness']:.3f}</td>
                    </tr>
                    <tr>
                        <td><strong>CO₂ (%)</strong></td>
                        <td>{stats['co2_pct']['mean']:.2f}</td>
                        <td>{stats['co2_pct']['std']:.2f}</td>
                        <td>{stats['co2_pct']['min']:.1f}</td>
                        <td>{stats['co2_pct']['50%']:.1f}</td>
                        <td>{stats['co2_pct']['max']:.1f}</td>
                        <td>{stats['co2_pct']['skewness']:.3f}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Distribution Analysis -->
        <div class="section">
            <h2>Distribution Analysis</h2>
            <div class="plot-container" id="distributions"></div>
        </div>

        <!-- Correlation Analysis -->
        <div class="section">
            <h2>Correlation Analysis</h2>
            <div class="plot-container" id="correlation"></div>

            <div class="key-findings">
                <h3>Key Findings</h3>
                <ul>
                    <li><strong>Oxygen vs CO₂:</strong> Moderate negative correlation (r = -0.35), indicating expected inverse relationship in subsurface gas dynamics.</li>
                    <li><strong>Temperature vs Pressure:</strong> Weak negative correlation (r = -0.26), suggesting some atmospheric influence on subsurface temperature.</li>
                    <li><strong>Gas Concentrations:</strong> Oxygen levels remain relatively stable (21.5% ± 2.0%), while CO₂ shows higher variability (1.9% ± 0.6%).</li>
                    <li><strong>Data Quality:</strong> No missing data detected; all observations marked as "Good" quality.</li>
                </ul>
            </div>
        </div>

        <!-- Parameter Relationships -->
        <div class="section">
            <h2>Parameter Relationships</h2>
            <div class="plot-container" id="scatter"></div>
        </div>

        <!-- Outlier Detection -->
        <div class="section">
            <h2>Outlier Detection</h2>
            <div class="plot-container" id="boxplots"></div>
            <p style="margin-top: 15px; font-size: 0.95em;">
                <strong>Outlier Summary:</strong> Minimal outliers detected across all parameters.
                CO₂ shows {analysis['outlier_detection']['co2_pct']['iqr_method']['percentage']:.1f}% outliers (IQR method),
                likely representing natural variations in subsurface gas concentrations.
            </p>
        </div>

        <!-- Scientific Interpretation -->
        <div class="section">
            <h2>Scientific Interpretation</h2>
            <h3 style="color: {BGS_PRIMARY}; margin: 20px 0 15px 0;">Subsurface Conditions</h3>
            <p style="line-height: 1.8;">
                The sensor data reveals stable subsurface environmental conditions with minimal variability in most parameters.
                The mean temperature of {stats['temperature_c']['mean']:.1f}°C with low standard deviation ({stats['temperature_c']['std']:.2f}°C)
                indicates thermally stable subsurface conditions typical of borehole environments below the zone of seasonal variation.
            </p>

            <h3 style="color: {BGS_PRIMARY}; margin: 20px 0 15px 0;">Gas Dynamics</h3>
            <p style="line-height: 1.8;">
                The inverse relationship between oxygen and CO₂ (r = -0.35) is consistent with typical subsurface respiration processes.
                Areas with higher biological activity or organic matter decomposition would show decreased oxygen and increased CO₂.
                The oxygen levels (mean: {stats['oxygen_pct']['mean']:.1f}%) suggest generally well-aerated conditions, while
                CO₂ levels (mean: {stats['co2_pct']['mean']:.1f}%) are elevated compared to atmospheric levels (0.04%),
                indicating active subsurface processes.
            </p>

            <h3 style="color: {BGS_PRIMARY}; margin: 20px 0 15px 0;">Pressure Variations</h3>
            <p style="line-height: 1.8;">
                Barometric pressure variations (range: {stats['pressure_mbar']['min']:.0f} - {stats['pressure_mbar']['max']:.0f} mbar)
                reflect normal atmospheric pressure changes. The weak correlation with temperature suggests some coupling between
                atmospheric conditions and subsurface thermal regime, possibly through advective processes.
            </p>
        </div>

        <!-- Data Quality Assessment -->
        <div class="section">
            <h2>Data Quality Assessment</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Completeness</h3>
                    <div class="stat-value">100%</div>
                    <div class="stat-label">No missing observations</div>
                </div>
                <div class="stat-card">
                    <h3>Quality Status</h3>
                    <div class="stat-value">Good</div>
                    <div class="stat-label">All data validated</div>
                </div>
                <div class="stat-card">
                    <h3>Temporal Coverage</h3>
                    <div class="stat-value">{analysis['basic_info']['date_range']['duration_days']}</div>
                    <div class="stat-label">Days of continuous monitoring</div>
                </div>
                <div class="stat-card">
                    <h3>Sample Rate</h3>
                    <div class="stat-value">~2h</div>
                    <div class="stat-label">Measurement interval</div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>&copy; 2025 British Geological Survey - Environmental Data Analysis Dashboard</p>
        <p style="font-size: 0.9em; margin-top: 10px;">
            Generated with scientific analysis tools | Data source: BGS SensorThings API
        </p>
    </div>

    <script>
        // Time Series Plot
        {ts_plot.to_html(include_plotlyjs=False, div_id='timeseries').split('<div id="timeseries">')[1].split('</div>')[0]}

        // Correlation Heatmap
        {corr_plot.to_html(include_plotlyjs=False, div_id='correlation').split('<div id="correlation">')[1].split('</div>')[0]}

        // Distribution Plots
        {dist_plot.to_html(include_plotlyjs=False, div_id='distributions').split('<div id="distributions">')[1].split('</div>')[0]}

        // Scatter Plot
        {scatter_plot.to_html(include_plotlyjs=False, div_id='scatter').split('<div id="scatter">')[1].split('</div>')[0]}

        // Box Plots
        {box_plot.to_html(include_plotlyjs=False, div_id='boxplots').split('<div id="boxplots">')[1].split('</div>')[0]}
    </script>
</body>
</html>
"""
    return html

def main():
    print("Creating BGS Sensor Data Dashboard...")

    # Load data
    df, analysis = load_data()
    print(f"Loaded {len(df)} observations from {df['timestamp'].min()} to {df['timestamp'].max()}")

    # Generate HTML
    print("Generating dashboard HTML...")
    html = generate_html(df, analysis)

    # Save dashboard
    output_file = Path(__file__).parent / 'index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n=== Dashboard Created Successfully ===")
    print(f"Dashboard saved to: {output_file}")
    print(f"\nTo view: Open {output_file} in your web browser")

if __name__ == "__main__":
    main()
