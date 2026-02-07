#!/usr/bin/env python3
"""
BU Course Scraper - Three-stage scraping

1. IScript_SubjectCourses - get list of courses per subject
2. IScript_CatalogCourseDetails - get description, Hub units, open terms
3. IScript_BrowseSections - get professors, sections, schedule, locations

Usage:
    python scrape_with_cookies.py -o data/courses.json
    python scrape_with_cookies.py --subject CASCS -o data/cs.json
    python scrape_with_cookies.py --no-details -o data/basic.json
"""

import json
import time
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)


# ============================================================================
# YOUR SESSION COOKIES (from browser DevTools)
# ============================================================================
COOKIES = {
  "79eb100099b9a8bf": "3:false:.bu.edu",
  "mybustudent-PORTAL-PSJSESSIONID": "0c3aa5a4bc992563d7867cc6e537a6e69e0b66e0",
  "_shibsession_64656661756c7468747470733a2f2f6d79627573747564656e742e62752e6564752f73702f73686962626f6c657468": "_147cb96bcc34a37cd30b8df701a42474",
  "JSESSIONID": "7fE1OqWXUIne3Z1U4j4tlEZti1fUqXsV!1627343887",
  "ExpirePage": "https://mybustudent.bu.edu/psp/BUPRD/",
  "PS_LOGINLIST": "https://mybustudent.bu.edu/BUPRD",
  "PS_TOKEN": "pQAAAAQDAgEBAAAAvAIAAAAAAAAsAAAABABTaGRyAk4AbQg4AC4AMQAwABTsCH+d98SUTV86d+zFvviB8P2PbmUAAAAFAFNkYXRhWXicHYk7CoAwEAUnUazEmxhMDFqLRAs/CFrYeQJv6OHcZB/MDOwL5JlWSvxp0pUDK4GbjYUisDNTHZxMXDyMUt7R4OiokyNjW1qM0Am92NBLW5mXDz9zWAta",
  "PS_TokenSite": "https://mybustudent.bu.edu/psp/BUPRD/?JSESSIONID",
  "SignOnDefault": "",
  "PS_LASTSITE": "https://mybustudent.bu.edu/psp/BUPRD/",
  "hpt_institution": "BU001",
  "lcsrftoken": "mCWKEnhCjLcrrFxY1B/K3oz/VoqHREuHZGzkQmZOwQU=",
  "CSRFCookie": "77507a90-51ec-4226-a74f-bdc5660e05cc",
  "PS_TOKENEXPIRE": "6_Feb_2026_23:16:46_GMT"
}


# ============================================================================
# ENDPOINTS
# ============================================================================
BASE_URL = "https://mybustudent.bu.edu/psc/BUPRD/EMPLOYEE/SA/s"
SUBJECT_COURSES_URL = f"{BASE_URL}/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_SubjectCourses"
COURSE_DETAILS_URL = f"{BASE_URL}/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_CatalogCourseDetails"
BROWSE_SECTIONS_URL = f"{BASE_URL}/WEBLIB_HCX_CM.H_BROWSE_CLASSES.FieldFormula.IScript_BrowseSections"


# ============================================================================
# TERM CODES - Map strm codes to readable names
# ============================================================================
TERM_MAP = {
    "2251": "Spring 2025",
    "2254": "Summer 1 2025",
    "2256": "Summer 2 2025",
    "2258": "Fall 2025",
    "2261": "Spring 2026",
    "2264": "Summer 1 2026",
    "2266": "Summer 2 2026",
    "2268": "Fall 2026",
}


# ============================================================================
# SUBJECTS TO SCRAPE
# ============================================================================
SUBJECTS = [
    # CAS - College of Arts & Sciences
    "CASAA", "CASAH", "CASAM", "CASAN", "CASAR", "CASAS", "CASBI", "CASCG",
    "CASCH", "CASCI", "CASCL", "CASCS", "CASEC", "CASEN", "CASGE", "CASGG",
    "CASHI", "CASIR", "CASLC", "CASLF", "CASLG", "CASLI", "CASLJ", "CASLK",
    "CASLN", "CASLO", "CASLP", "CASLR", "CASLS", "CASLT", "CASLU", "CASLW",
    "CASLX", "CASLY", "CASLZ", "CASMA", "CASNE", "CASPH", "CASPO", "CASPS",
    "CASPY", "CASRN", "CASSO", "CASWS", "CASWR",
    # CDS
    "CDSDS",
    # ENG
    "ENGBE", "ENGEC", "ENGEK", "ENGME", "ENGMS", "ENGSE",
    # COM
    "COMCM", "COMCO", "COMFT", "COMJO",
    # QST
    "QSTAC", "QSTBA", "QSTFE", "QSTIS", "QSTLA", "QSTMG", "QSTMK", "QSTOB",
    "QSTOM", "QSTQM", "QSTSI", "QSTSM",
    # CFA
    "CFAAH", "CFAFA", "CFAMU", "CFATH",
    # SAR
    "SARHS", "SARHU", "SAROT", "SARPT", "SARSH",
    # SED
    "SEDCT", "SEDDE", "SEDED", "SEDHE", "SEDSE",
    # SHA
    "SHAHF", "SHASM",
    # SPH
    "SPHBS", "SPHEP", "SPHGH", "SPHHP",
    # CGS
    "CGSRH", "CGSSS", "CGSWR",
    # KHC
    "KHCKC",
    # MET
    "METCS", "METAD",
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def parse_time(time_str: str) -> str:
    """
    Convert "12.20.00.000000" to "12:20 PM"
    """
    if not time_str:
        return ""
    
    try:
        parts = time_str.split(".")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        
        period = "AM" if hour < 12 else "PM"
        display_hour = hour
        if hour > 12:
            display_hour = hour - 12
        elif hour == 0:
            display_hour = 12
        
        return f"{display_hour}:{minute:02d} {period}"
    except (ValueError, IndexError):
        return time_str


def clean_hub_name(name: str) -> str:
    """
    Clean Hub unit name: "HUB Historical Consciousness" -> "Historical Consciousness"
    """
    if name.startswith("HUB "):
        return name[4:]
    return name


# ============================================================================
# DATA CLASSES
# ============================================================================
@dataclass
class Meeting:
    days: str
    start_time: str
    end_time: str
    location: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Course:
    code: str
    title: str
    section: str = ""
    professor: str = "TBA"
    term: str = ""
    credits: int = 4
    hub_units: list = field(default_factory=list)
    description: str = ""
    schedule: list = field(default_factory=list)
    enrollment_cap: int = 0
    enrollment_total: int = 0
    section_type: str = ""
    status: str = ""
    class_nbr: int = 0
    
    def to_dict(self) -> dict:
        return {
            'id': self.generate_id(),
            'code': self.code,
            'title': self.title,
            'section': self.section,
            'professor': self.professor,
            'term': self.term,
            'credits': self.credits,
            'hub_units': self.hub_units,
            'description': self.description,
            'schedule': [m.to_dict() if isinstance(m, Meeting) else m for m in self.schedule],
            'department': self.extract_department(),
            'college': self.extract_college(),
            'enrollment_cap': self.enrollment_cap,
            'enrollment_total': self.enrollment_total,
            'section_type': self.section_type,
            'status': self.status,
            'class_nbr': self.class_nbr,
        }
    
    def generate_id(self) -> str:
        code = self.code.replace(' ', '-')
        section = self.section or 'A1'
        term = self.term.replace(' ', '') if self.term else "Catalog"
        return f"{code}-{section}-{term}"
    
    def extract_department(self) -> str:
        parts = self.code.split()
        return parts[1] if len(parts) >= 2 else "XX"
    
    def extract_college(self) -> str:
        parts = self.code.split()
        return parts[0] if len(parts) >= 1 else "CAS"


# ============================================================================
# SCRAPER
# ============================================================================
class BUScraper:
    
    def __init__(self, delay: float = 0.15, fetch_details: bool = True):
        self.delay = delay
        self.fetch_details = fetch_details
        self.session = requests.Session()
        self.session.cookies.update(COOKIES)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
        })
    
    def test_connection(self) -> bool:
        """Test if cookies are still valid."""
        print("Testing connection...")
        try:
            resp = self.session.get(
                SUBJECT_COURSES_URL,
                params={"institution": "BU001", "x_acad_career": "UGRD", "subject": "CASCS"},
                timeout=10
            )
            
            if "login" in resp.url.lower():
                print("✗ Session expired. Please refresh cookies.")
                return False
            
            data = resp.json()
            if "courses" in data:
                print(f"✓ Connection OK ({len(data['courses'])} CS courses found)")
                return True
            
            print("✗ Unexpected response format")
            return False
            
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def scrape_all(self, subjects: list[str] = None) -> list[Course]:
        """Scrape all subjects."""
        if not self.test_connection():
            return []
        
        subjects = subjects or SUBJECTS
        all_courses = []
        
        for i, subject in enumerate(subjects):
            print(f"[{i+1}/{len(subjects)}] {subject}...", end=" ", flush=True)
            try:
                courses = self.scrape_subject(subject)
                all_courses.extend(courses)
                print(f"{len(courses)} sections")
            except Exception as e:
                print(f"error: {e}")
            
            time.sleep(self.delay)
        
        print(f"\nTotal: {len(all_courses)} course sections")
        return all_courses
    
    def scrape_subject(self, subject: str) -> list[Course]:
        """Scrape all courses for a subject."""
        # Step 1: Get course list
        resp = self.session.get(
            SUBJECT_COURSES_URL,
            params={"institution": "BU001", "x_acad_career": "UGRD", "subject": subject},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        courses = []
        course_list = data.get("courses", [])
        
        for item in course_list:
            college = subject[:3]
            dept = subject[3:]
            catalog_nbr = item.get("catalog_nbr", "").strip()
            code = f"{college} {dept} {catalog_nbr}"
            title = item.get("descr", "")
            crse_id = item.get("crse_id")
            crse_offer_nbr = item.get("crse_offer_nbr", 1)
            effdt = item.get("effdt", "")
            typ_offr = item.get("typ_offr", "")
            
            # Get base credits
            credits = 4
            offerings = item.get("offerings", [])
            if offerings:
                careers = offerings[0].get("careers", [])
                if careers:
                    max_units = careers[0].get("max_addable_units", 4)
                    if max_units and max_units < 100:
                        credits = int(max_units)
            
            # Step 2: Get course details (description, Hub units, open terms)
            description = ""
            hub_units = []
            open_term_codes = []
            
            if self.fetch_details:
                try:
                    details = self._fetch_course_details(
                        crse_id, crse_offer_nbr, effdt, subject, catalog_nbr, typ_offr
                    )
                    if details:
                        course_details = details.get("course_details", {})
                        description = course_details.get("descrlong", "")
                        
                        # Parse Hub units
                        for attr in course_details.get("attributes", []):
                            if attr.get("crse_attribute") == "HUB":
                                full_name = attr.get("crse_attribute_value_descr", "")
                                if full_name:
                                    hub_units.append(clean_hub_name(full_name))
                        
                        # Get credits
                        units_min = course_details.get("units_minimum")
                        if units_min:
                            credits = int(units_min)
                        
                        # Get open terms from offerings
                        det_offerings = course_details.get("offerings", [])
                        if det_offerings:
                            for ot in det_offerings[0].get("open_terms", []):
                                strm = ot.get("strm")
                                if strm:
                                    open_term_codes.append(strm)
                    
                    time.sleep(self.delay / 4)
                except Exception:
                    pass
                
                # Step 3: Get sections for each open term
                found_sections = False
                for term_code in open_term_codes:
                    term_name = TERM_MAP.get(term_code, f"Term {term_code}")
                    
                    try:
                        sections = self._fetch_sections(crse_id, crse_offer_nbr, term_code)
                        
                        for sec in sections:
                            found_sections = True
                            
                            course = Course(
                                code=code,
                                title=title,
                                credits=credits,
                                description=description,
                                hub_units=hub_units.copy(),
                                term=term_name,
                                section=sec.get("section", ""),
                                professor=sec.get("professor", "TBA"),
                                schedule=sec.get("schedule", []),
                                enrollment_cap=sec.get("enrollment_cap", 0),
                                enrollment_total=sec.get("enrollment_total", 0),
                                section_type=sec.get("section_type", ""),
                                status=sec.get("status", ""),
                                class_nbr=sec.get("class_nbr", 0),
                            )
                            courses.append(course)
                        
                        time.sleep(self.delay / 4)
                    except Exception:
                        pass
                
                # If no sections found, add catalog entry
                if not found_sections:
                    courses.append(Course(
                        code=code,
                        title=title,
                        credits=credits,
                        description=description,
                        hub_units=hub_units,
                        term=item.get("typ_offr_descr", ""),
                    ))
            else:
                # No details mode - just basic info
                courses.append(Course(
                    code=code,
                    title=title,
                    credits=credits,
                    term=item.get("typ_offr_descr", ""),
                ))
        
        return courses
    
    def _fetch_course_details(self, crse_id, crse_offer_nbr, effdt, subject, catalog_nbr, typ_offr) -> dict | None:
        """Fetch course description and Hub units."""
        params = {
            "institution": "BU001",
            "course_id": crse_id,
            "use_catalog_print": "Y",
            "effdt": effdt,
            "x_acad_career": "UGRD",
            "crse_offer_nbr": crse_offer_nbr,
            "subject": subject,
            "catalog_nbr": catalog_nbr,
            "typ_offr": typ_offr,
        }
        
        resp = self.session.get(COURSE_DETAILS_URL, params=params, timeout=30)
        
        if resp.status_code == 200:
            try:
                return resp.json()
            except json.JSONDecodeError:
                return None
        return None
    
    def _fetch_sections(self, crse_id: str, crse_offer_nbr: int, term_code: str) -> list[dict]:
        """Fetch sections with professors and schedules."""
        params = {
            "institution": "BU001",
            "campus": "",
            "location": "",
            "course_id": crse_id,
            "x_acad_career": "UGRD",
            "term": term_code,
            "crse_offer_nbr": crse_offer_nbr,
        }
        
        resp = self.session.get(BROWSE_SECTIONS_URL, params=params, timeout=30)
        
        if resp.status_code != 200:
            return []
        
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return []
        
        sections = []
        section_list = data.get("sections", [])
        
        for sec in section_list:
            # Parse instructor - get first non-dash name
            professor = "TBA"
            instructors = sec.get("instructors", [])
            for inst in instructors:
                name = inst.get("name", "") if isinstance(inst, dict) else str(inst)
                if name and name != "-":
                    professor = name
                    break
            
            # Parse schedule/meetings
            schedule = []
            for mtg in sec.get("meetings", []):
                days = mtg.get("days", "")
                start = parse_time(mtg.get("start_time", ""))
                end = parse_time(mtg.get("end_time", ""))
                
                # Build location string
                location = mtg.get("facility_descr", "")
                if not location:
                    bldg = mtg.get("bldg_cd", "")
                    room = mtg.get("room", "")
                    if bldg and room:
                        location = f"{bldg} {room}"
                    else:
                        location = bldg or room or ""
                
                if days or start:
                    schedule.append(Meeting(
                        days=days,
                        start_time=start,
                        end_time=end,
                        location=location,
                    ))
            
            section_info = {
                "section": sec.get("class_section", ""),
                "professor": professor,
                "schedule": schedule,
                "enrollment_cap": sec.get("class_capacity", 0),
                "enrollment_total": sec.get("enrollment_total", 0),
                "section_type": sec.get("section_type", sec.get("component", "")),
                "status": sec.get("enrl_stat_descr", ""),
                "class_nbr": sec.get("class_nbr", 0),
            }
            
            sections.append(section_info)
        
        return sections
    
    def save(self, courses: list[Course], output_path: str):
        """Save courses to JSON."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = [c.to_dict() for c in courses]
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Saved {len(courses)} courses to {path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape BU courses")
    parser.add_argument("-o", "--output", default="data/courses.json")
    parser.add_argument("--subject", help="Scrape single subject (e.g., CASCS)")
    parser.add_argument("--no-details", action="store_true", help="Skip fetching details (faster)")
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()
    
    print("BU Course Scraper")
    print("=" * 50)
    print(f"Output: {args.output}")
    print(f"Fetch details: {not args.no_details}")
    print()
    
    scraper = BUScraper(
        delay=args.delay, 
        fetch_details=not args.no_details,
    )
    
    if args.subject:
        subjects = [args.subject]
    else:
        subjects = SUBJECTS
    
    courses = scraper.scrape_all(subjects)
    
    if courses:
        scraper.save(courses, args.output)
    else:
        print("✗ No courses found")
        sys.exit(1)


if __name__ == "__main__":
    main()