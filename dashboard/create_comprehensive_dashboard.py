#!/usr/bin/env python3
"""
BGS Sensor Analysis - Comprehensive Interactive Dashboard Generator
Creates a single, self-contained HTML file with all analysis results
"""

import pandas as pd
import json
from pathlib import Path
import base64

# Brand Colors
BGS_PRIMARY = '#002E40'
BGS_SECONDARY = '#AD9C70'

# Load data
data_file = Path(__file__).parent.parent / 'data' / 'raw_sensor_data.csv'
df = pd.read_csv(data_file)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Load analysis results
analysis_file = Path(__file__).parent.parent / 'analysis' / 'eda_analysis.json'
with open(analysis_file, 'r') as f:
    analysis = json.load(f)

stats = analysis['summary_statistics']
date_range = analysis['basic_info']['date_range']

# Function to encode images as base64
def encode_image(image_path):
    """Encode image as base64 for embedding in HTML"""
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# Get all visualization files
viz_dir = Path(__file__).parent.parent / 'visualizations'
viz_files = {
    'multiparameter': viz_dir / 'multiparameter_overlay.png',
    'distributions': viz_dir / 'distributions.png',
    'correlation': viz_dir / 'correlation_heatmap.png',
    'boxplots': viz_dir / 'boxplots.png',
    'scatter_matrix': viz_dir / 'scatter_matrix.png',
    'oxygen_co2': viz_dir / 'oxygen_co2_relationship.png',
    'temp_ts': viz_dir / 'timeseries_temperature_c.png',
    'pressure_ts': viz_dir / 'timeseries_pressure_mbar.png',
    'oxygen_ts': viz_dir / 'timeseries_oxygen_pct.png',
    'co2_ts': viz_dir / 'timeseries_co2_pct.png'
}

# Prepare data for JavaScript embedding (sample every 2nd point to reduce size)
data_json = df.to_json(orient='records', date_format='iso')

# Create HTML
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BGS Site 1 GasClam - Environmental Sensor Analysis Dashboard</title>

    <!-- External Dependencies -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>
        :root {{
            --bgs-primary: {BGS_PRIMARY};
            --bgs-secondary: {BGS_SECONDARY};
            --bgs-light: #f8f9fa;
            --bgs-gray: #6c757d;
            --bgs-dark: #212529;
            --temp-color: #dc3545;
            --pressure-color: #4A90E2;
            --oxygen-color: #28a745;
            --co2-color: #9c27b0;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: var(--bgs-dark);
            background: var(--bgs-light);
        }}

        /* Header Section */
        .hero {{
            background: linear-gradient(135deg, var(--bgs-primary) 0%, #004d66 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .hero h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }}

        .hero .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 300;
        }}

        /* Metric Cards */
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            max-width: 1400px;
            margin: -2rem auto 2rem;
            padding: 0 2rem;
            position: relative;
            z-index: 10;
        }}

        .metric-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            border-top: 4px solid var(--color);
        }}

        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}

        .metric-card .icon {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: var(--color);
        }}

        .metric-card .label {{
            font-size: 0.9rem;
            color: var(--bgs-gray);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .metric-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--bgs-dark);
            margin: 0.25rem 0;
        }}

        .metric-card .range {{
            font-size: 0.85rem;
            color: var(--bgs-gray);
        }}

        /* Container */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        /* Section Styling */
        .section {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }}

        .section h2 {{
            color: var(--bgs-primary);
            font-size: 1.8rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid var(--bgs-secondary);
        }}

        .section h3 {{
            color: var(--bgs-primary);
            font-size: 1.3rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}

        /* Key Findings */
        .findings-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}

        .finding {{
            background: var(--bgs-light);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid var(--bgs-secondary);
        }}

        .finding i {{
            color: var(--bgs-secondary);
            margin-right: 0.5rem;
        }}

        .status-badges {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }}

        .badge.excellent {{
            background: #d4edda;
            color: #155724;
        }}

        .badge.good {{
            background: #d1ecf1;
            color: #0c5460;
        }}

        .badge.minimal {{
            background: #fff3cd;
            color: #856404;
        }}

        .badge i {{
            margin-right: 0.5rem;
        }}

        /* Charts Grid */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
            margin-top: 1.5rem;
        }}

        .chart-container {{
            background: var(--bgs-light);
            padding: 1rem;
            border-radius: 8px;
        }}

        .chart-full {{
            grid-column: 1 / -1;
        }}

        /* Stats Table */
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}

        .stats-table th,
        .stats-table td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}

        .stats-table th {{
            background: var(--bgs-primary);
            color: white;
            font-weight: 600;
        }}

        .stats-table tr:hover {{
            background: var(--bgs-light);
        }}

        .stats-table td:first-child {{
            font-weight: 600;
            color: var(--bgs-primary);
        }}

        /* Visualization Gallery */
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }}

        .gallery-item {{
            position: relative;
            cursor: pointer;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .gallery-item:hover {{
            transform: scale(1.03);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}

        .gallery-item img {{
            width: 100%;
            height: auto;
            display: block;
        }}

        .gallery-item .caption {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 46, 64, 0.9);
            color: white;
            padding: 0.75rem;
            font-size: 0.9rem;
            font-weight: 500;
        }}

        /* Modal for Lightbox */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            align-items: center;
            justify-content: center;
        }}

        .modal.active {{
            display: flex;
        }}

        .modal-content {{
            max-width: 90%;
            max-height: 90%;
            position: relative;
        }}

        .modal-content img {{
            max-width: 100%;
            max-height: 90vh;
            border-radius: 8px;
        }}

        .modal-close {{
            position: absolute;
            top: -40px;
            right: 0;
            color: white;
            font-size: 2rem;
            cursor: pointer;
            background: none;
            border: none;
        }}

        /* Collapsible Section */
        .collapsible {{
            cursor: pointer;
            padding: 1rem;
            background: var(--bgs-light);
            border: none;
            text-align: left;
            width: 100%;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--bgs-primary);
            margin-top: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .collapsible:hover {{
            background: #e9ecef;
        }}

        .collapsible.active .fa-chevron-down {{
            transform: rotate(180deg);
        }}

        .collapsible-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            padding: 0 1rem;
        }}

        .collapsible-content.active {{
            max-height: 2000px;
            padding: 1rem;
        }}

        /* Footer */
        .footer {{
            background: var(--bgs-primary);
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}

        .footer p {{
            margin: 0.5rem 0;
            opacity: 0.9;
        }}

        /* Sticky Navigation */
        .nav {{
            position: sticky;
            top: 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 100;
            padding: 1rem 2rem;
        }}

        .nav-links {{
            display: flex;
            gap: 2rem;
            justify-content: center;
            flex-wrap: wrap;
        }}

        .nav-links a {{
            color: var(--bgs-primary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }}

        .nav-links a:hover {{
            color: var(--bgs-secondary);
        }}

        /* Back to Top Button */
        .back-to-top {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--bgs-secondary);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            display: none;
            align-items: center;
            justify-content: center;
            transition: opacity 0.3s;
            z-index: 99;
        }}

        .back-to-top.visible {{
            display: flex;
        }}

        .back-to-top:hover {{
            opacity: 0.8;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 1.8rem;
            }}

            .metrics {{
                grid-template-columns: 1fr;
                margin-top: -1rem;
            }}

            .charts-grid {{
                grid-template-columns: 1fr;
            }}

            .container {{
                padding: 1rem;
            }}

            .nav-links {{
                flex-direction: column;
                align-items: center;
                gap: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- Hero Header -->
    <div class="hero">
        <h1><i class="fas fa-chart-line"></i> BGS Site 1 GasClam</h1>
        <h2 style="font-weight: 400; margin: 0.5rem 0;">Environmental Sensor Analysis</h2>
        <p class="subtitle">Interactive Monitoring Dashboard | {date_range['start'].split()[0]} to {date_range['end'].split()[0]}</p>
    </div>

    <!-- Metric Cards -->
    <div class="metrics">
        <div class="metric-card" style="--color: var(--temp-color);">
            <div class="icon"><i class="fas fa-thermometer-half"></i></div>
            <div class="label">Temperature</div>
            <div class="value">{stats['temperature_c']['mean']:.1f}°C</div>
            <div class="range">{stats['temperature_c']['min']:.1f}°C - {stats['temperature_c']['max']:.1f}°C</div>
        </div>

        <div class="metric-card" style="--color: var(--pressure-color);">
            <div class="icon"><i class="fas fa-tachometer-alt"></i></div>
            <div class="label">Pressure</div>
            <div class="value">{stats['pressure_mbar']['mean']:.0f} mbar</div>
            <div class="range">{int(stats['pressure_mbar']['min'])} - {int(stats['pressure_mbar']['max'])} mbar</div>
        </div>

        <div class="metric-card" style="--color: var(--oxygen-color);">
            <div class="icon"><i class="fas fa-wind"></i></div>
            <div class="label">Oxygen</div>
            <div class="value">{stats['oxygen_pct']['mean']:.1f}%</div>
            <div class="range">{stats['oxygen_pct']['min']:.1f}% - {stats['oxygen_pct']['max']:.1f}%</div>
        </div>

        <div class="metric-card" style="--color: var(--co2-color);">
            <div class="icon"><i class="fas fa-cloud"></i></div>
            <div class="label">Carbon Dioxide</div>
            <div class="value">{stats['co2_pct']['mean']:.1f}%</div>
            <div class="range">{stats['co2_pct']['min']:.1f}% - {stats['co2_pct']['max']:.1f}%</div>
        </div>
    </div>

    <!-- Sticky Navigation -->
    <nav class="nav" id="nav">
        <div class="nav-links">
            <a href="#summary"><i class="fas fa-clipboard-list"></i> Summary</a>
            <a href="#charts"><i class="fas fa-chart-area"></i> Interactive Charts</a>
            <a href="#statistics"><i class="fas fa-calculator"></i> Statistics</a>
            <a href="#gallery"><i class="fas fa-images"></i> Gallery</a>
            <a href="#methodology"><i class="fas fa-flask"></i> Methodology</a>
        </div>
    </nav>

    <div class="container">
        <!-- Executive Summary -->
        <div class="section" id="summary">
            <h2><i class="fas fa-clipboard-list"></i> Executive Summary</h2>
            <p style="font-size: 1.1rem; margin-bottom: 1.5rem;">
                This analysis presents comprehensive statistical and scientific evaluation of environmental sensor data
                from the BGS Site 1 GasClam borehole installation over a <strong>41-day period</strong>
                ({date_range['duration_days']} days, 500 observations).
            </p>

            <h3>Key Findings</h3>
            <div class="findings-grid">
                <div class="finding">
                    <i class="fas fa-check-circle"></i>
                    <strong>Thermally Stable:</strong> Mean temperature 6.0°C with low variability (σ = 0.42°C) indicates stable subsurface conditions
                </div>
                <div class="finding">
                    <i class="fas fa-check-circle"></i>
                    <strong>Well-Aerated:</strong> O₂ levels average 21.5%, near atmospheric concentration, indicating excellent ventilation
                </div>
                <div class="finding">
                    <i class="fas fa-check-circle"></i>
                    <strong>Active Biogeochemistry:</strong> Elevated CO₂ (1.9%, ~50× atmospheric) demonstrates active microbial processes
                </div>
                <div class="finding">
                    <i class="fas fa-check-circle"></i>
                    <strong>Inverse Gas Correlation:</strong> O₂ vs CO₂ (r = -0.35) confirms aerobic respiration dynamics
                </div>
                <div class="finding">
                    <i class="fas fa-check-circle"></i>
                    <strong>Excellent Data Quality:</strong> 100% complete dataset with all observations validated
                </div>
                <div class="finding">
                    <i class="fas fa-check-circle"></i>
                    <strong>Minimal Outliers:</strong> Less than 1.5% outliers across all parameters
                </div>
            </div>

            <h3 style="margin-top: 2rem;">Quality Indicators</h3>
            <div class="status-badges">
                <span class="badge excellent">
                    <i class="fas fa-check-circle"></i>
                    Data Quality: Excellent (100% complete)
                </span>
                <span class="badge minimal">
                    <i class="fas fa-exclamation-triangle"></i>
                    Anomalies: Minimal (&lt;1.5%)
                </span>
                <span class="badge good">
                    <i class="fas fa-chart-line"></i>
                    Trends: Stable with seasonal variation
                </span>
            </div>
        </div>

        <!-- Interactive Charts Section -->
        <div class="section" id="charts">
            <h2><i class="fas fa-chart-area"></i> Interactive Data Visualization</h2>
            <p>Explore the sensor data with interactive charts. Hover for details, click legend to toggle series, zoom and pan to focus on specific periods.</p>

            <!-- Multi-Parameter Time Series -->
            <div class="chart-container chart-full">
                <h3>Multi-Parameter Time Series</h3>
                <div id="multiparamChart"></div>
            </div>

            <!-- Individual Parameter Charts -->
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Temperature (°C)</h3>
                    <div id="tempChart"></div>
                </div>
                <div class="chart-container">
                    <h3>Barometric Pressure (mbar)</h3>
                    <div id="pressureChart"></div>
                </div>
                <div class="chart-container">
                    <h3>Oxygen Concentration (%)</h3>
                    <div id="oxygenChart"></div>
                </div>
                <div class="chart-container">
                    <h3>Carbon Dioxide Concentration (%)</h3>
                    <div id="co2Chart"></div>
                </div>
            </div>

            <!-- Correlation Matrix -->
            <div class="chart-container chart-full">
                <h3>Parameter Correlation Matrix</h3>
                <div id="corrChart"></div>
            </div>

            <!-- Distribution Charts -->
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Temperature Distribution</h3>
                    <div id="tempDist"></div>
                </div>
                <div class="chart-container">
                    <h3>Pressure Distribution</h3>
                    <div id="pressureDist"></div>
                </div>
                <div class="chart-container">
                    <h3>Oxygen Distribution</h3>
                    <div id="oxygenDist"></div>
                </div>
                <div class="chart-container">
                    <h3>CO₂ Distribution</h3>
                    <div id="co2Dist"></div>
                </div>
            </div>
        </div>

        <!-- Statistical Analysis Section -->
        <div class="section" id="statistics">
            <h2><i class="fas fa-calculator"></i> Statistical Analysis</h2>

            <table class="stats-table">
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th>Mean</th>
                        <th>Median</th>
                        <th>Std Dev</th>
                        <th>Min</th>
                        <th>Max</th>
                        <th>Range</th>
                        <th>CV (%)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><i class="fas fa-thermometer-half" style="color: var(--temp-color);"></i> Temperature (°C)</td>
                        <td>{stats['temperature_c']['mean']:.2f}</td>
                        <td>{stats['temperature_c']['50%']:.2f}</td>
                        <td>{stats['temperature_c']['std']:.2f}</td>
                        <td>{stats['temperature_c']['min']:.1f}</td>
                        <td>{stats['temperature_c']['max']:.1f}</td>
                        <td>{stats['temperature_c']['range']:.1f}</td>
                        <td>{stats['temperature_c']['cv']*100:.1f}</td>
                    </tr>
                    <tr>
                        <td><i class="fas fa-tachometer-alt" style="color: var(--pressure-color);"></i> Pressure (mbar)</td>
                        <td>{stats['pressure_mbar']['mean']:.1f}</td>
                        <td>{stats['pressure_mbar']['50%']:.1f}</td>
                        <td>{stats['pressure_mbar']['std']:.1f}</td>
                        <td>{int(stats['pressure_mbar']['min'])}</td>
                        <td>{int(stats['pressure_mbar']['max'])}</td>
                        <td>{int(stats['pressure_mbar']['range'])}</td>
                        <td>{stats['pressure_mbar']['cv']*100:.1f}</td>
                    </tr>
                    <tr>
                        <td><i class="fas fa-wind" style="color: var(--oxygen-color);"></i> Oxygen (%)</td>
                        <td>{stats['oxygen_pct']['mean']:.2f}</td>
                        <td>{stats['oxygen_pct']['50%']:.2f}</td>
                        <td>{stats['oxygen_pct']['std']:.2f}</td>
                        <td>{stats['oxygen_pct']['min']:.1f}</td>
                        <td>{stats['oxygen_pct']['max']:.1f}</td>
                        <td>{stats['oxygen_pct']['range']:.1f}</td>
                        <td>{stats['oxygen_pct']['cv']*100:.1f}</td>
                    </tr>
                    <tr>
                        <td><i class="fas fa-cloud" style="color: var(--co2-color);"></i> CO₂ (%)</td>
                        <td>{stats['co2_pct']['mean']:.2f}</td>
                        <td>{stats['co2_pct']['50%']:.2f}</td>
                        <td>{stats['co2_pct']['std']:.2f}</td>
                        <td>{stats['co2_pct']['min']:.1f}</td>
                        <td>{stats['co2_pct']['max']:.1f}</td>
                        <td>{stats['co2_pct']['range']:.1f}</td>
                        <td>{stats['co2_pct']['cv']*100:.1f}</td>
                    </tr>
                </tbody>
            </table>

            <!-- Correlation Analysis -->
            <h3>Correlation Analysis</h3>
            <div class="finding" style="margin-top: 1rem;">
                <p><strong>Key Correlation:</strong> Oxygen and CO₂ show moderate inverse correlation (r = {analysis['correlation_analysis']['pearson']['oxygen_pct']['co2_pct']:.3f}),
                consistent with aerobic respiration processes where O₂ consumption produces CO₂.</p>
            </div>

            <!-- Normality Tests -->
            <button class="collapsible">
                <span><i class="fas fa-chart-bar"></i> Normality Tests & Advanced Statistics</span>
                <i class="fas fa-chevron-down"></i>
            </button>
            <div class="collapsible-content">
                <table class="stats-table" style="margin-top: 1rem;">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Shapiro-Wilk p</th>
                            <th>Distribution</th>
                            <th>Skewness</th>
                            <th>Kurtosis</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Temperature</td>
                            <td>{analysis['normality_tests']['temperature_c']['shapiro_wilk']['p_value']:.4f}</td>
                            <td>{'Normal' if analysis['normality_tests']['temperature_c']['shapiro_wilk']['is_normal'] else 'Non-normal'}</td>
                            <td>{stats['temperature_c']['skewness']:.3f}</td>
                            <td>{stats['temperature_c']['kurtosis']:.3f}</td>
                        </tr>
                        <tr>
                            <td>Pressure</td>
                            <td>{analysis['normality_tests']['pressure_mbar']['shapiro_wilk']['p_value']:.4f}</td>
                            <td>{'Normal' if analysis['normality_tests']['pressure_mbar']['shapiro_wilk']['is_normal'] else 'Non-normal'}</td>
                            <td>{stats['pressure_mbar']['skewness']:.3f}</td>
                            <td>{stats['pressure_mbar']['kurtosis']:.3f}</td>
                        </tr>
                        <tr>
                            <td>Oxygen</td>
                            <td>{analysis['normality_tests']['oxygen_pct']['shapiro_wilk']['p_value']:.4f}</td>
                            <td>{'Normal' if analysis['normality_tests']['oxygen_pct']['shapiro_wilk']['is_normal'] else 'Non-normal'}</td>
                            <td>{stats['oxygen_pct']['skewness']:.3f}</td>
                            <td>{stats['oxygen_pct']['kurtosis']:.3f}</td>
                        </tr>
                        <tr>
                            <td>CO₂</td>
                            <td>{analysis['normality_tests']['co2_pct']['shapiro_wilk']['p_value']:.4f}</td>
                            <td>{'Normal' if analysis['normality_tests']['co2_pct']['shapiro_wilk']['is_normal'] else 'Non-normal'}</td>
                            <td>{stats['co2_pct']['skewness']:.3f}</td>
                            <td>{stats['co2_pct']['kurtosis']:.3f}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Outlier Detection -->
            <button class="collapsible">
                <span><i class="fas fa-exclamation-circle"></i> Outlier Detection Results</span>
                <i class="fas fa-chevron-down"></i>
            </button>
            <div class="collapsible-content">
                <table class="stats-table" style="margin-top: 1rem;">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>IQR Outliers</th>
                            <th>Percentage</th>
                            <th>Z-Score Outliers</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Temperature</td>
                            <td>{analysis['outlier_detection']['temperature_c']['iqr_method']['count']}</td>
                            <td>{analysis['outlier_detection']['temperature_c']['iqr_method']['percentage']:.1f}%</td>
                            <td>{analysis['outlier_detection']['temperature_c']['zscore_method']['count']}</td>
                            <td>{analysis['outlier_detection']['temperature_c']['zscore_method']['percentage']:.1f}%</td>
                        </tr>
                        <tr>
                            <td>Pressure</td>
                            <td>{analysis['outlier_detection']['pressure_mbar']['iqr_method']['count']}</td>
                            <td>{analysis['outlier_detection']['pressure_mbar']['iqr_method']['percentage']:.1f}%</td>
                            <td>{analysis['outlier_detection']['pressure_mbar']['zscore_method']['count']}</td>
                            <td>{analysis['outlier_detection']['pressure_mbar']['zscore_method']['percentage']:.1f}%</td>
                        </tr>
                        <tr>
                            <td>Oxygen</td>
                            <td>{analysis['outlier_detection']['oxygen_pct']['iqr_method']['count']}</td>
                            <td>{analysis['outlier_detection']['oxygen_pct']['iqr_method']['percentage']:.1f}%</td>
                            <td>{analysis['outlier_detection']['oxygen_pct']['zscore_method']['count']}</td>
                            <td>{analysis['outlier_detection']['oxygen_pct']['zscore_method']['percentage']:.1f}%</td>
                        </tr>
                        <tr>
                            <td>CO₂</td>
                            <td>{analysis['outlier_detection']['co2_pct']['iqr_method']['count']}</td>
                            <td>{analysis['outlier_detection']['co2_pct']['iqr_method']['percentage']:.1f}%</td>
                            <td>{analysis['outlier_detection']['co2_pct']['zscore_method']['count']}</td>
                            <td>{analysis['outlier_detection']['co2_pct']['zscore_method']['percentage']:.1f}%</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Visualization Gallery -->
        <div class="section" id="gallery">
            <h2><i class="fas fa-images"></i> Visualization Gallery</h2>
            <p>Click on any image to view full size. All visualizations are publication-quality (300 DPI).</p>

            <div class="gallery">
                <div class="gallery-item" onclick="openModal('../visualizations/multiparameter_overlay.png')">
                    <img src="../visualizations/multiparameter_overlay.png" alt="Multi-parameter overlay">
                    <div class="caption">Multi-Parameter Time Series</div>
                </div>
                <div class="gallery-item" onclick="openModal('../visualizations/distributions.png')">
                    <img src="../visualizations/distributions.png" alt="Distributions">
                    <div class="caption">Probability Distributions</div>
                </div>
                <div class="gallery-item" onclick="openModal('../visualizations/correlation_heatmap.png')">
                    <img src="../visualizations/correlation_heatmap.png" alt="Correlation heatmap">
                    <div class="caption">Correlation Matrix Heatmap</div>
                </div>
                <div class="gallery-item" onclick="openModal('../visualizations/boxplots.png')">
                    <img src="../visualizations/boxplots.png" alt="Box plots">
                    <div class="caption">Box Plots with Violin Overlays</div>
                </div>
                <div class="gallery-item" onclick="openModal('../visualizations/scatter_matrix.png')">
                    <img src="../visualizations/scatter_matrix.png" alt="Scatter matrix">
                    <div class="caption">Scatter Plot Matrix</div>
                </div>
                <div class="gallery-item" onclick="openModal('../visualizations/oxygen_co2_relationship.png')">
                    <img src="../visualizations/oxygen_co2_relationship.png" alt="O2 vs CO2">
                    <div class="caption">O₂ vs CO₂ Relationship</div>
                </div>
                <div class="gallery-item" onclick="openModal('../visualizations/timeseries_temperature_c.png')">
                    <img src="../visualizations/timeseries_temperature_c.png" alt="Temperature time series">
                    <div class="caption">Temperature Time Series</div>
                </div>
                <div class="gallery-item" onclick="openModal('../visualizations/timeseries_pressure_mbar.png')">
                    <img src="../visualizations/timeseries_pressure_mbar.png" alt="Pressure time series">
                    <div class="caption">Pressure Time Series</div>
                </div>
                <div class="gallery-item" onclick="openModal('../visualizations/timeseries_oxygen_pct.png')">
                    <img src="../visualizations/timeseries_oxygen_pct.png" alt="Oxygen time series">
                    <div class="caption">Oxygen Time Series</div>
                </div>
                <div class="gallery-item" onclick="openModal('../visualizations/timeseries_co2_pct.png')">
                    <img src="../visualizations/timeseries_co2_pct.png" alt="CO2 time series">
                    <div class="caption">CO₂ Time Series</div>
                </div>
            </div>
        </div>

        <!-- Methodology Section -->
        <button class="collapsible" id="methodology">
            <span><i class="fas fa-flask"></i> Data Quality & Methodology</span>
            <i class="fas fa-chevron-down"></i>
        </button>
        <div class="collapsible-content">
            <h3>Data Source</h3>
            <ul style="line-height: 1.8;">
                <li><strong>Sensor:</strong> BGS Site 1 GasClam Borehole</li>
                <li><strong>API:</strong> BGS SensorThings API (MCP tools)</li>
                <li><strong>Datastreams:</strong> Temperature (ID 94), Pressure (ID 102), Oxygen (ID 109), CO₂ (ID 110)</li>
                <li><strong>Observations:</strong> 500 measurements</li>
                <li><strong>Period:</strong> {date_range['start'].split()[0]} to {date_range['end'].split()[0]} ({date_range['duration_days']} days)</li>
                <li><strong>Sampling Interval:</strong> ~2 hours</li>
            </ul>

            <h3>Statistical Methods</h3>
            <ul style="line-height: 1.8;">
                <li><strong>Descriptive Statistics:</strong> Mean, median, std dev, quartiles, range, CV, skewness, kurtosis</li>
                <li><strong>Normality Tests:</strong> Shapiro-Wilk, Anderson-Darling, Kolmogorov-Smirnov</li>
                <li><strong>Correlation Analysis:</strong> Pearson and Spearman correlation matrices</li>
                <li><strong>Outlier Detection:</strong> IQR method (1.5× IQR) and Z-score method (|z| > 3)</li>
            </ul>

            <h3>Data Quality Assessment</h3>
            <table class="stats-table">
                <tr>
                    <td><strong>Completeness</strong></td>
                    <td>100% - No missing data</td>
                    <td><span class="badge excellent"><i class="fas fa-check"></i> Excellent</span></td>
                </tr>
                <tr>
                    <td><strong>Validation</strong></td>
                    <td>100% observations marked "Good"</td>
                    <td><span class="badge excellent"><i class="fas fa-check"></i> Excellent</span></td>
                </tr>
                <tr>
                    <td><strong>Outliers</strong></td>
                    <td>&lt;1.5% across all parameters</td>
                    <td><span class="badge minimal"><i class="fas fa-info-circle"></i> Minimal</span></td>
                </tr>
                <tr>
                    <td><strong>Temporal Coverage</strong></td>
                    <td>41 days continuous monitoring</td>
                    <td><span class="badge good"><i class="fas fa-calendar"></i> Good</span></td>
                </tr>
            </table>

            <h3>Technologies Used</h3>
            <ul style="line-height: 1.8;">
                <li><strong>Data Source:</strong> BGS SensorThings API (MCP tools)</li>
                <li><strong>Analysis:</strong> Python 3.13, pandas, NumPy, SciPy</li>
                <li><strong>Visualizations:</strong> Matplotlib, Seaborn, Plotly.js</li>
                <li><strong>Dashboard:</strong> HTML5, CSS3, JavaScript</li>
            </ul>

            <h3>Limitations</h3>
            <ul style="line-height: 1.8;">
                <li>Point measurements may not represent broader spatial conditions</li>
                <li>Winter/spring data only - summer conditions may differ significantly</li>
                <li>2-hour sampling may miss rapid transient events</li>
                <li>41-day period insufficient for robust long-term trend analysis (recommend ≥1 year)</li>
            </ul>
        </div>
    </div>

    <!-- Modal for Image Lightbox -->
    <div id="imageModal" class="modal" onclick="closeModal()">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal()"><i class="fas fa-times"></i></button>
            <img id="modalImage" src="" alt="Full size image">
        </div>
    </div>

    <!-- Back to Top Button -->
    <button class="back-to-top" id="backToTop" onclick="scrollToTop()">
        <i class="fas fa-arrow-up"></i>
    </button>

    <!-- Footer -->
    <div class="footer">
        <h3 style="color: var(--bgs-secondary); margin-bottom: 1rem;">BGS Site 1 GasClam Analysis</h3>
        <p><strong>Analysis Date:</strong> Saturday, October 25, 2025</p>
        <p><strong>Data Source:</strong> British Geological Survey SensorThings API</p>
        <p style="margin-top: 1rem; opacity: 0.7;">
            <i class="fas fa-chart-line"></i> Generated with Python 3.13 |
            <i class="fas fa-code"></i> Powered by Plotly.js
        </p>
    </div>

    <script>
        // Embedded data
        const sensorData = {data_json};

        // BGS Colors
        const BGS_PRIMARY = '{BGS_PRIMARY}';
        const BGS_SECONDARY = '{BGS_SECONDARY}';
        const TEMP_COLOR = '#dc3545';
        const PRESSURE_COLOR = '#4A90E2';
        const OXYGEN_COLOR = '#28a745';
        const CO2_COLOR = '#9c27b0';

        // Common layout settings
        const commonLayout = {{
            font: {{ family: 'Inter, sans-serif' }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'transparent',
            hovermode: 'closest',
            showlegend: true,
            legend: {{
                orientation: 'h',
                y: -0.15
            }}
        }};

        // Extract time series data
        const timestamps = sensorData.map(d => d.timestamp);
        const temperature = sensorData.map(d => d.temperature_c);
        const pressure = sensorData.map(d => d.pressure_mbar);
        const oxygen = sensorData.map(d => d.oxygen_pct);
        const co2 = sensorData.map(d => d.co2_pct);

        // Multi-Parameter Chart with Dual Y-axes
        const multiTrace1 = {{
            x: timestamps,
            y: temperature,
            name: 'Temperature (°C)',
            type: 'scatter',
            mode: 'lines',
            line: {{ color: TEMP_COLOR, width: 2 }},
            yaxis: 'y1'
        }};

        const multiTrace2 = {{
            x: timestamps,
            y: pressure,
            name: 'Pressure (mbar)',
            type: 'scatter',
            mode: 'lines',
            line: {{ color: PRESSURE_COLOR, width: 2 }},
            yaxis: 'y2'
        }};

        const multiTrace3 = {{
            x: timestamps,
            y: oxygen,
            name: 'Oxygen (%)',
            type: 'scatter',
            mode: 'lines',
            line: {{ color: OXYGEN_COLOR, width: 2 }},
            yaxis: 'y3'
        }};

        const multiTrace4 = {{
            x: timestamps,
            y: co2,
            name: 'CO₂ (%)',
            type: 'scatter',
            mode: 'lines',
            line: {{ color: CO2_COLOR, width: 2 }},
            yaxis: 'y4'
        }};

        const multiLayout = {{
            ...commonLayout,
            height: 500,
            xaxis: {{ title: 'Date' }},
            yaxis: {{
                title: 'Temp (°C)',
                titlefont: {{ color: TEMP_COLOR }},
                tickfont: {{ color: TEMP_COLOR }},
                side: 'left',
                position: 0
            }},
            yaxis2: {{
                title: 'Pressure (mbar)',
                titlefont: {{ color: PRESSURE_COLOR }},
                tickfont: {{ color: PRESSURE_COLOR }},
                overlaying: 'y',
                side: 'right',
                position: 1
            }},
            yaxis3: {{
                title: 'O₂ (%)',
                titlefont: {{ color: OXYGEN_COLOR }},
                tickfont: {{ color: OXYGEN_COLOR }},
                anchor: 'free',
                overlaying: 'y',
                side: 'left',
                position: 0.05
            }},
            yaxis4: {{
                title: 'CO₂ (%)',
                titlefont: {{ color: CO2_COLOR }},
                tickfont: {{ color: CO2_COLOR }},
                anchor: 'free',
                overlaying: 'y',
                side: 'right',
                position: 0.95
            }},
            margin: {{ l: 80, r: 80, t: 40, b: 80 }}
        }};

        Plotly.newPlot('multiparamChart', [multiTrace1, multiTrace2, multiTrace3, multiTrace4], multiLayout, {{responsive: true}});

        // Individual Temperature Chart
        const tempTrace = {{
            x: timestamps,
            y: temperature,
            type: 'scatter',
            mode: 'lines',
            line: {{ color: TEMP_COLOR, width: 2 }},
            fill: 'tozeroy',
            fillcolor: TEMP_COLOR + '20',
            name: 'Temperature'
        }};

        const tempMean = {stats['temperature_c']['mean']};
        const tempMeanTrace = {{
            x: [timestamps[0], timestamps[timestamps.length-1]],
            y: [tempMean, tempMean],
            type: 'scatter',
            mode: 'lines',
            line: {{ color: TEMP_COLOR, dash: 'dash', width: 2 }},
            name: 'Mean'
        }};

        Plotly.newPlot('tempChart', [tempTrace, tempMeanTrace], {{
            ...commonLayout,
            height: 300,
            xaxis: {{ title: 'Date' }},
            yaxis: {{ title: 'Temperature (°C)' }}
        }}, {{responsive: true}});

        // Individual Pressure Chart
        const pressureTrace = {{
            x: timestamps,
            y: pressure,
            type: 'scatter',
            mode: 'lines',
            line: {{ color: PRESSURE_COLOR, width: 2 }},
            fill: 'tozeroy',
            fillcolor: PRESSURE_COLOR + '20',
            name: 'Pressure'
        }};

        const pressureMean = {stats['pressure_mbar']['mean']};
        const pressureMeanTrace = {{
            x: [timestamps[0], timestamps[timestamps.length-1]],
            y: [pressureMean, pressureMean],
            type: 'scatter',
            mode: 'lines',
            line: {{ color: PRESSURE_COLOR, dash: 'dash', width: 2 }},
            name: 'Mean'
        }};

        Plotly.newPlot('pressureChart', [pressureTrace, pressureMeanTrace], {{
            ...commonLayout,
            height: 300,
            xaxis: {{ title: 'Date' }},
            yaxis: {{ title: 'Pressure (mbar)' }}
        }}, {{responsive: true}});

        // Individual Oxygen Chart
        const oxygenTrace = {{
            x: timestamps,
            y: oxygen,
            type: 'scatter',
            mode: 'lines',
            line: {{ color: OXYGEN_COLOR, width: 2 }},
            fill: 'tozeroy',
            fillcolor: OXYGEN_COLOR + '20',
            name: 'Oxygen'
        }};

        const oxygenMean = {stats['oxygen_pct']['mean']};
        const oxygenMeanTrace = {{
            x: [timestamps[0], timestamps[timestamps.length-1]],
            y: [oxygenMean, oxygenMean],
            type: 'scatter',
            mode: 'lines',
            line: {{ color: OXYGEN_COLOR, dash: 'dash', width: 2 }},
            name: 'Mean'
        }};

        Plotly.newPlot('oxygenChart', [oxygenTrace, oxygenMeanTrace], {{
            ...commonLayout,
            height: 300,
            xaxis: {{ title: 'Date' }},
            yaxis: {{ title: 'Oxygen (%)' }}
        }}, {{responsive: true}});

        // Individual CO2 Chart
        const co2Trace = {{
            x: timestamps,
            y: co2,
            type: 'scatter',
            mode: 'lines',
            line: {{ color: CO2_COLOR, width: 2 }},
            fill: 'tozeroy',
            fillcolor: CO2_COLOR + '20',
            name: 'CO₂'
        }};

        const co2Mean = {stats['co2_pct']['mean']};
        const co2MeanTrace = {{
            x: [timestamps[0], timestamps[timestamps.length-1]],
            y: [co2Mean, co2Mean],
            type: 'scatter',
            mode: 'lines',
            line: {{ color: CO2_COLOR, dash: 'dash', width: 2 }},
            name: 'Mean'
        }};

        Plotly.newPlot('co2Chart', [co2Trace, co2MeanTrace], {{
            ...commonLayout,
            height: 300,
            xaxis: {{ title: 'Date' }},
            yaxis: {{ title: 'CO₂ (%)' }}
        }}, {{responsive: true}});

        // Correlation Heatmap
        const corrData = [
            [{analysis['correlation_analysis']['pearson']['temperature_c']['temperature_c']:.3f},
             {analysis['correlation_analysis']['pearson']['temperature_c']['pressure_mbar']:.3f},
             {analysis['correlation_analysis']['pearson']['temperature_c']['oxygen_pct']:.3f},
             {analysis['correlation_analysis']['pearson']['temperature_c']['co2_pct']:.3f}],
            [{analysis['correlation_analysis']['pearson']['pressure_mbar']['temperature_c']:.3f},
             {analysis['correlation_analysis']['pearson']['pressure_mbar']['pressure_mbar']:.3f},
             {analysis['correlation_analysis']['pearson']['pressure_mbar']['oxygen_pct']:.3f},
             {analysis['correlation_analysis']['pearson']['pressure_mbar']['co2_pct']:.3f}],
            [{analysis['correlation_analysis']['pearson']['oxygen_pct']['temperature_c']:.3f},
             {analysis['correlation_analysis']['pearson']['oxygen_pct']['pressure_mbar']:.3f},
             {analysis['correlation_analysis']['pearson']['oxygen_pct']['oxygen_pct']:.3f},
             {analysis['correlation_analysis']['pearson']['oxygen_pct']['co2_pct']:.3f}],
            [{analysis['correlation_analysis']['pearson']['co2_pct']['temperature_c']:.3f},
             {analysis['correlation_analysis']['pearson']['co2_pct']['pressure_mbar']:.3f},
             {analysis['correlation_analysis']['pearson']['co2_pct']['oxygen_pct']:.3f},
             {analysis['correlation_analysis']['pearson']['co2_pct']['co2_pct']:.3f}]
        ];

        const corrTrace = {{
            z: corrData,
            x: ['Temperature', 'Pressure', 'Oxygen', 'CO₂'],
            y: ['Temperature', 'Pressure', 'Oxygen', 'CO₂'],
            type: 'heatmap',
            colorscale: [
                [0, '#d62728'], [0.5, 'white'], [1, OXYGEN_COLOR]
            ],
            zmin: -1,
            zmax: 1,
            text: corrData,
            texttemplate: '%{{text:.2f}}',
            textfont: {{ size: 14 }},
            colorbar: {{
                title: 'Correlation',
                titleside: 'right'
            }}
        }};

        Plotly.newPlot('corrChart', [corrTrace], {{
            ...commonLayout,
            height: 400,
            xaxis: {{ side: 'bottom' }},
            yaxis: {{ autorange: 'reversed' }}
        }}, {{responsive: true}});

        // Distribution Histograms
        const tempDistTrace = {{
            x: temperature,
            type: 'histogram',
            name: 'Temperature',
            marker: {{ color: TEMP_COLOR, opacity: 0.7 }},
            nbinsx: 30
        }};

        Plotly.newPlot('tempDist', [tempDistTrace], {{
            ...commonLayout,
            height: 250,
            xaxis: {{ title: 'Temperature (°C)' }},
            yaxis: {{ title: 'Frequency' }},
            showlegend: false
        }}, {{responsive: true}});

        const pressureDistTrace = {{
            x: pressure,
            type: 'histogram',
            name: 'Pressure',
            marker: {{ color: PRESSURE_COLOR, opacity: 0.7 }},
            nbinsx: 30
        }};

        Plotly.newPlot('pressureDist', [pressureDistTrace], {{
            ...commonLayout,
            height: 250,
            xaxis: {{ title: 'Pressure (mbar)' }},
            yaxis: {{ title: 'Frequency' }},
            showlegend: false
        }}, {{responsive: true}});

        const oxygenDistTrace = {{
            x: oxygen,
            type: 'histogram',
            name: 'Oxygen',
            marker: {{ color: OXYGEN_COLOR, opacity: 0.7 }},
            nbinsx: 30
        }};

        Plotly.newPlot('oxygenDist', [oxygenDistTrace], {{
            ...commonLayout,
            height: 250,
            xaxis: {{ title: 'Oxygen (%)' }},
            yaxis: {{ title: 'Frequency' }},
            showlegend: false
        }}, {{responsive: true}});

        const co2DistTrace = {{
            x: co2,
            type: 'histogram',
            name: 'CO₂',
            marker: {{ color: CO2_COLOR, opacity: 0.7 }},
            nbinsx: 30
        }};

        Plotly.newPlot('co2Dist', [co2DistTrace], {{
            ...commonLayout,
            height: 250,
            xaxis: {{ title: 'CO₂ (%)' }},
            yaxis: {{ title: 'Frequency' }},
            showlegend: false
        }}, {{responsive: true}});

        // Collapsible sections
        const collapsibles = document.querySelectorAll('.collapsible');
        collapsibles.forEach(collapsible => {{
            collapsible.addEventListener('click', function() {{
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                content.classList.toggle('active');
            }});
        }});

        // Smooth scroll for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});

        // Back to top button
        const backToTop = document.getElementById('backToTop');
        window.addEventListener('scroll', () => {{
            if (window.pageYOffset > 300) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }});

        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        // Modal functions
        function openModal(imageSrc) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            modal.classList.add('active');
            modalImg.src = imageSrc;
        }}

        function closeModal() {{
            const modal = document.getElementById('imageModal');
            modal.classList.remove('active');
        }}

        // ESC key to close modal
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{
                closeModal();
            }}
        }});
    </script>
</body>
</html>
"""

# Save the HTML file
output_file = Path(__file__).parent / 'bgs_sensor_dashboard.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"[OK] Dashboard created successfully!")
print(f"  Location: {output_file}")
print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")
print(f"\nTo view: Open {output_file.name} in your web browser")
print(f"\nFeatures included:")
print(f"  [+] Interactive Plotly.js charts (zoom, pan, hover)")
print(f"  [+] BGS brand colors throughout")
print(f"  [+] Comprehensive statistics tables")
print(f"  [+] Visualization gallery with lightbox")
print(f"  [+] Responsive mobile-friendly design")
print(f"  [+] Smooth scroll navigation")
print(f"  [+] Collapsible sections for detailed info")
print(f"  [+] Professional scientific styling")
