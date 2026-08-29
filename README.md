# 📊 Dash2BI AI — HTML Dashboard to Power BI Converter

> **Dash2BI AI** transforms existing HTML dashboard designs and dataset files (.csv, .xlsx) into production-ready **Microsoft Power BI Projects (.pbip)** with complete **PBIR** report definitions and **TMDL** tabular semantic models.

---

## 🌟 Key Features

- **4-Step User Workflow**: Upload → Analyze → Preview & Map → Convert & Download.
- **Dataset Local Profiling**: Local schema detection, numeric/date/categorical classification, data quality metrics (null %, duplicate rows, suspicious values).
- **Deep HTML Analysis Engine**: Extracts KPI cards, metric cards, charts (Bar, Column, Line, Area, Pie, Donut, Scatter, Gauge), tables, matrix structures, slicers, text boxes, and canvas layout coordinates.
- **Hybrid Semantic Mapping**: Multi-tier field matching using exact matching, case-insensitive normalization, domain synonym dictionary, token overlap, and optional **Claude 3.5 Sonnet** AI-assisted reasoning.
- **Auto DAX Measure Generation**: Synthesizes clean DAX measure expressions (`SUM`, `AVERAGE`, `COUNT`, `DISTINCTCOUNT`, `DIVIDE`) with full schema validation.
- **Valid Power BI Project (.pbip) Generation**: Directly compiles standard Microsoft Power BI Project (`.pbip`), PBIR report definitions (`definition.pbir`, `page.json`, `visual.json`), and TMDL semantic models (`model.tmdl`, `table.tmdl`).
- **Interactive 2D Spatial Wireframe**: Renders interactive 2D layout bounding boxes in Power BI canvas coordinates (1280x720).
- **Pre-Flight 10-Check Validation Engine**: Verifies schema integrity, field mappings, visual IDs, and TMDL definitions prior to export.

---

## 📁 Architecture & File Layout

```
dash2bi_ai/
├── app.py                         # Main Streamlit application entrypoint
├── .streamlit/
│   ├── config.toml                # Streamlit UI theme configuration
│   └── secrets.toml.example       # Secrets configuration template
├── src/
│   ├── data/                      # Dataset loading, sheet parsing, schema profiling & quality metrics
│   ├── html/                      # DOM parsing, CSS style extraction, JS chart library detection, visual & layout detector
│   ├── ai/                        # Anthropic Claude API provider & prompt builder
│   ├── mapping/                   # Multi-tier hybrid field mapper, visual spec mapper, confidence scoring
│   ├── dax/                       # DAX measure formula generator & syntax/schema validator
│   ├── powerbi/                   # Semantic model generator, PBIP root generator, PBIR generator, TMDL generator, ZIP packager
│   ├── preview/                   # Mapping review table UI, 2D wireframe preview UI, validation summary UI
│   └── utils/                     # Logger, error handlers, path security, upload validators
├── sample_data/
│   ├── sample_superstore.csv      # Sample CSV dataset (100 orders)
│   ├── sample_superstore.xlsx     # Sample multi-sheet Excel dataset
│   └── sample_dashboard.html      # Comprehensive HTML dashboard design
├── tests/                         # Unit test suite (dataset, html, mapping, dax, powerbi)
├── run_tests.py                   # Automated unittest test runner
├── requirements.txt               # Python package dependencies
└── README.md                      # Documentation
```

---

## ⚡ Quick Start & Local Setup

### 1. Prerequisites
- Python 3.10+
- Power BI Desktop (for opening generated `.pbip` projects)

### 2. Installation
```bash
git clone https://github.com/your-username/dash2bi-ai.git
cd dash2bi-ai
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```

### 4. Run Automated Test Suite
```bash
python run_tests.py
```

---

## 📌 Power BI Generation: PBIX vs PBIP / PBIR / TMDL

### 🔍 Technical Clarification
- **PBIX**: Power BI Desktop single-file proprietary binary report package.
- **PBIP (Power BI Project)**: Official open file directory format supported natively by Power BI Desktop.
- **PBIR (Power BI Report Definition)**: Modern JSON-based report definition format inside `.Report/` directories.
- **TMDL (Tabular Model Definition Language)**: Human-readable model definition format inside `.SemanticModel/` directories.

> [!IMPORTANT]
> **Strict Compliance**:
> Dash2BI AI generates fully compliant, valid **Power BI Projects (`.pbip`)**. 
> The application will **never** fake or rename binary files to `.pbix`.

### 🚀 Power BI Desktop Workflow
1. Download the generated `Dash2BI_PowerBI_Project.zip` from Step 4.
2. Extract the ZIP archive contents.
3. Double-click `Dash2BI_Reconstructed_Report.pbip` to open directly in **Power BI Desktop**.
4. In Power BI Desktop, click **File → Save As** and choose **Power BI Report (*.pbix)**.

---

## 🎯 Supported Visuals

| HTML Element | Power BI Visual Equivalent |
| :--- | :--- |
| KPI Card / Metric Card | Card (`card`) |
| Bar Chart | Clustered Bar Chart (`barChart`) |
| Column Chart | Clustered Column Chart (`columnChart`) |
| Line Chart | Line Chart (`lineChart`) |
| Area Chart | Area Chart (`areaChart`) |
| Pie Chart | Pie Chart (`pieChart`) |
| Donut Chart | Donut Chart (`donutChart`) |
| Scatter Chart | Scatter Chart (`scatterChart`) |
| Table / Data Table | Table (`tableEx`) |
| Dropdown Filter / Slicer | Slicer (`slicer`) |
| Date Range Selector | Date Slicer (`slicer`) |
| Dashboard Title / Text | Text Box (`textbox`) |

---

## ☁️ Streamlit Cloud Deployment

1. Push repository to GitHub.
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/) and create a **New App**.
3. Select your repository, set Main file path to `app.py`.
4. Under **Advanced Settings → Secrets**, add your Anthropic API key:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Click **Deploy!**
