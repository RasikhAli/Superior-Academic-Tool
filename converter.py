from openpyxl.utils import get_column_letter
from openpyxl import load_workbook
from datetime import datetime
import pandas as pd
import re
import os

def convert_xlsx_to_csv(input_filename, output_filename=None):
    """
    Convert Excel timetable to CSV format
    
    Parameters:
    input_filename (str): Path to the input XLSX file
    output_filename (str, optional): Path to the output CSV file. If None, 
                                    will use input filename with .csv extension
    
    Returns:
    str: Path to the created CSV file
    """
    # If output_filename not provided, derive from input_filename
    if output_filename is None:
        output_filename = os.path.splitext(input_filename)[0] + '.csv'
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Load workbook and worksheet
    wb = load_workbook(filename=input_filename)
    ws = wb.active

    # Define layout structure
    day_blocks = [
        {"day_cell": "B5", "room_rows": range(7, 21),  "time_row": 5},
        {"day_cell": "B21", "room_rows": range(23, 36), "time_row": 22},
        {"day_cell": "B36", "room_rows": range(38, 52), "time_row": 37},
        {"day_cell": "B52", "room_rows": range(54, 67), "time_row": 53},
        {"day_cell": "B67", "room_rows": range(69, 83), "time_row": 68},
        {"day_cell": "B83", "room_rows": range(85, 92), "time_row": 84},
        {"day_cell": "B92", "room_rows": range(94, 99), "time_row": 93},
    ]

    time_cols = range(4, 11)  # D to J

    # Read merged cell values correctly
    merged_cells = ws.merged_cells.ranges

    def fix_class_group_format(class_group_str):
        if not class_group_str:
            return class_group_str
            
        # Format 1: BSDS/BSAI-6A → BSDS-6A & BSAI-6A
        class_group_str = re.sub(
            r'\b([A-Z]{4})/([A-Z]{4})-(\d+[A-Za-z]*)\b',
            r'\1-\3 & \2-\3',
            class_group_str
        )
        
        # Format 2: BSAI-1A/BSDS-1A → BSAI-1A & BSDS-1A
        class_group_str = re.sub(
            r'\b([A-Z]{4}-\d+[A-Za-z]*)/([A-Z]{4}-\d+[A-Za-z]*)\b',
            r'\1 & \2',
            class_group_str
        )

        # Format 3: BSSE-2A,2B,2C,2D,2E → BSSE-2A & BSSE-2B & BSSE-2C & BSSE-2D & BSSE-2E
        class_group_str = re.sub(
            r'([A-Z]{4}-\d+[A-Za-z]*)[,]([A-Z]{4}-\d+[A-Za-z]*)',
            r'\1 & \2',
            class_group_str
        )

        return class_group_str


    def get_cell_value(row, col):
        cell = ws.cell(row=row, column=col)
        coord = f"{get_column_letter(col)}{row}"
        for merged in merged_cells:
            if coord in merged:
                return ws.cell(merged.min_row, merged.min_col).value
        return cell.value

    # Extract structured timetable
    rows = []

    for block in day_blocks:
        raw_day = ws[block["day_cell"]].value
        if isinstance(raw_day, datetime):
            day = raw_day.strftime("%A")
        else:
            day = str(raw_day).strip()

        time_row = block["time_row"]
        room_rows = block["room_rows"]

        # Get all time slots (from D to J)
        time_slots = {col: str(get_cell_value(time_row, col)).strip() for col in time_cols}

        # Loop through each row (i.e., room) and each time slot
        for r in room_rows:
            room = get_cell_value(r, 2)  # Column B = 2 (Rooms)
            for c in time_cols:
                val = get_cell_value(r, c)
                if not val:
                    continue

                # Handle multi-line and complex cell content
                lines = [line.strip() for line in str(val).strip().split("\n") if line.strip()]

                # Skip unwanted entries
                if lines and lines[0].lower() in ["used in cs department", "namaz break"]:
                    continue

                subject = lines[0]
                groups = []
                teachers = []
                teacher_timeslot = None

                for line in lines[1:]:
                    # Detect group identifiers
                    if re.search(r'\b(BS\w{2,4})[-/]\d+[A-Za-z]*', line):
                        # Convert "BSDS/BSAI-6A" to "BSDS-6A & BSAI-6A"
                        line = fix_class_group_format(line)
                        groups.append(line)
                    else:
                        # Detect teacher and timeslot (e.g., "Ms. Kanwal Shahbaz (08:00 - 10:00)")
                        match = re.match(r"(.*)\s*\((\d{1,2}:\d{2} - \d{1,2}:\d{2})\)", line)
                        if match:
                            teacher_name = match.group(1).strip()
                            teacher_timeslot = match.group(2).strip()
                            teachers.append(teacher_name)
                        else:
                            # Consider it part of teacher names if not matched with timeslot
                            teachers.append(line)

                # If a timeslot was detected in the teacher's name, use it
                time_for_this_class = time_slots.get(c)  # Default time slot
                if teacher_timeslot:
                    time_for_this_class = teacher_timeslot

                # Apply fix_class_group_format to the entire group string
                full_groups = " & ".join(groups)  # Now this will have the proper format
                full_teachers = " ".join([t.strip().strip(",") for t in ", ".join(teachers).split(",") if t.strip()])

                # Append row with formatted data
                rows.append({
                    "Day": day,
                    "Time": time_for_this_class,
                    "Room": str(room).strip(),
                    "Subject": subject,
                    "Class/Group": fix_class_group_format(full_groups),  # Apply here
                    "Teacher(s) Name": full_teachers
                })

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    def fix_time_format(time_str):
        # Normalize all time ranges to have exactly one space before and after the dash
        return re.sub(r'\s*-\s*', ' - ', time_str.strip())

    # Apply fixes
    df['Time'] = df['Time'].apply(fix_time_format)
    df['Class/Group'] = df['Class/Group'].apply(fix_class_group_format)

    # Output
    df.to_csv(output_filename, index=False)
    print(f"Converted {input_filename} to {output_filename}")
    
    return output_filename

# If run directly, use the hardcoded filename
if __name__ == "__main__":
    input_file = 'Timetable SE Department (Fall-25) UpdatedVersion - 1.1.xlsx'
    convert_xlsx_to_csv(input_file)
