# Air Quality Analyzer & Visualization Suite

## Description
A data analysis and visualization tool for air quality sensor data (Temperature, PPT, Humidity, Pressure).

This project processes CSV sensor logs and generates:
- A PDF report with statistics and charts  
- An interactive HTML dashboard for exploratory analysis  
- A visualization gallery for experimenting with different chart styles  

It is designed to transform raw sensor data into insights and presentation-ready outputs.

---

## Features
- Automatic Data Analysis
  - Cleans and processes CSV sensor data
  - Computes min, max, and average statistics

- Threshold Monitoring
  - Detects values outside safe ranges
  - Generates alert summaries

- PDF Report Generation
  - Summary tables
  - Time series charts
  - Stacked area charts
  - Heatmaps (CO₂ over time)
  - 3D scatter visualizations

- Interactive HTML Dashboard
  - Multi-line time series charts
  - Heatmap visualization
  - 3D interactive scatter plots

- Visualization Gallery UI
  - Switch between multiple 3D visual styles
  - Load custom CSV files directly in browser
  - Customize color metrics and point size

- Advanced Visualizations
  - Normalized multi-metric comparison
  - Threshold zone highlighting
  - Time-based 3D data exploration

---

## Installation

### 1. Clone the repository
https://github.com/analicm/bs2026_student_projects.git

### 2. Install dependencies
pip install numpy pandas matplotlib plotly

---

## Usage

### Run the analyzer
python hello.py input.csv output_name

### Example
python hello.py sensor_data.csv report

### Output
- report.pdf → Full analytical report  
- report.html → Interactive dashboard  

---

### Open visualization gallery
Open the HTML file in your browser:

open JS_Plot.html

---

## Technologies Used

### Backend / Analysis
- Python  
- pandas  
- numpy  
- matplotlib  
- plotly  

### Frontend
- HTML5 / CSS3  
- JavaScript  
- Plotly.js  

---

## Configuration

### Expected CSV format
Date, Temperature, CO2PPM, PressureHpa, HumidityPct

---

### Threshold settings (hardcoded)
THRESHOLDS = {
    "Temperature": {"low": None, "high": 30.0},
    "CO2PPM": {"low": None, "high": 1000.0},
    "PressureHpa": {"low": 980.0, "high": 1035.0},
    "HumidityPct": {"low": 30.0, "high": 70.0},
}

---

## Summary
Raw sensor CSV → Analysis → PDF report + Interactive dashboard

---

## Author
GitHub: https://github.com/analicm
