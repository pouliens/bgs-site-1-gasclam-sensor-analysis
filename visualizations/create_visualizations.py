#!/usr/bin/env python3
"""
Create scientific visualizations for BGS sensor data analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for professional scientific plots
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'

def load_data():
    """Load sensor data"""
    data_file = Path(__file__).parent.parent / "data" / "raw_sensor_data.csv"
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def create_time_series_plots(df, output_dir):
    """Create individual time series plots for each parameter"""
    print("Creating time series plots...")

    parameters = [
        ('temperature_c', 'Temperature', '°C', '#1f77b4'),
        ('pressure_mbar', 'Barometric Pressure', 'mbar', '#ff7f0e'),
        ('oxygen_pct', 'Oxygen', '%', '#2ca02c'),
        ('co2_pct', 'Carbon Dioxide', '%', '#d62728')
    ]

    for col, name, unit, color in parameters:
        fig, ax = plt.subplots(figsize=(12, 5))

        ax.plot(df['timestamp'], df[col], color=color, linewidth=1, alpha=0.7)

        # Add trend line
        x_numeric = np.arange(len(df))
        z = np.polyfit(x_numeric, df[col], 1)
        p = np.poly1d(z)
        ax.plot(df['timestamp'], p(x_numeric), "--", color='gray', linewidth=2, label=f'Trend (slope={z[0]:.4f})')

        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{name} ({unit})', fontsize=12, fontweight='bold')
        ax.set_title(f'{name} Time Series - BGS Site 1 GasClam', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        # Format x-axis
        fig.autofmt_xdate()

        plt.tight_layout()
        plt.savefig(output_dir / f'timeseries_{col}.png', bbox_inches='tight')
        plt.close()

    print(f"  Created {len(parameters)} time series plots")

def create_multi_parameter_overlay(df, output_dir):
    """Create multi-parameter overlay chart"""
    print("Creating multi-parameter overlay chart...")

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 12), sharex=True)

    # Temperature
    ax1.plot(df['timestamp'], df['temperature_c'], color='#1f77b4', linewidth=1)
    ax1.set_ylabel('Temperature (°C)', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Multi-Parameter Environmental Monitoring - BGS Site 1 GasClam', fontsize=14, fontweight='bold', pad=20)

    # Pressure
    ax2.plot(df['timestamp'], df['pressure_mbar'], color='#ff7f0e', linewidth=1)
    ax2.set_ylabel('Pressure (mbar)', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Oxygen
    ax3.plot(df['timestamp'], df['oxygen_pct'], color='#2ca02c', linewidth=1)
    ax3.set_ylabel('Oxygen (%)', fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # CO2
    ax4.plot(df['timestamp'], df['co2_pct'], color='#d62728', linewidth=1)
    ax4.set_ylabel('CO₂ (%)', fontsize=11, fontweight='bold')
    ax4.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(output_dir / 'multiparameter_overlay.png', bbox_inches='tight')
    plt.close()

    print("  Created multi-parameter overlay chart")

def create_distributions(df, output_dir):
    """Create distribution plots with histograms and KDE"""
    print("Creating distribution plots...")

    parameters = [
        ('temperature_c', 'Temperature', '°C'),
        ('pressure_mbar', 'Barometric Pressure', 'mbar'),
        ('oxygen_pct', 'Oxygen', '%'),
        ('co2_pct', 'Carbon Dioxide', '%')
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, (col, name, unit) in enumerate(parameters):
        ax = axes[idx]

        # Histogram with KDE
        ax.hist(df[col], bins=30, density=True, alpha=0.7, color='skyblue', edgecolor='black')

        # Add KDE
        from scipy import stats as sp_stats
        kde = sp_stats.gaussian_kde(df[col])
        x_range = np.linspace(df[col].min(), df[col].max(), 100)
        ax.plot(x_range, kde(x_range), 'r-', linewidth=2, label='KDE')

        # Add mean and median lines
        mean_val = df[col].mean()
        median_val = df[col].median()
        ax.axvline(mean_val, color='green', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
        ax.axvline(median_val, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')

        ax.set_xlabel(f'{name} ({unit})', fontsize=10, fontweight='bold')
        ax.set_ylabel('Density', fontsize=10, fontweight='bold')
        ax.set_title(f'{name} Distribution', fontsize=11, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Parameter Distributions - BGS Site 1 GasClam', fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(output_dir / 'distributions.png', bbox_inches='tight')
    plt.close()

    print("  Created distribution plots")

def create_boxplots(df, output_dir):
    """Create box plots for outlier detection"""
    print("Creating box plots...")

    parameters = [
        ('temperature_c', 'Temperature', '°C'),
        ('pressure_mbar', 'Barometric Pressure', 'mbar'),
        ('oxygen_pct', 'Oxygen', '%'),
        ('co2_pct', 'Carbon Dioxide', '%')
    ]

    fig, axes = plt.subplots(1, 4, figsize=(16, 5))

    for idx, (col, name, unit) in enumerate(parameters):
        ax = axes[idx]

        bp = ax.boxplot([df[col]], widths=0.6, patch_artist=True,
                        boxprops=dict(facecolor='lightblue', edgecolor='black'),
                        medianprops=dict(color='red', linewidth=2),
                        whiskerprops=dict(color='black', linewidth=1.5),
                        capprops=dict(color='black', linewidth=1.5))

        ax.set_ylabel(f'{name} ({unit})', fontsize=10, fontweight='bold')
        ax.set_title(f'{name}', fontsize=11, fontweight='bold')
        ax.set_xticklabels([''])
        ax.grid(True, alpha=0.3, axis='y')

        # Add statistics annotation
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        ax.text(1.15, df[col].median(), f'Median: {df[col].median():.2f}\nIQR: {iqr:.2f}',
                fontsize=8, verticalalignment='center')

    plt.suptitle('Box Plots - Outlier Detection', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'boxplots.png', bbox_inches='tight')
    plt.close()

    print("  Created box plots")

def create_correlation_heatmap(df, output_dir):
    """Create correlation heatmap"""
    print("Creating correlation heatmap...")

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr_matrix = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                vmin=-1, vmax=1, ax=ax)

    ax.set_title('Pearson Correlation Matrix - BGS Sensor Parameters', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(output_dir / 'correlation_heatmap.png', bbox_inches='tight')
    plt.close()

    print("  Created correlation heatmap")

def create_scatter_matrix(df, output_dir):
    """Create scatter plot matrix for parameter relationships"""
    print("Creating scatter plot matrix...")

    numeric_data = df[['temperature_c', 'pressure_mbar', 'oxygen_pct', 'co2_pct']]

    # Rename columns for better labels
    numeric_data.columns = ['Temp (°C)', 'Pressure (mbar)', 'O₂ (%)', 'CO₂ (%)']

    fig = pd.plotting.scatter_matrix(numeric_data, figsize=(14, 14), alpha=0.5,
                                      diagonal='kde', color='steelblue', hist_kwds={'bins': 20})

    plt.suptitle('Parameter Relationships - Scatter Matrix', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_dir / 'scatter_matrix.png', bbox_inches='tight')
    plt.close()

    print("  Created scatter plot matrix")

def create_oxygen_co2_relationship(df, output_dir):
    """Create detailed scatter plot of O2 vs CO2 relationship"""
    print("Creating O2 vs CO2 relationship plot...")

    fig, ax = plt.subplots(figsize=(10, 8))

    scatter = ax.scatter(df['oxygen_pct'], df['co2_pct'], c=df['temperature_c'],
                         cmap='viridis', alpha=0.6, s=50, edgecolors='black', linewidth=0.5)

    # Add regression line
    z = np.polyfit(df['oxygen_pct'], df['co2_pct'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['oxygen_pct'].min(), df['oxygen_pct'].max(), 100)
    ax.plot(x_line, p(x_line), "r--", linewidth=2, label=f'Linear Fit (R²={np.corrcoef(df["oxygen_pct"], df["co2_pct"])[0,1]**2:.3f})')

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Temperature (°C)', fontsize=11, fontweight='bold')

    ax.set_xlabel('Oxygen (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Carbon Dioxide (%)', fontsize=12, fontweight='bold')
    ax.set_title('Oxygen vs Carbon Dioxide Relationship\nColored by Temperature', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'oxygen_co2_relationship.png', bbox_inches='tight')
    plt.close()

    print("  Created O2 vs CO2 relationship plot")

def main():
    # Load data
    df = load_data()

    # Create output directory
    output_dir = Path(__file__).parent
    print(f"\nGenerating visualizations to: {output_dir}\n")

    # Create all visualizations
    create_time_series_plots(df, output_dir)
    create_multi_parameter_overlay(df, output_dir)
    create_distributions(df, output_dir)
    create_boxplots(df, output_dir)
    create_correlation_heatmap(df, output_dir)
    create_scatter_matrix(df, output_dir)
    create_oxygen_co2_relationship(df, output_dir)

    print("\n=== Visualization Generation Complete ===")
    print(f"All plots saved to: {output_dir}")

if __name__ == "__main__":
    main()
