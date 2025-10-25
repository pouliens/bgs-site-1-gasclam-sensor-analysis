#!/usr/bin/env python3
"""
Custom EDA Analysis for BGS Sensor Data
Comprehensive statistical analysis and insights generation
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

def load_data(filepath):
    """Load sensor data"""
    print(f"Loading data from: {filepath}")
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def basic_info(df):
    """Get basic dataset information"""
    info = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024**2),
        "date_range": {
            "start": str(df['timestamp'].min()),
            "end": str(df['timestamp'].max()),
            "duration_days": (df['timestamp'].max() - df['timestamp'].min()).days
        }
    }
    return info

def missing_data_analysis(df):
    """Analyze missing data patterns"""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100

    result = {col: {
        "count": int(missing[col]),
        "percentage": float(missing_pct[col])
    } for col in df.columns if missing[col] > 0}

    return result if result else {"message": "No missing data found"}

def summary_statistics(df):
    """Generate comprehensive summary statistics"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    stats_dict = {}
    for col in numeric_cols:
        data = df[col].dropna()
        stats_dict[col] = {
            "count": int(len(data)),
            "mean": float(data.mean()),
            "std": float(data.std()),
            "min": float(data.min()),
            "25%": float(data.quantile(0.25)),
            "50%": float(data.median()),
            "75%": float(data.quantile(0.75)),
            "max": float(data.max()),
            "range": float(data.max() - data.min()),
            "cv": float(data.std() / data.mean()) if data.mean() != 0 else None,
            "skewness": float(stats.skew(data)),
            "kurtosis": float(stats.kurtosis(data))
        }

    return stats_dict

def normality_tests(df):
    """Perform normality tests on numeric variables"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    results = {}
    for col in numeric_cols:
        data = df[col].dropna()

        # Shapiro-Wilk test
        if len(data) <= 5000:  # Shapiro-Wilk works best for n < 5000
            shapiro_stat, shapiro_p = stats.shapiro(data)
        else:
            shapiro_stat, shapiro_p = None, None

        # Anderson-Darling test
        anderson_result = stats.anderson(data)

        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.kstest(data, 'norm', args=(data.mean(), data.std()))

        results[col] = {
            "shapiro_wilk": {
                "statistic": float(shapiro_stat) if shapiro_stat else None,
                "p_value": float(shapiro_p) if shapiro_p else None,
                "is_normal": bool(shapiro_p > 0.05) if shapiro_p else None
            },
            "anderson_darling": {
                "statistic": float(anderson_result.statistic),
                "critical_values": anderson_result.critical_values.tolist(),
                "significance_levels": anderson_result.significance_level.tolist()
            },
            "kolmogorov_smirnov": {
                "statistic": float(ks_stat),
                "p_value": float(ks_p),
                "is_normal": bool(ks_p > 0.05)
            }
        }

    return results

def outlier_detection(df):
    """Detect outliers using IQR and Z-score methods"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    results = {}
    for col in numeric_cols:
        data = df[col].dropna()

        # IQR method
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers_iqr = data[(data < lower_bound) | (data > upper_bound)]

        # Z-score method
        z_scores = np.abs(stats.zscore(data))
        outliers_zscore = data[z_scores > 3]

        results[col] = {
            "iqr_method": {
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "count": int(len(outliers_iqr)),
                "percentage": float(len(outliers_iqr) / len(data) * 100)
            },
            "zscore_method": {
                "threshold": 3.0,
                "count": int(len(outliers_zscore)),
                "percentage": float(len(outliers_zscore) / len(data) * 100)
            }
        }

    return results

def correlation_analysis(df):
    """Analyze correlations between numeric variables"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_data = df[numeric_cols]

    # Pearson correlation
    pearson = numeric_data.corr(method='pearson')

    # Spearman correlation
    spearman = numeric_data.corr(method='spearman')

    # Find strong correlations
    strong_correlations = []
    for i in range(len(pearson.columns)):
        for j in range(i+1, len(pearson.columns)):
            col1 = pearson.columns[i]
            col2 = pearson.columns[j]
            pearson_val = pearson.iloc[i, j]
            spearman_val = spearman.iloc[i, j]

            if abs(pearson_val) > 0.5:  # Strong correlation threshold
                strong_correlations.append({
                    "variable1": col1,
                    "variable2": col2,
                    "pearson": float(pearson_val),
                    "spearman": float(spearman_val),
                    "strength": "strong" if abs(pearson_val) > 0.7 else "moderate"
                })

    return {
        "pearson": pearson.to_dict(),
        "spearman": spearman.to_dict(),
        "strong_correlations": strong_correlations
    }

def generate_insights(df, stats_summary, outliers, correlations, missing_data):
    """Generate automated insights"""
    insights = []

    # Data scale insights
    rows, cols = df.shape
    if rows > 100000:
        insights.append({
            "category": "data_scale",
            "message": f"Large dataset detected ({rows:,} rows). Consider sampling for initial exploration.",
            "severity": "info"
        })

    # Missing data insights
    if missing_data != {"message": "No missing data found"}:
        total_missing = sum([v["percentage"] for v in missing_data.values()])
        if total_missing > 5:
            insights.append({
                "category": "data_quality",
                "message": f"Significant missing data detected. Total missing: {total_missing:.1f}%",
                "severity": "warning"
            })

    # Correlation insights
    if correlations["strong_correlations"]:
        for corr in correlations["strong_correlations"]:
            insights.append({
                "category": "correlation",
                "message": f"Strong {corr['strength']} correlation between {corr['variable1']} and {corr['variable2']} (r={corr['pearson']:.2f})",
                "severity": "info"
            })

    # Outlier insights
    for col, outlier_info in outliers.items():
        if outlier_info["iqr_method"]["percentage"] > 5:
            insights.append({
                "category": "outliers",
                "message": f"High outlier rate in {col}: {outlier_info['iqr_method']['percentage']:.1f}% of observations",
                "severity": "warning"
            })

    # Distribution insights
    for col, col_stats in stats_summary.items():
        if abs(col_stats["skewness"]) > 1:
            insights.append({
                "category": "distribution",
                "message": f"{col} is highly skewed (skewness={col_stats['skewness']:.2f}). Consider transformation.",
                "severity": "info"
            })

    return insights

def main():
    # Load data
    data_file = Path(__file__).parent.parent / "data" / "raw_sensor_data.csv"
    df = load_data(data_file)

    print("\n=== Running Comprehensive EDA Analysis ===\n")

    # Run all analyses
    print("1. Basic Information...")
    basic = basic_info(df)

    print("2. Missing Data Analysis...")
    missing = missing_data_analysis(df)

    print("3. Summary Statistics...")
    summary = summary_statistics(df)

    print("4. Normality Tests...")
    normality = normality_tests(df)

    print("5. Outlier Detection...")
    outliers = outlier_detection(df)

    print("6. Correlation Analysis...")
    correlations = correlation_analysis(df)

    print("7. Generating Insights...")
    insights = generate_insights(df, summary, outliers, correlations, missing)

    # Compile results
    results = {
        "basic_info": basic,
        "missing_data": missing,
        "summary_statistics": summary,
        "normality_tests": normality,
        "outlier_detection": outliers,
        "correlation_analysis": correlations,
        "insights": insights
    }

    # Save results
    output_file = Path(__file__).parent / "eda_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n=== Analysis Complete ===")
    print(f"Results saved to: {output_file}")
    print(f"\nKey Findings:")
    print(f"- Dataset size: {basic['shape'][0]} rows x {basic['shape'][1]} columns")
    print(f"- Date range: {basic['date_range']['start']} to {basic['date_range']['end']}")
    print(f"- Duration: {basic['date_range']['duration_days']} days")
    print(f"- Strong correlations found: {len(correlations['strong_correlations'])}")
    print(f"- Insights generated: {len(insights)}")

    print("\nTop Insights:")
    for i, insight in enumerate(insights[:5], 1):
        print(f"  {i}. [{insight['category']}] {insight['message']}")

if __name__ == "__main__":
    main()
