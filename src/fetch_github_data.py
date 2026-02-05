#!/usr/bin/env python3
"""
Fetch BU course data from existing GitHub repositories.

This is the fastest way to get course data - other students have already
scraped it. We just need to normalize it to our format.

Sources:
1. bu-course-cli: https://github.com/craigxiangfu/bu-course-cli/blob/main/full_list.json
2. BU-HUB-greedy-algorithm: https://github.com/wyatt-howe/BU-HUB-greedy-algorithm/blob/master/catalog/catalog.json

Usage:
    python fetch_github_data.py --output data/courses.json

Or manually:
    1. Download full_list.json from bu-course-cli repo
    2. Run: python fetch_github_data.py --input full_list.json --output data/courses.json
"""

import json
import re
import sys
from pathlib import Path


def normalize_code(code: str) -> str:
    """
    Normalize course code to "CAS CS 111" format.
    
    Handles:
    - "CASCS111" -> "CAS CS 111"
    - "CAS CS111" -> "CAS CS 111" 
    - "CDS DS 100" -> "CDS DS 100"
    """
    code = ' '.join(code.split())
    
    # Already good format
    if re.match(r'^[A-Z]{2,4} [A-Z]{2} \d{3}', code):
        return code
    
    # Compressed format: "CASCS111"
    match = re.match(r'^([A-Z]{2,4})([A-Z]{2})(\d{3})$', code.replace(' ', ''))
    if match:
        return f"{match.group(1)} {match.group(2)} {match.group(3)}"
    
    return code


def generate_id(code: str, section: str, term: str) -> str:
    """Generate unique course ID."""
    code_normalized = code.replace(' ', '-')
    term_normalized = term.replace(' ', '')
    return f"{code_normalized}-{section}-{term_normalized}"


def parse_schedule_string(s: str) -> list[dict]:
    """Parse schedule string like 'MWF 10:10-11:00 @ CAS 313'."""
    if not s:
        return []
    
    # Try pattern: "days time-time location"
    match = re.match(
        r'([A-Za-z]+)\s+(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})(?:\s+(?:@\s*)?(.+))?',
        s.strip()
    )
    
    if match:
        return [{
            'days': match.group(1),
            'start_time': match.group(2),
            'end_time': match.group(3),
            'location': (match.group(4) or '').strip(),
        }]
    
    return []


def convert_course(item: dict, default_term: str = "Fall 2026") -> dict:
    """Convert a course from GitHub format to our format."""
    # Extract code
    code = (
        item.get('course_code') or 
        item.get('code') or 
        item.get('courseCode') or
        ''
    )
    
    if not code:
        return None
    
    code = normalize_code(code)
    
    # Extract college and department from code
    parts = code.split()
    college = parts[0] if len(parts) >= 1 else 'CAS'
    department = parts[1] if len(parts) >= 2 else 'XX'
    
    # Section
    section = item.get('section', 'A1')
    
    # Term
    term = item.get('term') or item.get('semester') or default_term
    
    # Schedule
    schedule = []
    if 'schedule' in item:
        if isinstance(item['schedule'], list):
            for s in item['schedule']:
                if isinstance(s, dict):
                    schedule.append({
                        'days': s.get('days', ''),
                        'start_time': s.get('start_time') or s.get('start', ''),
                        'end_time': s.get('end_time') or s.get('end', ''),
                        'location': s.get('location', ''),
                    })
                elif isinstance(s, str):
                    schedule.extend(parse_schedule_string(s))
        elif isinstance(item['schedule'], str):
            schedule = parse_schedule_string(item['schedule'])
    
    # Hub units
    hub_units = item.get('BU_Hub') or item.get('hub_units') or item.get('hub') or []
    if isinstance(hub_units, str):
        hub_units = [hub_units]
    
    return {
        'id': generate_id(code, section, term),
        'code': code,
        'title': item.get('course_title') or item.get('title') or item.get('name', ''),
        'description': item.get('description', ''),
        'section': section,
        'professor': item.get('professor') or item.get('instructor') or item.get('instructors', 'TBA'),
        'term': term,
        'credits': int(item.get('credits', 4)),
        'hub_units': hub_units,
        'department': department,
        'college': college,
        'schedule': schedule,
    }


def process_github_data(input_data: list | dict, default_term: str = "Fall 2026") -> list[dict]:
    """Process GitHub course data into our format."""
    # Handle different data structures
    if isinstance(input_data, dict):
        items = list(input_data.values())
    else:
        items = input_data
    
    courses = []
    seen_ids = set()
    
    for item in items:
        if not isinstance(item, dict):
            continue
        
        course = convert_course(item, default_term)
        if course and course['id'] not in seen_ids:
            courses.append(course)
            seen_ids.add(course['id'])
    
    # Sort by code
    courses.sort(key=lambda c: c['code'])
    
    return courses


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert GitHub BU course data to our format')
    parser.add_argument('--input', '-i', help='Input JSON file (if not provided, uses sample data)')
    parser.add_argument('--output', '-o', default='data/courses.json', help='Output file')
    parser.add_argument('--term', default='Fall 2026', help='Default term')
    args = parser.parse_args()
    
    if args.input:
        print(f"Reading from {args.input}...")
        with open(args.input) as f:
            input_data = json.load(f)
    else:
        # Generate larger sample data for testing
        print("No input file provided. Generating sample data...")
        input_data = generate_sample_data()
    
    courses = process_github_data(input_data, args.term)
    
    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(courses, f, indent=2)
    
    print(f"Converted {len(courses)} courses -> {args.output}")
    
    # Print summary
    depts = set(c['department'] for c in courses)
    print(f"Departments: {len(depts)}")
    print(f"Sample: {', '.join(sorted(depts)[:10])}")


def generate_sample_data() -> list[dict]:
    """Generate realistic sample course data for testing."""
    
    # Real BU departments and course prefixes
    departments = {
        'CS': ('Computer Science', ['Introduction to Computer Science', 'Data Structures', 
               'Analysis of Algorithms', 'Computer Systems', 'Concepts of Programming Languages',
               'Database Systems', 'Software Engineering', 'Machine Learning', 'Computer Networks',
               'Operating Systems', 'Compilers', 'Artificial Intelligence', 'Computer Graphics']),
        'MA': ('Mathematics', ['Calculus I', 'Calculus II', 'Multivariate Calculus', 'Linear Algebra',
               'Differential Equations', 'Probability', 'Statistics', 'Abstract Algebra',
               'Real Analysis', 'Complex Analysis', 'Number Theory', 'Topology']),
        'EC': ('Economics', ['Introductory Microeconomics', 'Introductory Macroeconomics',
               'Intermediate Microeconomics', 'Intermediate Macroeconomics', 'Econometrics',
               'Game Theory', 'International Trade', 'Public Finance', 'Labor Economics']),
        'PH': ('Philosophy', ['Introduction to Philosophy', 'Ethics', 'Logic', 'Epistemology',
               'Metaphysics', 'Philosophy of Mind', 'Political Philosophy', 'Aesthetics']),
        'PY': ('Physics', ['General Physics I', 'General Physics II', 'Modern Physics',
               'Electromagnetism', 'Quantum Mechanics', 'Thermodynamics', 'Classical Mechanics']),
        'BI': ('Biology', ['Introduction to Biology I', 'Introduction to Biology II', 'Genetics',
               'Cell Biology', 'Ecology', 'Biochemistry', 'Molecular Biology', 'Neuroscience']),
        'CH': ('Chemistry', ['General Chemistry I', 'General Chemistry II', 'Organic Chemistry I',
               'Organic Chemistry II', 'Physical Chemistry', 'Analytical Chemistry', 'Biochemistry']),
        'WR': ('Writing', ['First-Year Writing Seminar', 'Advanced Writing', 'Research Writing']),
        'HI': ('History', ['World History I', 'World History II', 'American History',
               'European History', 'Asian History', 'Modern History', 'Ancient History']),
        'SO': ('Sociology', ['Introduction to Sociology', 'Social Theory', 'Research Methods',
               'Urban Sociology', 'Race and Ethnicity', 'Social Inequality']),
    }
    
    # Hub requirements
    hub_options = [
        ['Quantitative Reasoning I'],
        ['Quantitative Reasoning II'],
        ['Scientific Inquiry I'],
        ['Scientific Inquiry II'],
        ['Social Inquiry I'],
        ['Social Inquiry II'],
        ['Philosophical Inquiry'],
        ['Historical Consciousness'],
        ['Critical Thinking'],
        ['Writing-Intensive Course'],
        ['First-Year Writing Seminar'],
        ['Oral/Signed Communication'],
        ['Digital/Multimedia Expression'],
        ['Ethical Reasoning'],
        ['Global Citizenship'],
        ['Research and Information Literacy'],
    ]
    
    # Meeting time patterns
    time_slots = [
        ('MWF', '08:00', '08:50'),
        ('MWF', '09:05', '09:55'),
        ('MWF', '10:10', '11:00'),
        ('MWF', '11:15', '12:05'),
        ('MWF', '12:20', '13:10'),
        ('MWF', '13:25', '14:15'),
        ('MWF', '14:30', '15:20'),
        ('TuTh', '08:00', '09:15'),
        ('TuTh', '09:30', '10:45'),
        ('TuTh', '11:00', '12:15'),
        ('TuTh', '12:30', '13:45'),
        ('TuTh', '14:00', '15:15'),
        ('TuTh', '15:30', '16:45'),
        ('TuTh', '17:00', '18:15'),
    ]
    
    # Locations
    locations = ['CAS 313', 'CAS 226', 'CAS 522', 'CAS 211', 'CAS 224',
                 'CGS 129', 'CGS 515', 'PSY B51', 'PSY B53', 'STH 105',
                 'PHO 210', 'PHO 206', 'EPC 201', 'EPC 203', 'LSE 103']
    
    # Professor last names
    professors = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
                  'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
                  'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
                  'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
                  'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King']
    
    courses = []
    course_num = 100
    
    import random
    random.seed(42)  # Reproducible
    
    for dept, (dept_name, course_titles) in departments.items():
        for i, title in enumerate(course_titles):
            num = 100 + i * 10 + random.randint(0, 9)
            
            # Generate 1-3 sections per course
            for section_idx in range(random.randint(1, 3)):
                section = f"A{section_idx + 1}"
                slot = random.choice(time_slots)
                
                courses.append({
                    'course_code': f'CAS {dept} {num}',
                    'course_title': title,
                    'section': section,
                    'professor': f'Dr. {random.choice(professors)}',
                    'credits': 4,
                    'BU_Hub': random.choice(hub_options) if random.random() > 0.3 else [],
                    'description': f'An introduction to {title.lower()} covering fundamental concepts and applications.',
                    'schedule': [{
                        'days': slot[0],
                        'start_time': slot[1],
                        'end_time': slot[2],
                        'location': random.choice(locations),
                    }],
                })
    
    return courses


if __name__ == '__main__':
    main()
