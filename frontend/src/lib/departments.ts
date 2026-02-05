/**
 * Mapping of department codes to full names.
 * Based on Boston University's official department abbreviations.
 */
export const DEPARTMENT_NAMES: Record<string, string> = {
  "AA": "African American Studies",
  "AC": "Accountancy",
  "AD": "Art & Design",
  "AH": "Art History",
  "AM": "American Studies",
  "AN": "Anthropology",
  "AR": "Archaeology",
  "AS": "Astronomy",
  "BA": "Business Administration",
  "BE": "Biomedical Engineering",
  "BI": "Biology",
  "CG": "Computer Graphics",
  "CH": "Chemistry",
  "CI": "Cinema Studies",
  "CL": "Classical Studies",
  "CM": "Communication",
  "CO": "Computer Science", // Some courses use CO
  "CS": "Computer Science",
  "DS": "Data Science",
  "EC": "Economics",
  "EK": "Engineering Core",
  "EN": "English",
  "FA": "Fine Arts",
  "FE": "Finance & Economics",
  "FT": "Film & Television",
  "HF": "Health Sciences",
  "HI": "History",
  "HS": "Health Sciences",
  "IR": "International Relations",
  "IS": "Information Systems",
  "JO": "Journalism",
  "LA": "Latin",
  "LC": "Chinese",
  "LF": "French",
  "LG": "Greek",
  "LI": "Italian",
  "LJ": "Japanese",
  "LK": "Korean",
  "LN": "Linguistics",
  "LO": "Portuguese",
  "LP": "Polish",
  "LR": "Russian",
  "LS": "Spanish",
  "LT": "Turkish",
  "LW": "Swahili",
  "LX": "Slavic Languages",
  "LY": "Arabic",
  "LZ": "Hebrew",
  "MA": "Mathematics",
  "ME": "Mechanical Engineering",
  "MK": "Marketing",
  "MS": "Marine Science",
  "MU": "Music",
  "NE": "Neuroscience",
  "OM": "Operations Management",
  "OT": "Occupational Therapy",
  "PH": "Public Health",
  "PO": "Political Science",
  "PS": "Psychological & Brain Sciences",
  "PT": "Physical Therapy",
  "PY": "Physics",
  "QM": "Quantitative Methods",
  "RH": "Rhetoric",
  "RN": "Religion",
  "SE": "Systems Engineering",
  "SH": "Speech & Hearing",
  "SI": "Social Innovation",
  "SM": "Sports Management",
  "SO": "Sociology",
  "SS": "Social Sciences",
  "TH": "Theatre",
  "WR": "Writing",
  "WS": "Women's & Gender Studies",
};

/**
 * Get the full name for a department code.
 * Returns the code itself if no mapping exists.
 */
export function getDepartmentName(code: string): string {
  return DEPARTMENT_NAMES[code] || code;
}

/**
 * Get a display string with both code and name.
 * e.g., "CS - Computer Science"
 */
export function getDepartmentDisplay(code: string): string {
  const name = DEPARTMENT_NAMES[code];
  return name ? `${code} - ${name}` : code;
}
