# Superior Academic Tool

![Superior Academic Tool](https://img.shields.io/badge/Superior-Academic%20Tool-blue?style=for-the-badge&logo=graduation-cap)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-red?style=for-the-badge&logo=flask)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-orange?style=for-the-badge&logo=pandas)
![Data Analysis](https://img.shields.io/badge/Data-Analysis-purple?style=for-the-badge&logo=chart-line)
![Academic](https://img.shields.io/badge/Academic-Management-yellow?style=for-the-badge&logo=book)

A comprehensive academic management platform designed to streamline educational data processing, timetable management, CGPA calculation, and creative text design - all in one unified dashboard.

## ✨ Features

### 📅 Timetable Management
- **Teacher Timetables**: View and manage individual teacher schedules with hierarchical name parsing (Dr, Prof, Ms, etc.).
- **Section Timetables**: Access class section schedules with automatic group expansion (e.g., BSSE-5A & 5B).
- **Room/Lab Timetables**: Dedicated view for room and laboratory schedules to track occupancy.
- **Semester Identification**: Automatically extracts semester info (e.g., Fall-25 & Spring-26) from filenames.
- **Smart Search**: Quick search functionality with Select2 integration and autocomplete.
- **Automatic Conversion**: Robust XLSX to CSV conversion with real-time file modification tracking.
- **Export Options**: Download semester-specific timetables as Excel files directly from the dashboard.

### 🎓 CGPA Calculator
- **Semester GPA Calculation**: Calculate current semester GPA (SGPA) based on marks and credit hours.
- **Cumulative GPA**: Compute overall CGPA using previous semester data.
- **Flexible Input**: Dynamic subject addition/removal with automatic calculation.
- **Grade Breakdown**: Instant grade assignment according to Superior University's latest grading scheme.
- **First Semester Support**: Toggle between first-semester and continuing student modes.

### 🎨 ShadowText Studio
- **Gradient Text Effects**: Create stunning text with customizable top and bottom gradient colors.
- **Shadow Customization**: Precision controls for font size, shadow intensity (alpha), and shadow angle.
- **Live Preview**: Rapid image generation with high-quality preview rendering.
- **Export Suite**: Download full-size designs or use the "Crop & Download" feature for perfect framing.
- **Responsive Canvas**: High-quality PNG output optimized for presentations and profile headers.

### 🎯 User Interface
- **Modern Dashboard**: Professional card-based layout with real-time stats (Total Teachers, Sections, Rooms).
- **Persistent Sidebar**: Improved navigation with quick access to all modules and developer info.
- **Dynamic Theme Engine**: Toggle between Sun (Light) and Moon (Dark) modes with persistent local storage.
- **Last Updated Tracking**: Header display showing exactly when the current data was last modified.

## 🏗️ Project Structure

```
Superior-Academic-Tool/
├── app.py                    # Main Flask application with advanced routing and API endpoints
├── converter.py              # XLSX to CSV converter for timetables
├── cgpa_calculator.py        # CGPA calculation logic and official grading system blueprint
├── shadowtext_studio.py      # ShadowText Studio blueprint for image generation
├── requirements.txt          # Python dependencies (Flask, Pandas, PIL, etc.)
├── README.md                 # Project documentation
├── LICENSE.md                # MIT License
├── templates/
│   └── index.html            # Main unified dashboard template with modular sections
├── static/
│   ├── styles.css            # Modern CSS with custom scrollbars, glassmorphism, and theme tokens
│   ├── script.js             # Core frontend logic, AJAX handlers, and UI interactions
│   └── ...                   # Asset files and generated outputs
├── uploads/                  # Data storage
│   ├── csv/                  # Converted CSV timetable files
│   └── xlsx/                 # Source XLSX timetable files
└── venv/                     # Virtual environment
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Steps

1. **Clone the repository:**
```bash
git clone https://github.com/RasikhAli/Superior-Academic-Tool.git
cd Superior-Academic-Tool
```

2. **Create and Activate Virtual Environment:**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the Application:**
```bash
python app.py
```

5. **Access the Dashboard:**
Navigate to `http://127.0.0.1:5000` (or `http://localhost:10000` depending on environment).

## 📖 Usage Guide

### Timetable Management

1. **Upload Data**: Place XLSX timetable files in `uploads/xlsx/`. The app detects the latest file and updates automatically.
2. **Search**: Use the dropdowns in the Teacher, Section, or Room sections to filter data.
3. **Downloads**: In the Section Timetable area, use the dedicated download buttons to get specific semester schedules in Excel format.

### CGPA Calculator

1. **Student Status**: Choose "Yes" for 1st Semester or "No" to input previous CGPA/Credits.
2. **Entry**: Enter subject names, select credit hours (1-4), and type in marks (0-100).
3. **Live Sync**: Calculation happens instantly as you type; results are displayed in prominent cards.

### ShadowText Studio

1. **Design**: Fill in your text, pick your colors using the color picker, and fine-tune with sliders.
2. **Generate**: Click "Generate Image" to render your design in the preview window.
3. **Save**: Use "Download" or "Crop & Download" to save your creation to your machine.

## 🛠️ Technologies Used

### Backend
- **Flask 3.0+**: Main web framework and blueprint architecture.
- **Pandas 2.0+ & openpyxl**: Advanced data processing for Excel and CSV.
- **Pillow (PIL)**: High-performance image manipulation for creative tools.
- **NumPy**: Numeric operations for gradient interpolation.

### Frontend
- **Bootstrap 4.5**: Responsive grid and UI components.
- **jQuery 3.5 & AJAX**: Smooth data fetching without page reloads.
- **Select2**: Advanced searchable dropdowns for better UX.
- **Font Awesome 6.0**: Beautiful, consistent iconography.
- **Custom CSS**: Premium dark/light themes with glassmorphism effects.

## 🎯 Key Features Explained

### Intelligent Grading System
The CGPA calculator strictly follows the latest academic standards:
- **A** (85-100): 4.00
- **A-** (80-84): 3.66
- **B+** (75-79): 3.33
- **B** (71-74): 3.00
- **B-** (68-70): 2.66
- **C+** (64-67): 2.33
- **C** (61-63): 2.00
- **C-** (58-60): 1.66
- **D** (50-57): 1.00
- **F** (0-49): 0.00

### Automated Data Pipeline
- **Hierarchical Parsing**: Correctly identifies teachers using prefixes (Dr, Prof, Sir, etc.) to ensure clean listings.
- **Merging Logic**: Automatically merges consecutive time slots for the same class/teacher to provide a readable schedule view.
- **Filename Extraction**: Uses Regex to parse semester years and version numbers directly from the file system.

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/RasikhAli/Superior-Academic-Tool?style=social)
![GitHub forks](https://img.shields.io/github/forks/RasikhAli/Superior-Academic-Tool?style=social)
![GitHub issues](https://img.shields.io/github/issues/RasikhAli/Superior-Academic-Tool)
![GitHub license](https://img.shields.io/github/license/RasikhAli/Superior-Academic-Tool)

## 🐛 Troubleshooting

### Port Already in Use
If you encounter `Address already in use`:
- **Windows**: `netstat -ano | findstr :5000` then `taskkill /PID <PID> /F`
- **Linux**: `lsof -ti:5000 | xargs kill -9`

### File Format Issues
- Ensure your timetable files are in `.xlsx` format.
- Names should contain semester info like `Fall-25` for automatic detection.

## 👨‍💻 Author

**Rasikh Ali**
- GitHub: [@RasikhAli](https://github.com/RasikhAli)
- LinkedIn: [Rasikh Ali](https://www.linkedin.com/in/rasikh-ali/)

## 🙏 Acknowledgments

- Superior University for the academic framework context.
- The Flask & Pandas communities for their robust libraries.
- All users who provide feedback to improve this tool.

---

<div align="center">
  <p>Made with ❤️ by <b>Rasikh Ali</b></p>
  <p>⭐ Star this repository if you find it helpful!</p>
</div>
