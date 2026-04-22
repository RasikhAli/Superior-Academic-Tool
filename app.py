from flask import Flask, request, render_template, jsonify, send_file
import csv
from io import BytesIO
import os
from datetime import datetime
import re
import glob
import subprocess
import sys
import importlib
import converter  # Import the converter module
from cgpa_calculator import cgpa_bp  # Import the CGPA calculator blueprint
from shadowtext_studio import shadowtext_bp  # Import the ShadowText Studio blueprint
import pandas as pd

app = Flask(__name__)

# Register the CGPA calculator blueprint
app.register_blueprint(cgpa_bp)

# Register the ShadowText Studio blueprint
app.register_blueprint(shadowtext_bp)

timetable_info = "Fall 2025 - Version 1.10"  # Default fallback


# Create required folder structure
def create_folder_structure():
    folders = ["uploads", "uploads/csv", "uploads/xlsx", "static"]
    for folder in folders:
        try:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create folder {folder}: {e}")


# Initialize folder structure
try:
    create_folder_structure()
except Exception as e:
    print(f"Warning: Could not initialize folder structure: {e}")

# Store timetable data for each teacher
timetable_data = {}
teacher_names = set()

# Valid prefixes in hierarchical order
prefix_hierarchy = ["Ms", "Mrs", "Miss", "Ma'am", "Maam", "Mr", "Sir", "Dr", "Prof"]

# Add file modification tracking
last_modified = None
current_csv_file = None


def get_latest_xlsx_file():
    """Get the latest xlsx file from uploads/xlsx folder"""
    try:
        xlsx_files = glob.glob("uploads/xlsx/*.xlsx")
        if not xlsx_files:
            print("nothing new")
            return None
        return max(xlsx_files, key=os.path.getmtime)
    except Exception as e:
        print(f"Error finding xlsx files: {e}")
        return None


def convert_xlsx_to_csv():
    """Convert latest xlsx file to csv using converter.py"""
    latest_xlsx = get_latest_xlsx_file()
    if not latest_xlsx:
        print("No xlsx files found in uploads/xlsx folder")
        return None

    # Get output filename
    output_filename = (
        "uploads/csv/" + os.path.splitext(os.path.basename(latest_xlsx))[0] + ".csv"
    )

    try:
        # Reload the converter module to ensure we get fresh code
        importlib.reload(converter)

        # Call the converter with our input and output paths
        converter.convert_xlsx_to_csv(latest_xlsx, output_filename)

        return output_filename
    except Exception as e:
        print(f"Error converting xlsx to csv: {e}")
        import traceback

        traceback.print_exc()
        return None


def get_current_csv_file():
    """Get the current CSV file to use"""
    global current_csv_file

    # Check if we need to convert xlsx to csv
    try:
        latest_xlsx = get_latest_xlsx_file()
        if latest_xlsx:
            expected_csv = (
                "uploads/csv/"
                + os.path.splitext(os.path.basename(latest_xlsx))[0]
                + ".csv"
            )

            # Convert if CSV doesn't exist or xlsx is newer
            if not os.path.exists(expected_csv) or os.path.getmtime(
                latest_xlsx
            ) > os.path.getmtime(expected_csv):
                print("Converting latest xlsx to csv...")
                converted_csv = convert_xlsx_to_csv()
                if converted_csv:
                    current_csv_file = converted_csv
            else:
                current_csv_file = expected_csv
    except Exception as e:
        print(f"Error in xlsx processing: {e}")

    # Fallback to any existing CSV in csv folder
    if not current_csv_file or not os.path.exists(current_csv_file):
        try:
            csv_files = glob.glob("uploads/csv/*.csv")
            if csv_files:
                current_csv_file = max(csv_files, key=os.path.getmtime)
        except Exception as e:
            print(f"Error finding csv files: {e}")

    return current_csv_file


def extract_semester_info(filename):
    """
    Extract semester information from filename
    Handles both single and multiple semesters
    Example: "Fall-25 & Spring-26" returns "Fall-25 & Spring-26"
    """
    # Pattern to match semester info like "Fall-25", "Spring-26", etc.
    # This will capture multiple semesters separated by &
    semester_pattern = (
        r"((?:Fall|Spring|Summer)-\d{2}(?:\s*&\s*(?:Fall|Spring|Summer)-\d{2})*)"
    )
    match = re.search(semester_pattern, filename, re.IGNORECASE)

    if match:
        return match.group(1)

    return "Current Semester"


def extract_timetable_info(filename):
    """
    Extract timetable info from filename
    Example: "Timetable SE Department (Fall-25 & Spring-26) Version-1.0.xlsx"
    Returns: "Fall 2025 & Spring 2026 - Version 1.0"
    """
    # Extract the base filename without path and extension
    base_filename = os.path.basename(filename)
    base_filename = os.path.splitext(base_filename)[0]

    # Pattern to match semester info like "Fall-25", "Spring-26", etc.
    # This will capture multiple semesters separated by &
    semester_pattern = (
        r"((?:Fall|Spring|Summer)-\d{2}(?:\s*&\s*(?:Fall|Spring|Summer)-\d{2})*)"
    )
    semester_match = re.search(semester_pattern, base_filename, re.IGNORECASE)

    # Pattern to match version info like "Version-1.0", "Version 1.0", "v1.0", etc.
    version_pattern = r"(?:Version|Ver|v)[\s-]*(\d+\.\d+)"
    version_match = re.search(version_pattern, base_filename, re.IGNORECASE)

    result_parts = []

    if semester_match:
        semester_str = semester_match.group(1)

        # Convert "Fall-25 & Spring-26" to "Fall 2025 & Spring 2026"
        def expand_semester(match):
            season = match.group(1)
            year = match.group(2)
            full_year = f"20{year}"
            return f"{season} {full_year}"

        expanded_semester = re.sub(
            r"(Fall|Spring|Summer)-(\d{2})",
            expand_semester,
            semester_str,
            flags=re.IGNORECASE,
        )
        result_parts.append(expanded_semester)

    if version_match:
        version = version_match.group(1)
        result_parts.append(f"Version {version}")

    if result_parts:
        return " - ".join(result_parts)

    return "Fall 2025 - Version 1.10"  # Default fallback


def clean_teacher_name(teacher_name):
    """Clean teacher name by removing common prefixes for image path generation"""
    prefixes = [
        "DR. ",
        "DR ",
        "MR. ",
        "MR ",
        "MS. ",
        "MS ",
        "MISS ",
        "MISS. ",
        "MRS. ",
        "MRS ",
        "PROF. ",
        "PROF ",
        "SIR ",
        "MA'AM ",
        "MAAM ",
    ]
    cleaned_name = teacher_name.upper()

    for prefix in prefixes:
        if cleaned_name.startswith(prefix.upper()):
            cleaned_name = cleaned_name[len(prefix) :].strip()
            break

    return cleaned_name


def generate_teacher_image_path(teacher_name):
    """Generate image path for teacher, checking if file exists"""
    cleaned_name = clean_teacher_name(teacher_name)

    # Check for jpg first
    jpg_path = f"static/faculty/{cleaned_name}.jpg"
    if os.path.exists(jpg_path):
        return f"/static/faculty/{cleaned_name}.jpg"

    # Check for png
    png_path = f"static/faculty/{cleaned_name}.png"
    if os.path.exists(png_path):
        return f"/static/faculty/{cleaned_name}.png"

    # Fallback to profile.png
    return "/static/faculty/profile.png"


def export_to_xlsx(data, filename):
    """Export data to XLSX and return as response"""
    if data and len(data) > 0:
        if isinstance(data[0], dict):
            df = pd.DataFrame(data)
        else:
            # For simple lists
            if filename.startswith("sections"):
                df = pd.DataFrame({"Section": data})
            elif filename.startswith("rooms"):
                df = pd.DataFrame({"Room": data})
            else:
                df = pd.DataFrame({"Data": data})

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )
    else:
        # Return empty file
        output = BytesIO()
        df = pd.DataFrame()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )


@app.route("/timetable")
@app.route("/timetable/xlsx")
def get_timetable():
    name = request.args.get("name", "").upper()
    timetable_type = request.args.get(
        "type", "teacher"
    )  # 'teacher', 'section', or 'room'

    if name:
        if timetable_type == "teacher":
            data = timetable_data.get(name, [])
        elif timetable_type == "room":  # room timetable
            data = []
            for entries in timetable_data.values():
                for entry in entries:
                    location = entry.get("location", "").strip()
                    if location and name.lower() in location.lower():
                        data.append(entry)
        else:  # section timetable
            data = []
            for entries in timetable_data.values():
                for entry in entries:
                    groups = entry["groups"]
                    if groups:
                        # groups is now a list, not a string
                        if isinstance(groups, list):
                            # Check if name matches any group in the list
                            if any(name.lower() in group.lower() for group in groups):
                                data.append(entry)
                        else:
                            # Fallback for string format
                            if name.lower() in groups.lower():
                                data.append(entry)
    else:
        # Return data for all teachers
        data = [entry for entries in timetable_data.values() for entry in entries]

    # Sort the data by day and time before returning
    sorted_data = sort_entries_by_day_and_time(data)

    # Check if XLSX export is requested
    if request.path.endswith("/xlsx"):
        filename = f"timetable_{timetable_type}_{name if name else 'all'}.xlsx"
        return export_to_xlsx(sorted_data, filename)

    return jsonify(sorted_data)


@app.route("/get_sections")
@app.route("/get_sections/xlsx")
def get_sections():
    """Get all unique sections from the timetable data"""
    sections = set()
    for entries in timetable_data.values():
        for entry in entries:
            groups = entry["groups"]
            if groups:
                # groups is now a list, not a string
                if isinstance(groups, list):
                    sections.update(groups)
                else:
                    # Fallback for string format
                    group_parts = [g.strip() for g in groups.split("/")]
                    sections.update(group_parts)

    sections_list = sorted(list(sections))

    # Check if XLSX export is requested
    if request.path.endswith("/xlsx"):
        data = [{"Section": section} for section in sections_list]
        filename = "sections.xlsx"
        return export_to_xlsx(data, filename)

    return jsonify(sections_list)


@app.route("/get_rooms")
@app.route("/get_rooms/xlsx")
def get_rooms():
    """Get all unique rooms/labs from the timetable data"""
    rooms = set()
    for entries in timetable_data.values():
        for entry in entries:
            location = entry.get("location", "").strip()
            if location:
                rooms.add(location)

    rooms_list = sorted(list(rooms))

    # Check if XLSX export is requested
    if request.path.endswith("/xlsx"):
        data = [{"Room": room} for room in rooms_list]
        filename = "rooms.xlsx"
        return export_to_xlsx(data, filename)

    return jsonify(rooms_list)


@app.route("/get_teachers")
@app.route("/get_teachers/xlsx")
def get_teachers():
    """Get all teachers with their records"""
    teachers_record_file = "uploads/csv/teachers-record.csv"
    teachers_data = []

    if os.path.exists(teachers_record_file):
        with open(teachers_record_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                teachers_data.append(
                    {
                        "name": row.get("Teacher name", ""),
                        "subjects": row.get("Subjects/Courses", ""),
                        "sections": row.get("Sections", ""),
                        "office_number": row.get("Office Number", ""),
                        "superior_email": row.get("Superior email", ""),
                        "image": row.get("Teacher's Image", ""),
                        "designation": row.get("Teacher's Designation", ""),
                        "employee_code": row.get("Teacher's Employee code", ""),
                    }
                )

    # Apply search filter
    search = request.args.get("search", "").strip().lower()
    if search:
        teachers_data = [
            teacher
            for teacher in teachers_data
            if search in teacher["name"].lower()
            or search in teacher["subjects"].lower()
            or search in teacher["sections"].lower()
            or search in teacher["designation"].lower()
            or search in teacher["employee_code"].lower()
            or search in teacher["office_number"].lower()
        ]

    # Apply subject filter
    subject_filter = request.args.get("subject", "").strip()
    if subject_filter:
        teachers_data = [
            teacher
            for teacher in teachers_data
            if subject_filter in teacher["subjects"]
        ]

    # Apply section filter
    section_filter = request.args.get("section", "").strip()
    if section_filter:
        teachers_data = [
            teacher
            for teacher in teachers_data
            if section_filter in teacher["sections"]
        ]

    # Apply sorting
    sort_by = request.args.get("sort", "name")
    if sort_by == "name":
        teachers_data.sort(key=lambda x: x["name"].lower())
    elif sort_by == "designation":
        teachers_data.sort(key=lambda x: (x["designation"] or "").lower())
    elif sort_by == "subjects":
        teachers_data.sort(key=lambda x: x["subjects"].lower())
    elif sort_by == "sections":
        teachers_data.sort(key=lambda x: x["sections"].lower())
    elif sort_by == "employee_code":
        teachers_data.sort(key=lambda x: x["employee_code"] or "")
    elif sort_by == "office_number":
        teachers_data.sort(key=lambda x: x["office_number"] or "")

    # Check if XLSX export is requested
    if request.path.endswith("/xlsx"):
        filename = "teachers-record.xlsx"
        return export_to_xlsx(teachers_data, filename)

    return jsonify(teachers_data)


@app.route("/")
def index():
    global last_modified, timetable_info

    # Get current CSV file (will convert if needed)
    try:
        csv_file = get_current_csv_file()
    except Exception as e:
        print(f"Error getting CSV file: {e}")
        csv_file = None

    if not csv_file or not os.path.exists(csv_file):
        return render_template(
            "index.html",
            table_html="<p>No timetable files found. Please upload an xlsx file to uploads/xlsx folder.</p>",
            teacher_names=[],
            semester_info="No Data",
            timetable_info=timetable_info,
        )

    # Check if file has been modified
    try:
        current_modified = os.path.getmtime(csv_file)
    except Exception as e:
        print(f"Error getting file modified time: {e}")
        current_modified = None

    if last_modified != current_modified:
        try:
            process_file(csv_file)
            last_modified = current_modified
        except Exception as e:
            print(f"Error processing file: {e}")
            return render_template(
                "index.html",
                table_html=f"<p>Error processing timetable file: {str(e)}</p>",
                teacher_names=[],
                semester_info="Error",
                timetable_info=timetable_info,
            )

    # Extract semester info from filename
    try:
        semester_info = extract_semester_info(csv_file)
    except Exception as e:
        print(f"Error extracting semester info: {e}")
        semester_info = "Unknown"

    # Extract timetable info from the xlsx filename (not csv)
    try:
        latest_xlsx = get_latest_xlsx_file()
        if latest_xlsx:
            timetable_info = extract_timetable_info(latest_xlsx)
    except Exception as e:
        print(f"Error extracting timetable info: {e}")

    try:
        table_html = generate_cards_html()
        sorted_teachers = sort_teachers_by_prefix_and_name(teacher_names)
    except Exception as e:
        print(f"Error generating cards: {e}")
        table_html = ""
        sorted_teachers = []

    # Format last modified date
    try:
        last_updated = (
            datetime.fromtimestamp(last_modified).strftime("%b %d, %Y")
            if last_modified
            else "N/A"
        )
    except Exception as e:
        print(f"Error formatting date: {e}")
        last_updated = "N/A"

    return render_template(
        "index.html",
        table_html=table_html,
        teacher_names=sorted_teachers,
        semester_info=semester_info,
        timetable_info=timetable_info,
        last_updated=last_updated,
    )


def parse_multiple_teachers(teachers_str):
    """Parse multiple teachers from a string like 'Mr. John Mr. Jane Dr. Smith'"""
    teachers_str = teachers_str.strip()
    if not teachers_str:
        return []

    teachers = []
    current_teacher = ""
    words = teachers_str.split()

    for word in words:
        # Check if this word is a prefix (start of new teacher name)
        if any(word.upper().startswith(prefix.upper()) for prefix in prefix_hierarchy):
            # If we have a current teacher, add it to the list
            if current_teacher.strip():
                teachers.append(current_teacher.strip().upper())
            # Start new teacher name
            current_teacher = word
        else:
            # Continue building current teacher name
            current_teacher += " " + word

    # Add the last teacher
    if current_teacher.strip():
        teachers.append(current_teacher.strip().upper())

    return teachers


def parse_groups(group_string):
    """Parse group string and return list of individual groups"""
    if not group_string or group_string.strip() == "":
        return []

    # Clean the string
    group_string = group_string.strip()

    # Split by & and clean each part
    parts = [part.strip() for part in group_string.split("&")]
    groups = []
    current_prefix = ""

    for part in parts:
        # If part contains a dash, it's a full group name
        if "-" in part:
            groups.append(part)
            # Extract prefix for next iterations (e.g., "BSSE" from "BSSE-5A")
            current_prefix = part.split("-")[0]
        else:
            # It's just a number/suffix, use the current prefix
            if current_prefix and part:
                groups.append(f"{current_prefix}-{part}")
            elif part:
                # If no current prefix, this might be a standalone group
                groups.append(part)

    # Remove duplicates while preserving order
    seen = set()
    unique_groups = []
    for group in groups:
        if group and group not in seen:
            seen.add(group)
            unique_groups.append(group)

    return unique_groups


def create_teachers_record_csv():
    """Create teachers-record.csv with teacher information from timetable data"""
    teachers_record = {}

    # Collect data for each teacher
    for teacher, entries in timetable_data.items():
        if teacher not in teachers_record:
            teachers_record[teacher] = {
                "subjects": set(),
                "sections": set(),
                "office_number": "",
                "superior_email": "",
                "image": generate_teacher_image_path(
                    teacher
                ),  # Auto-generate image path
                "designation": "",
                "employee_code": "",
            }

        for entry in entries:
            # Add subjects (unique)
            teachers_record[teacher]["subjects"].add(entry["subject"])

            # Add sections (unique)
            if entry["groups"]:
                if isinstance(entry["groups"], list):
                    teachers_record[teacher]["sections"].update(entry["groups"])
                else:
                    teachers_record[teacher]["sections"].add(entry["groups"])

    # Check if teachers-record.csv exists and load existing data (preserve manual overrides)
    teachers_record_file = "uploads/csv/teachers-record.csv"
    if os.path.exists(teachers_record_file):
        with open(teachers_record_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                teacher_name = row.get("Teacher name", "").strip()
                if teacher_name in teachers_record:
                    teachers_record[teacher_name]["office_number"] = row.get(
                        "Office Number", ""
                    ).strip()
                    teachers_record[teacher_name]["superior_email"] = row.get(
                        "Superior email", ""
                    ).strip()
                    # Only override image if manually set in CSV, otherwise keep auto-generated path
                    manual_image = row.get("Teacher's Image", "").strip()
                    if manual_image:
                        teachers_record[teacher_name]["image"] = manual_image
                    teachers_record[teacher_name]["designation"] = row.get(
                        "Teacher's Designation", ""
                    ).strip()
                    teachers_record[teacher_name]["employee_code"] = row.get(
                        "Teacher's Employee code", ""
                    ).strip()
                    teachers_record[teacher_name]["superior_email"] = row.get(
                        "Superior email", ""
                    ).strip()
                    teachers_record[teacher_name]["image"] = row.get(
                        "Teacher's Image", ""
                    ).strip()
                    teachers_record[teacher_name]["designation"] = row.get(
                        "Teacher's Designation", ""
                    ).strip()
                    teachers_record[teacher_name]["employee_code"] = row.get(
                        "Teacher's Employee code", ""
                    ).strip()

    # Write the CSV file
    with open(teachers_record_file, "w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "Teacher name",
            "Subjects/Courses",
            "Sections",
            "Office Number",
            "Superior email",
            "Teacher's Image",
            "Teacher's Designation",
            "Teacher's Employee code",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for teacher, data in sorted(teachers_record.items()):
            writer.writerow(
                {
                    "Teacher name": teacher,
                    "Subjects/Courses": ", ".join(sorted(data["subjects"])),
                    "Sections": ", ".join(sorted(data["sections"])),
                    "Office Number": data["office_number"],
                    "Superior email": data["superior_email"],
                    "Teacher's Image": data["image"],
                    "Teacher's Designation": data["designation"],
                    "Teacher's Employee code": data["employee_code"],
                }
            )


def process_file(file_path):
    # Clear previous timetable data
    timetable_data.clear()
    teacher_names.clear()

    # Temporary storage for merging consecutive slots
    temp_entries = []

    # Read CSV file
    with open(file_path, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            day = row.get("Day", "").strip()
            time = row.get("Time", "").strip()
            room = row.get("Room", "").strip()
            subject = row.get("Subject", "").strip()
            group = row.get("Class/Group", "").strip()
            teachers_str = row.get("Teacher(s) Name", "").strip()

            # Skip empty rows or rows with F25 placeholder
            if not subject or subject == "F25" or not teachers_str:
                continue

            # Parse multiple teachers
            teachers = parse_multiple_teachers(teachers_str)

            if not teachers:
                continue

            # Add teachers to set
            for teacher in teachers:
                teacher_names.add(teacher)

            # Parse and expand groups
            expanded_groups = parse_groups(group)

            # Extract start and end time
            if "-" in time:
                start_time, end_time = [t.strip() for t in time.split("-", 1)]
            else:
                start_time = end_time = time.strip()

            temp_entry = {
                "day": day,
                "start_time": start_time,
                "end_time": end_time,
                "location": room,
                "subject": subject,
                "groups": expanded_groups,
                "teachers": teachers,
            }
            temp_entries.append(temp_entry)

    # Merge consecutive time slots
    merged_entries = merge_consecutive_slots(temp_entries)

    # Convert to final format and add to timetable_data
    for entry in merged_entries:
        # Create entry for each individual teacher
        for teacher in entry["teachers"]:
            final_entry = {
                "day": entry["day"],
                "start_time": entry["start_time"],
                "end_time": entry["end_time"],
                "location": entry["location"],
                "subject": entry["subject"],
                "groups": entry["groups"],
                "teachers": ", ".join(
                    entry["teachers"]
                ),  # Keep all teachers in the display
            }

            # Add entry to individual teacher's timetable
            if teacher in timetable_data:
                # Check for duplicates before adding
                duplicate_found = False
                for existing_entry in timetable_data[teacher]:
                    if (
                        existing_entry["day"] == final_entry["day"]
                        and existing_entry["start_time"] == final_entry["start_time"]
                        and existing_entry["end_time"] == final_entry["end_time"]
                        and existing_entry["location"] == final_entry["location"]
                        and existing_entry["subject"] == final_entry["subject"]
                    ):
                        duplicate_found = True
                        break

                if not duplicate_found:
                    timetable_data[teacher].append(final_entry)
            else:
                timetable_data[teacher] = [final_entry]

    # Sort each teacher's entries by day and time
    for teacher in timetable_data:
        timetable_data[teacher] = sort_entries_by_day_and_time(timetable_data[teacher])

    # Create teachers record CSV
    create_teachers_record_csv()


def normalize_time(time_str):
    """Normalize time format for comparison"""
    time_str = time_str.strip()
    # Handle times like "01:30" vs "1:30"
    if ":" in time_str:
        parts = time_str.split(":")
        hour = parts[0].zfill(2)  # Pad with leading zero if needed
        minute = parts[1]
        return f"{hour}:{minute}"
    return time_str


def time_to_minutes(time_str):
    """Convert time string to minutes for proper sorting"""
    time_str = normalize_time(time_str)
    if ":" in time_str:
        hour, minute = time_str.split(":")
        hour = int(hour)
        minute = int(minute)

        # Handle 12-hour format without AM/PM indicators
        # Assume times 1-7 are PM (13-19), times 8-12 are AM (8-12)
        if hour >= 1 and hour <= 7:
            hour += 12  # Convert to 24-hour format

        return hour * 60 + minute
    return 0


def merge_consecutive_slots(entries):
    """Merge consecutive time slots for same subject, teacher, room, and day"""
    if not entries:
        return []

    # Sort entries by day, start_time, subject, location, teachers
    entries.sort(
        key=lambda x: (
            x["day"],
            time_to_minutes(x["start_time"]),
            x["subject"],
            x["location"],
            str(x["teachers"]),
        )
    )

    merged = []
    current = entries[0].copy()

    for i in range(1, len(entries)):
        entry = entries[i]

        # Normalize times for comparison
        current_end = normalize_time(current["end_time"])
        entry_start = normalize_time(entry["start_time"])

        # Check if this entry can be merged with current
        same_day = current["day"] == entry["day"]
        same_subject = current["subject"] == entry["subject"]
        same_location = current["location"] == entry["location"]
        same_groups = current["groups"] == entry["groups"]
        same_teachers = set(current["teachers"]) == set(entry["teachers"])
        consecutive_time = current_end == entry_start

        if (
            same_day
            and same_subject
            and same_location
            and same_groups
            and same_teachers
            and consecutive_time
        ):
            # print(f"MERGING: {current['day']} {current['start_time']}-{current['end_time']} + {entry['start_time']}-{entry['end_time']} = {current['start_time']}-{entry['end_time']}")
            # print(f"  Subject: {current['subject']}")
            # print(f"  Location: {current['location']}")
            # print(f"  Groups: {current['groups']}")
            # print(f"  Teachers: {current['teachers']}")

            # Merge by extending end time
            current["end_time"] = entry["end_time"]
        else:
            # Can't merge, add current to merged list and start new
            merged.append(current)
            current = entry.copy()

    # Add the last entry
    merged.append(current)
    return merged


def sort_entries_by_day_and_time(entries):
    """Sort entries by day order and then by time"""
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    def day_time_key(entry):
        day = entry.get("day", "")
        start_time = entry.get("start_time", "")

        # Get day index
        day_index = day_order.index(day) if day in day_order else 999

        # Convert time to comparable format (remove colons, pad with zeros)
        time_parts = start_time.replace(":", "").strip()
        time_num = int(time_parts) if time_parts.isdigit() else 0

        return (day_index, time_num)

    return sorted(entries, key=day_time_key)


def generate_cards_html():
    card_html = ""
    sorted_teachers = sort_teachers_by_prefix_and_name(teacher_names)
    for teacher in sorted_teachers:
        entries = timetable_data.get(teacher, [])
        card_html += f'<div class="teacher-timetable" id="{teacher.replace(" ", "_")}">'
        card_html += '<div class="card">'
        card_html += (
            f'<h5 class="card-title"><i class="fas fa-user-tie"></i>{teacher}</h5>'
        )
        card_html += '<div class="table-container">'
        card_html += '<div class="table-responsive">'
        card_html += '<table class="table">'
        card_html += '<thead><tr><th><i class="fas fa-calendar-day mr-2"></i>Day</th><th><i class="fas fa-clock mr-2"></i>Start Time</th><th><i class="fas fa-clock mr-2"></i>End Time</th><th><i class="fas fa-map-marker-alt mr-2"></i>Location</th><th><i class="fas fa-book mr-2"></i>Subject</th><th><i class="fas fa-users mr-2"></i>Groups</th></tr></thead><tbody>'

        for entry in entries:
            card_html += f"<tr class='timetable-row' data-teacher='{teacher}'>"
            card_html += f"<td>{entry['day']}</td>"
            card_html += f"<td>{entry['start_time']}</td>"
            card_html += f"<td>{entry['end_time']}</td>"
            card_html += f"<td>{entry['location']}</td>"
            card_html += f"<td>{entry['subject']}</td>"
            card_html += f"<td>{entry['groups']}</td></tr>"

        card_html += "</tbody></table>"
        card_html += "</div>"
        card_html += "</div>"
        card_html += "</div>"
        card_html += "</div>"
    return card_html


def sort_teachers_by_prefix_and_name(teachers):
    def prefix_key(teacher):
        # Find the prefix in the teacher name
        for prefix in prefix_hierarchy:
            if teacher.startswith(prefix.upper()):
                return prefix_hierarchy.index(prefix)
        return len(prefix_hierarchy)  # Return a high value if no prefix is found

    # Sort teachers first by prefix key, then by name
    try:
        sorted_teachers = sorted(
            teachers, key=lambda teacher: (prefix_key(teacher), teacher)
        )
    except Exception as e:
        print(f"Error sorting teachers: {e}")
        sorted_teachers = list(teachers)

    return sorted_teachers


@app.route("/section/<int:semester>")
def get_section_by_semester(semester):
    """Get all sections for a specific semester number"""
    sections_data = []

    for entries in timetable_data.values():
        for entry in entries:
            groups = entry["groups"]
            if groups:
                if isinstance(groups, list):
                    # Check if any group contains the semester number
                    matching_groups = [
                        group for group in groups if str(semester) in group
                    ]
                    if matching_groups:
                        entry_copy = entry.copy()
                        entry_copy["groups"] = matching_groups
                        sections_data.append(entry_copy)
                else:
                    if str(semester) in groups:
                        sections_data.append(entry)

    # Sort the data by day and time before returning
    sorted_data = sort_entries_by_day_and_time(sections_data)

    return jsonify(sorted_data)


@app.route("/section/<int:semester>/download")
def download_section_by_semester(semester):
    """Download all sections for a specific semester as Excel file"""
    sections_data = []

    for entries in timetable_data.values():
        for entry in entries:
            groups = entry["groups"]
            if groups:
                if isinstance(groups, list):
                    matching_groups = [
                        group for group in groups if str(semester) in group
                    ]
                    if matching_groups:
                        for group in matching_groups:
                            entry_copy = entry.copy()
                            entry_copy["section"] = group
                            entry_copy["groups_display"] = ", ".join(
                                entry_copy["groups"]
                            )
                            sections_data.append(entry_copy)
                else:
                    if str(semester) in groups:
                        entry_copy = entry.copy()
                        entry_copy["section"] = groups
                        entry_copy["groups_display"] = groups
                        sections_data.append(entry_copy)

    if not sections_data:
        return jsonify({"error": f"No data found for semester {semester}"}), 404

    # Define day order for proper sorting
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    def get_day_index(day):
        return day_order.index(day) if day in day_order else 999

    # Sort by section first, then by day order, then by time
    sections_data.sort(
        key=lambda x: (
            x["section"],
            get_day_index(x["day"]),
            time_to_minutes(x["start_time"]),
        )
    )

    # Create DataFrame
    df_data = []
    for entry in sections_data:
        df_data.append(
            {
                "Section": entry["section"],
                "Day": entry["day"],
                "Start Time": entry["start_time"],
                "End Time": entry["end_time"],
                "Subject": entry["subject"],
                "Location": entry["location"],
                "Teachers": entry["teachers"],
            }
        )

    df = pd.DataFrame(df_data)

    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"Semester {semester}", index=False)

    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"semester_{semester}_timetable.xlsx",
    )


# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9999))
    app.run(host="0.0.0.0", port=port)
