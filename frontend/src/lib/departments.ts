/**
 * Mapping of department codes to full names by college.
 * Based on Boston University's official department abbreviations.
 * 
 * Note: Some codes appear in multiple colleges with different meanings:
 * - AR: Archaeology (CAS) vs Visual Arts (CFA)
 * - CI: Cinema & Media Studies (CAS) vs Cinema & Media Studies (COM)
 * - EC: Economics (CAS) vs Electrical & Computer Engineering (ENG)
 * - ME: Middle East & North Africa Studies (CAS) vs Music Education (CFA) vs Mechanical Engineering (ENG)
 * - MS: Medical Science (CAS) vs Materials Science & Engineering (ENG)
 * - MU: Music (CAS) vs Music (CFA)
 * - BF: Bioinformatics (CDS) vs Bioinformatics (ENG)
 */
export const DEPARTMENT_NAMES: Record<string, Record<string, string>> = {
  CAS: {
    "AA": "African American & Black Diaspora Studies",
    "AH": "History of Art & Architecture",
    "AI": "Asian Studies",
    "AM": "American & New England Studies, including Preservation Studies",
    "AN": "Anthropology",
    "AR": "Archaeology",
    "AS": "Astronomy",
    "BB": "Biochemistry & Molecular Biology",
    "BI": "Biology",
    "C": "Core Curriculum",
    "CG": "Modern Greek",
    "CH": "Chemistry",
    "CI": "Cinema & Media Studies",
    "CL": "Classical Studies",
    "CS": "Computer Science",
    "EC": "Economics",
    "EE": "Earth & Environment",
    "EI": "Editorial Studies",
    "EN": "English",
    "FR": "French Studies (International Programs only)",
    "FY": "First Year Experience",
    "HI": "History",
    "HU": "Humanities",
    "ID": "Interdisciplinary Studies",
    "IN": "Internships",
    "IP": "International Programs",
    "IR": "International Relations",
    "IT": "Italian Studies (International Programs only)",
    "JS": "Jewish Studies",
    "LA": "Hausa",
    "LC": "Chinese",
    "LD": "Amharic, Igbo, Mandinka/Bambara, Setswana/Sesotho, isiZulu, Other African Languages and Linguistics",
    "LE": "Swahili (Kiswahili)",
    "LF": "French",
    "LG": "German",
    "LH": "Hebrew",
    "LI": "Italian",
    "LJ": "Japanese",
    "LK": "Korean",
    "LL": "Language Learning",
    "LM": "isiXosha",
    "LN": "Hindi-Urdu",
    "LO": "Yoruba",
    "LP": "Portuguese",
    "LR": "Russian",
    "LS": "Spanish",
    "LT": "Turkish",
    "LU": "Pulaar",
    "LW": "Wolof, Akan Twi",
    "LX": "Applied Linguistics",
    "LY": "Arabic",
    "LZ": "Persian (Farsi)",
    "MA": "Mathematics & Statistics",
    "ME": "Middle East & North Africa Studies",
    "MR": "Marine Science",
    "MS": "Medical Science",
    "MU": "Music",
    "NE": "Neuroscience",
    "NG": "Nigerian Studies (International Programs only)",
    "NS": "Natural Sciences",
    "PH": "Philosophy",
    "PO": "Political Science",
    "PS": "Psychological & Brain Sciences",
    "PY": "Physics",
    "QU": "Spanish Studies (Quito only)",
    "RN": "Religion",
    "RO": "Romance Studies",
    "SO": "Sociology",
    "SS": "Social Sciences",
    "SY": "Senior-Year Development",
    "TL": "Literary Translation",
    "WR": "Writing",
    "WS": "Women's, Gender & Sexuality Studies",
    "XL": "Comparative Literature",
  },
  QUESTROM: {
    "AC": "Accounting",
    "AD": "Art & Design",
    "BA": "Business Administration",
    "FE": "Finance",
    "IS": "Information Systems",
    "MK": "Marketing",
    "OM": "Operations Management",
    "QM": "Quantitative Methods",
    "SI": "Social Innovation",
    "SM": "Sports Management",
  },
  CDS: {
    "BF": "Bioinformatics",
    "DS": "Data Science",
    "DX": "Online Data Science course",
  },
  CFA: {
    "AR": "Visual Arts",
    "TH": "Theatre",
    "FAC": "FA Courses",
    "ME": "Music Education",
    "ML": "Applied Lessons",
    "MP": "Performance",
    "MT": "Music Theory",
    "MU": "Music",
  },
  CGS: {
    "HU": "Humanities",
    "MA": "Mathematics",
    "NS": "Natural Science",
    "RH": "Rhetoric",
    "SS": "Social Science",
  },
  COM: {
    "CI": "Cinema & Media Studies",
    "CM": "Mass Communication, Advertising & Public Relations",
    "CO": "Communication Core Courses",
    "EM": "Emerging Media Studies",
    "FT": "Film & Television",
    "JO": "Journalism",
  },
  ENG: {
    "BE": "Biomedical Engineering",
    "BF": "Bioinformatics",
    "EC": "Electrical & Computer Engineering",
    "EK": "Engineering Core",
    "ME": "Mechanical Engineering",
    "MS": "Materials Science & Engineering",
    "SE": "Systems Engineering",
  },
  SAR: {
    "HF": "Health Sciences",
    "HS": "Health Sciences",
    "OT": "Occupational Therapy",
    "PT": "Physical Therapy",
    "SH": "Speech & Hearing",
  },
};

/**
 * Get the full name for a department code, optionally scoped by college.
 * 
 * If college is provided, looks up the code in that college's mapping.
 * If college is not provided, searches all colleges and returns the first match
 * (for backwards compatibility with existing code).
 * 
 * @param code - Department code (e.g., "EC", "CS")
 * @param college - Optional college code (e.g., "CAS", "ENG")
 * @returns Full department name, or the code itself if not found
 */
export function getDepartmentName(code: string, college?: string): string {
  if (college && DEPARTMENT_NAMES[college]?.[code]) {
    return DEPARTMENT_NAMES[college][code];
  }
  
  // Fallback: search all colleges (for backwards compatibility)
  // This handles cases where college is not provided
  for (const collegeMap of Object.values(DEPARTMENT_NAMES)) {
    if (collegeMap[code]) {
      return collegeMap[code];
    }
  }
  
  return code;
}

/**
 * Get a display string with both code and name.
 * 
 * @param code - Department code (e.g., "EC", "CS")
 * @param college - Optional college code (e.g., "CAS", "ENG")
 * @returns Display string like "EC - Economics" or "EC - Electrical & Computer Engineering"
 */
export function getDepartmentDisplay(code: string, college?: string): string {
  const name = getDepartmentName(code, college);
  return name !== code ? `${code} - ${name}` : code;
}
