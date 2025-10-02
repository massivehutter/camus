# Place this code in camus/backend/courses/management/commands/scrape_courses.py
# (or a temporary test_scraper.py file)
import requests
from bs4 import BeautifulSoup
import re  # Python's regular expression library
import json # To print the output nicely

# --- The main scraping function ---
def scrape_comp_courses():
    """
    Scrapes all COMP courses and their prerequisites from the Rice catalog.
    Returns a tuple containing a dictionary of courses (nodes) and a list of prerequisites (edges).
    """
    # This URL directly targets the Computer Science (COMP) courses
    URL = "https://courses.rice.edu/courses/!SWKSCAT.cat?p_acyr_code=2026&p_action=CATASRCH&p_onebar=&p_mode=AND&p_subj_cd=COMP&p_subj=COMP&p_dept=&p_school=&p_df=&p_submit=&as_fid=f0071ef8b7d71a9106c5f903e7d8185a33b54f44"
    
    print("Fetching course data...")
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    # These data structures will hold our graph
    nodes = {}  # The courses {'COMP182': {'title': '...'}, ...}
    edges = []  # The prerequisites [('COMP140', 'COMP182'), ...]

    # Find all <div> tags with the class "courseblock"
    course_blocks = soup.find_all("div", class_="courseblock")
    print(f"Found {len(course_blocks)} course blocks.")

    # A regular expression to find any text matching "COMP" followed by 3 or 4 digits
    prereq_pattern = re.compile(r'COMP\s+\d{3,4}')

    for block in course_blocks:
        title_tag = block.find("p", class_="courseblocktitle")
        desc_tag = block.find("div", class_="courseblockdesc")

        if not title_tag or not desc_tag:
            continue

        # --- Extract Node (Course) Information ---
        title_text = title_tag.text.strip()
        
        # Extract the primary course code from the title text (e.g., "COMP 182")
        course_code_match = re.search(r'(COMP\s+\d{3,4})', title_text)
        if not course_code_match:
            continue
        
        # Standardize the course code to remove spaces (e.g., "COMP182")
        current_course = course_code_match.group(1).replace(" ", "")
        nodes[current_course] = {'title': title_text}
        
        # --- Extract Edges (Prerequisites) ---
        prereq_text = desc_tag.get_text()
        
        # Find all occurrences of the prereq pattern in the description
        found_prereqs = prereq_pattern.findall(prereq_text)
        
        for prereq in found_prereqs:
            # Standardize the prerequisite code
            prereq_course = prereq.replace(" ", "")
            
            # Avoid self-references (e.g., COMP 410 lists COMP 410 as a prereq)
            if current_course != prereq_course:
                edge = (prereq_course, current_course) # (from, to)
                if edge not in edges:
                    edges.append(edge)

    return (nodes, edges)

# --- Main execution block ---
if __name__ == '__main__':
    courses, prerequisites = scrape_comp_courses()
    
    print("\n--- Courses (Nodes) ---")
    print(f"Found {len(courses)} unique courses.")
    print(json.dumps(courses, indent=2))
    
    print("\n--- Prerequisites (Edges) ---")
    print(f"Found {len(prerequisites)} prerequisite relationships.")
    print(json.dumps(prerequisites, indent=2))