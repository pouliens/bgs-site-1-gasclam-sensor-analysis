# BGS Sensor Data Analysis Project

**Professional environmental sensor data analysis with interactive dashboard**

---

## What We Built

A comprehensive scientific analysis system for BGS Site 1 GasClam borehole environmental monitoring data, featuring:

- **Interactive Dashboard**: Professional HTML dashboard with BGS branding and Plotly visualizations
- **Statistical Analysis**: Complete EDA with normality tests, correlation analysis, and outlier detection
- **Scientific Visualizations**: 10 publication-quality plots (300 DPI)
- **Expert Interpretation**: 11-page scientific findings document
- **Full Documentation**: Reproducible analysis with complete methodology

---

## Key Results

**Dataset**: 500 observations over 41 days (Jan 30 - Mar 13, 2025)
**Data Quality**: 100% complete, all validated

| Parameter | Mean | Range | Key Finding |
|-----------|------|-------|-------------|
| Temperature | 6.0°C | 4.9-7.1°C | Thermally stable subsurface conditions |
| Pressure | 1015 mbar | 988-1041 mbar | Normal atmospheric variations |
| Oxygen | 21.5% | 16.0-24.3% | Well-aerated environment |
| CO₂ | 1.9% | 0.1-3.5% | Active biogeochemical processes |

**Correlation**: O₂ vs CO₂ (r = -0.35) confirms aerobic respiration dynamics

---

## Quick Access

### View Dashboard
```
Open: dashboard/index.html
```
Interactive plots with zoom, pan, and hover capabilities.

### Read Scientific Findings
```
Read: analysis/findings.md (11 pages)
```
Detailed interpretation with environmental and geotechnical implications.

### Explore Visualizations
```
Browse: visualizations/ (10 PNG files, 300 DPI)
```
Publication-ready static plots.

### Raw Data & Analysis
```
Data: data/raw_sensor_data.csv
Results: analysis/eda_analysis.json
```

---

## Technologies Used

- **Data Source**: BGS SensorThings API (MCP tools)
- **Analysis**: Python 3.13 (pandas, NumPy, SciPy)
- **Visualizations**: Matplotlib, Seaborn, Plotly
- **Dashboard**: HTML5 with Plotly.js
- **Branding**: BGS colors (#002E40, #AD9C70)

---

## Skills Demonstrated

✅ MCP tool integration (BGS SensorThings API)
✅ Exploratory data analysis with scientific-thinking skill
✅ Statistical analysis (normality tests, correlations, outliers)
✅ Scientific visualization (publication-quality)
✅ Interactive dashboard development
✅ Professional documentation
✅ Scientific interpretation and reporting

---

## Reproducibility

All analysis is fully reproducible:

```bash
# Regenerate analysis
python analysis/custom_eda.py

# Regenerate visualizations
python visualizations/create_visualizations.py

# Regenerate dashboard
python dashboard/generate_simple_dashboard.py
```

---

## Project Impact

This analysis provides:

1. **Baseline data** for long-term environmental monitoring
2. **Scientific insights** into subsurface gas dynamics
3. **Professional deliverables** suitable for publications
4. **Reusable methodology** for similar datasets
5. **Interactive tools** for stakeholder engagement

---

**Created**: March 2025
**Analysis Tool**: Claude Code with scientific-thinking skills
**Data Source**: British Geological Survey
