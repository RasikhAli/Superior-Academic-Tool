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
- **Teacher Timetables**: View and manage individual teacher schedules
- **Section Timetables**: Access class section schedules with ease
- **Smart Search**: Quick search functionality with Select2 integration
- **Automatic Conversion**: Seamless XLSX to CSV conversion for timetable data
- **Real-time Updates**: Dynamic loading of timetable information

### 🎓 CGPA Calculator
- **Semester GPA Calculation**: Calculate current semester GPA (SGPA)
- **Cumulative GPA**: Compute overall CGPA across all semesters
- **Flexible Input**: Support for multiple subjects with varying credit hours
- **Grade Breakdown**: Detailed grade analysis for each subject
- **First Semester Support**: Special handling for first-semester students
- **Previous Semester Integration**: Include previous CGPA and credit hours
- **Real-time Calculation**: Instant results as you enter marks

### 🎨 ShadowText Studio
- **Gradient Text Effects**: Create stunning text with customizable gradient colors
- **Shadow Customization**: Adjust shadow intensity and angle
- **Live Preview**: Real-time preview of your design
- **Export Options**: Download full image or auto-cropped version
- **Theme Support**: Works seamlessly in both light and dark modes
- **Professional Output**: High-quality PNG exports

### 🎯 User Interface
- **Modern Dashboard**: Clean, intuitive interface with card-based layout
- **Dark/Light Theme**: Toggle between themes for comfortable viewing
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Smooth Animations**: Polished transitions and hover effects
- **Professional Styling**: Beautiful gradients and modern design patterns

## 🏗️ Project Structure

```
Superior-Academic-Tool/
├── app.py                    # Main Flask application with all routes
├── converter.py              # XLSX to CSV converter for timetables
├── cgpa_calculator.py        # CGPA calculation logic and grading system
├── shadowtext_studio.py      # ShadowText Studio blueprint for text effects
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── LICENSE.md                # MIT License
├── .gitignore                # Git ignore rules
├── templates/
│   └── index.html            # Main unified dashboard template
├── static/
│   ├── styles.css            # Comprehensive CSS styles with theme support
│   ├── script.js             # JavaScript for timetable and UI functionality
│   ├── generated.png         # Generated ShadowText images (runtime)
│   └── generated_cropped.png # Cropped ShadowText images (runtime)
├── uploads/                  # Uploaded timetable files
│   ├── csv/                  # Converted CSV timetable files
│   └── xlsx/                 # Original XLSX timetable files
└── venv/                     # Virtual environment (created after setup)
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

2. **Create a virtual environment:**
```bash
python -m venv venv
```

3. **Activate the virtual environment:**
- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Run the application:**
```bash
python app.py
```

6. **Access the dashboard:**
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 📖 Usage Guide

### Timetable Management

1. **Upload Timetable:**
   - Place your XLSX timetable file in `uploads/xlsx/` directory
   - The app automatically converts it to CSV format
   - Latest file is used by default

2. **View Teacher Timetable:**
   - Click "Teacher Timetable" in the sidebar
   - Select a teacher from the dropdown
   - View their complete weekly schedule

3. **View Section Timetable:**
   - Click "Section Timetable" in the sidebar
   - Select a section from the dropdown
   - View the section's complete schedule

### CGPA Calculator

1. **Access Calculator:**
   - Click "CGPA Calculator" in the sidebar or dashboard card

2. **For First Semester Students:**
   - Keep the "First Semester" toggle ON
   - Enter subject names, credit hours, and marks
   - Results update automatically

3. **For Other Semesters:**
   - Toggle "First Semester" to OFF
   - Enter previous CGPA and total credit hours
   - Add current semester subjects
   - View both SGPA and CGPA

4. **Add/Remove Subjects:**
   - Click "Add Another Subject" to add more subjects
   - Click "Remove" to delete a subject
   - Minimum one subject required

### ShadowText Studio

1. **Access Studio:**
   - Click "ShadowText Studio" in the sidebar or dashboard card

2. **Create Text Effect:**
   - Enter your text in the text area
   - Choose top and bottom gradient colors
   - Adjust shadow intensity (0-10)
   - Adjust shadow angle (0-360°)
   - Preview updates in real-time

3. **Export Your Design:**
   - Click "Generate Image" to create the effect
   - Click "Download Image" for full-size PNG
   - Click "Crop & Download" for auto-cropped version

### Theme Toggle

- Click the sun/moon icon in the top-right corner
- Switch between light and dark themes
- Theme preference is saved automatically

## 🛠️ Technologies Used

### Backend
- **Flask 3.0+** - Web framework
- **Pandas 2.0+** - Data processing and analysis
- **Pillow (PIL)** - Image processing for ShadowText Studio
- **NumPy** - Numerical computations

### Frontend
- **Bootstrap 4.5** - Responsive UI framework
- **jQuery 3.5** - JavaScript library
- **Select2** - Enhanced select dropdowns
- **Font Awesome 6.0** - Icon library
- **Custom CSS** - Modern styling with theme support

### Data Processing
- **openpyxl** - XLSX file handling
- **CSV** - Timetable data storage

## 🎯 Key Features Explained

### Automatic Timetable Conversion
The app automatically detects the latest XLSX file in the `uploads/xlsx/` directory and converts it to CSV format for efficient processing. This happens on startup and ensures you're always working with the most recent data.

### Intelligent CGPA Calculation
The CGPA calculator uses Superior University's grading system:
- A+ (90-100): 4.00 GPA
- A (85-89): 3.70 GPA
- A- (80-84): 3.30 GPA
- B+ (75-79): 3.00 GPA
- B (71-74): 2.70 GPA
- B- (68-70): 2.30 GPA
- C+ (64-67): 2.00 GPA
- C (61-63): 1.70 GPA
- C- (58-60): 1.30 GPA
- D+ (54-57): 1.00 GPA
- D (50-53): 0.70 GPA
- F (0-49): 0.00 GPA

### ShadowText Studio Algorithm
Creates professional text effects using:
- PIL (Python Imaging Library) for image generation
- Gradient color interpolation
- Dynamic shadow rendering with customizable angles
- Automatic cropping to remove excess whitespace
- High-quality PNG export

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Make your changes**
4. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
5. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
6. **Open a Pull Request**

### Contribution Guidelines
- Follow PEP 8 style guide for Python code
- Add comments for complex logic
- Update README.md if adding new features
- Test thoroughly before submitting PR

## 🐛 Known Issues & Troubleshooting

### Port Already in Use
If you see "Address already in use" error:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### XLSX File Not Loading
- Ensure the file is in `uploads/xlsx/` directory
- Check file format is valid XLSX
- Verify file is not corrupted

### CGPA Calculator Not Updating
- Ensure marks are between 0-100
- Check that credit hours are selected
- Verify JavaScript is enabled in browser

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/RasikhAli/Superior-Academic-Tool?style=social)
![GitHub forks](https://img.shields.io/github/forks/RasikhAli/Superior-Academic-Tool?style=social)
![GitHub issues](https://img.shields.io/github/issues/RasikhAli/Superior-Academic-Tool)
![GitHub license](https://img.shields.io/github/license/RasikhAli/Superior-Academic-Tool)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 👨‍💻 Author

**Rasikh Ali**
- GitHub: [@RasikhAli](https://github.com/RasikhAli)
- LinkedIn: [Rasikh Ali](https://www.linkedin.com/in/rasikh-ali/)

## 🙏 Acknowledgments

- Superior University for the academic framework
- Flask community for excellent documentation
- Bootstrap team for the responsive framework
- All contributors who help improve this project

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/RasikhAli/Superior-Academic-Tool/issues) page
2. Create a new issue with detailed description
3. Contact the developer through GitHub

---

<div align="center">
  <p>Made with ❤️ by Rasikh Ali</p>
  <p>⭐ Star this repository if you find it helpful!</p>
</div>
