
from flask import Blueprint, render_template, request, jsonify

# Create a blueprint for the CGPA calculator
cgpa_bp = Blueprint('cgpa', __name__)

def calculate_gpa(subjects, marks, credit_hours, is_first_semester, previous_cgpa=0, previous_credits=0):
    total_credits = 0
    total_points = 0
    grades = {}
    
    # Extract the numeric part from keys to match subjects with marks and credits
    for subject_key in subjects:
        # Extract the number from subject_1, subject_2, etc.
        subject_num = subject_key.split('_')[1]
        marks_key = f'marks_{subject_num}'
        credits_key = f'credits_{subject_num}'
        
        # Check if we have corresponding marks and credits
        if marks_key in marks and credits_key in credit_hours:
            mark = float(marks[marks_key])
            credit = int(credit_hours[credits_key])
            
            # Convert marks to grade points
            if mark >= 85:
                grade_point = 4.0
            elif mark >= 80:
                grade_point = 3.66
            elif mark >= 75:
                grade_point = 3.33
            elif mark >= 70:
                grade_point = 3.0
            elif mark >= 65:
                grade_point = 2.66
            elif mark >= 60:
                grade_point = 2.33
            elif mark >= 55:
                grade_point = 2.0
            elif mark >= 50:
                grade_point = 1.66
            elif mark >= 45:
                grade_point = 1.33
            elif mark >= 40:
                grade_point = 1.0
            else:
                grade_point = 0.0
            
            total_points += grade_point * credit
            total_credits += credit
            grades[subject_key] = grade_point_to_grade(grade_point)
            
            # print(f"Subject: {subjects[subject_key]}, Mark: {mark}, Credit: {credit}, Grade Point: {grade_point}")
    
    sgpa = total_points / total_credits if total_credits > 0 else 0
    
    if not is_first_semester and previous_credits > 0:
        cgpa = ((previous_cgpa * previous_credits) + (sgpa * total_credits)) / (previous_credits + total_credits)
    else:
        cgpa = sgpa
    
    # print(f"Total Points: {total_points}, Total Credits: {total_credits}, SGPA: {sgpa}, CGPA: {cgpa}")
    
    return round(sgpa, 2), round(cgpa, 2), grades

def grade_point_to_grade(grade_point):
    if grade_point == 4:
        return 'A'
    elif grade_point >= 3.66:
        return 'A-'
    elif grade_point >= 3.33:
        return 'B+'
    elif grade_point >= 3:
        return 'B'
    elif grade_point >= 2.66:
        return 'B-'
    elif grade_point >= 2.33:
        return 'C+'
    elif grade_point >= 2:
        return 'C'
    elif grade_point >= 1.66:
        return 'C-'
    elif grade_point >= 1.33:
        return 'D+'
    elif grade_point >= 1:
        return 'D'
    else:
        return 'F'

@cgpa_bp.route('/cgpa/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        # print("Raw received data:", data)
        
        # Extract subjects, marks, and credit hours
        subjects = {}
        marks = {}
        credit_hours = {}
        
        # Process all form data
        for key, value in data.items():
            # print(f"Processing: {key} = {value}")
            
            if key.startswith('subject_') and value and str(value).strip():
                subjects[key] = str(value).strip()
                # print(f"Added subject: {key} = {subjects[key]}")
                
            elif key.startswith('marks_') and value is not None and str(value).strip():
                try:
                    mark_value = float(value)
                    marks[key] = mark_value
                    # print(f"Added marks: {key} = {marks[key]}")
                except (ValueError, TypeError) as e:
                    # print(f"Error converting marks {key}: {e}")
                    continue
                    
            elif key.startswith('credits_') and value is not None:
                try:
                    credit_value = int(value)
                    credit_hours[key] = credit_value
                    # print(f"Added credits: {key} = {credit_hours[key]}")
                except (ValueError, TypeError) as e:
                    # print(f"Error converting credits {key}: {e}")
                    continue
        
        # print("Final processed data:")
        # print(f"Subjects: {subjects}")
        # print(f"Marks: {marks}")
        # print(f"Credit Hours: {credit_hours}")
        
        # Check if we have matching data
        if not subjects or not marks or not credit_hours:
            return jsonify({
                'error': 'Missing required data',
                'sgpa': 0.0,
                'cgpa': 0.0,
                'grades': {},
                'subjects': subjects,
                'marks': marks,
                'credit_hours': credit_hours
            })
        
        # Get previous semester data
        previous_cgpa = 0.0
        previous_credits = 0
        is_first_semester = True
        
        if 'previous_cgpa' in data and data['previous_cgpa']:
            try:
                previous_cgpa = float(data['previous_cgpa'])
            except (ValueError, TypeError):
                previous_cgpa = 0.0
                
        if 'previous_credits' in data and data['previous_credits']:
            try:
                previous_credits = int(data['previous_credits'])
            except (ValueError, TypeError):
                previous_credits = 0
                
        # Check if first semester (checkbox is checked when it IS first semester)
        is_first_semester = data.get('firstSemesterLabel') == 'on'
        
        # # print(f"Previous CGPA: {previous_cgpa}, Previous Credits: {previous_credits}, Is First Semester: {is_first_semester}")
        
        # Calculate GPA
        sgpa, cgpa, grades = calculate_gpa(subjects, marks, credit_hours, is_first_semester, previous_cgpa, previous_credits)
        
        response = {
            'sgpa': sgpa,
            'cgpa': cgpa,
            'grades': grades,
            'subjects': subjects,
            'marks': marks,
            'credit_hours': credit_hours
        }
        
        # print("Final response:", response)
        return jsonify(response)
        
    except Exception as e:
        # print(f"Error in calculate route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'sgpa': 0.0,
            'cgpa': 0.0,
            'grades': {},
            'subjects': {},
            'marks': {},
            'credit_hours': {}
        }), 500

