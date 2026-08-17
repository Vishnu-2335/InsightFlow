# InsightFlow – Intelligent Business Analytics Platform

🚀 **[Live Demo](https://insightflowdashboard.streamlit.app)/** | 💻 **[GitHub Repository]([YOUR_GITHUB_URL](https://github.com/Vishnu-2335/InsightFlow))**

InsightFlow is an interactive business analytics dashboard built with Python and Streamlit. It allows users to upload CSV or Excel datasets and automatically transforms the data into useful business insights, visualizations, profiling information, and advanced analytics.

The project is designed to work with datasets that may use different column names. Instead of requiring a fixed schema, InsightFlow uses automatic column-role detection to identify fields such as sales, profit, quantity, customer, product, date, category, geography, and payment method.

## Features

### 📊 Business Performance

* Total Sales
* Total Profit
* Profit Margin
* Units Sold
* Orders
* Customers
* Automated business insights
* Business recommendations

### 📈 Visual Analytics

* Sales Trend
* Category Analysis
* Geographic Analysis
* Top Product / Sub-Category Analysis
* Profit Analysis
* Payment Analysis

### 💼 Business Analysis

* Sales Growth Analysis
* Profitability Analysis
* Performance Ranking
* Sales vs Profit Analysis
* Automated Business Recommendations

### 🔍 Data Profiling

* Data Quality Overview
* Column Information
* Numeric Summary
* Missing Value Analysis
* Duplicate Record Detection
* Dataset Preview

### 🔬 Advanced Analytics

* Customer Analysis
* Product / Sub-Category Analysis
* Statistical Anomaly Detection
* Monthly Sales Anomaly Detection
* Pareto / 80-20 Analysis

## Automatic Column Detection

One of the main features of InsightFlow is its schema detection system.

The application does not depend on one specific dataset structure. It can recognize common variations such as:

| Business Role          | Possible Column Names                      |
| ---------------------- | ------------------------------------------ |
| Sales                  | Sales, Amount, Revenue, Total Amount       |
| Profit                 | Profit, Net Profit, Profit Amount          |
| Quantity               | Quantity, Qty, Units Sold                  |
| Customer               | Customer Name, CustomerName, Customer      |
| Product                | Product Name, Product, Item                |
| Product-level fallback | Sub-Category                               |
| Category               | Category, Product Category                 |
| Geography              | Region, State, City                        |
| Date                   | Order Date, Transaction Date, Sales Date   |
| Payment                | Payment Mode, Payment Method, Payment Type |

For example, a dataset containing `Amount` instead of `Sales` can still be analyzed because InsightFlow identifies `Amount` as the sales field.

If a dataset does not contain a separate Product Name column but contains `Sub-Category`, InsightFlow uses the most detailed available product-level field without incorrectly renaming the original column.

## Project Structure

```text
InsightFlow/
│
├── app.py
├── analyzer.py
├── requirements.txt
├── README.md
└── data/
    └── your_dataset.csv
```

### app.py

Contains the Streamlit application and user interface.

### analyzer.py

Contains the data processing and analytics layer, including:

* Column-role detection
* Data cleaning
* KPI calculations
* Business analysis
* Visual analysis
* Anomaly detection
* Pareto analysis
* Automated insights
* Business recommendations

### requirements.txt

Contains the Python packages required to run the project.

## Technologies Used

* Python
* Streamlit
* Pandas
* NumPy
* Plotly
* OpenPyXL

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd InsightFlow
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## How to Use

1. Launch the application.
2. Upload a CSV or Excel dataset.
3. InsightFlow automatically detects the available business columns.
4. Review the generated KPIs.
5. Use the filters to narrow the dataset.
6. Explore **Visual Analytics**.
7. Explore **Business Analysis**.
8. Use **Data Profiling** when data-quality information is required.
9. Use **Advanced Analytics** for customer, product, anomaly, and Pareto analysis.

## Anomaly Detection

InsightFlow uses statistical analysis to identify unusually high or low values.

For monthly sales analysis:

* 🔵 **Blue points** represent normal monthly sales.
* 🔴 **Red points** represent detected anomalies.
* Anomalies can indicate unusually high or low sales periods that may require further investigation.

## Why This Project?

Traditional spreadsheet dashboards often require users to manually prepare data, create formulas, build charts, and update dashboards.

InsightFlow combines these steps into an automated analytics workflow:

```text
Dataset
   ↓
Automatic Column Detection
   ↓
Data Cleaning
   ↓
KPI Calculation
   ↓
Business Analysis
   ↓
Visualization
   ↓
Advanced Analytics
   ↓
Business Insights & Recommendations
```

This makes the project more than a static dashboard. It acts as a reusable analytics tool that can work with different business datasets.

## Future Improvements

Possible future enhancements include:

* AI-powered natural language questions
* Automated data-cleaning recommendations
* More advanced anomaly detection
* Sales forecasting
* Natural-language report generation
* Database connectivity
* Cloud deployment
* Exportable business reports

## Author

Developed as a Data Analytics project demonstrating automated data processing, business intelligence, visualization, and analytical techniques.
