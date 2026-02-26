import requests
import re
import base64

def get_repo_files(owner, repo, path=""):
    """Recursively gets all files in the repository."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(api_url)
    if response.status_code != 200:
        return []
    
    files = []
    contents = response.json()
    for item in contents:
        if item['type'] == 'file':
            files.append(item)
        elif item['type'] == 'dir':
            files.extend(get_repo_files(owner, repo, item['path']))
    return files

def extract_from_source(content, file_ext):
    """Regex patterns to find dependencies in actual code."""
    deps = []
    if file_ext == '.py':
        # Matches 'import package' or 'from package import ...'
        deps = re.findall(r"^\s*(?:import|from)\s+([a-zA-Z0-9_]+)", content, re.MULTILINE)
    elif file_ext in ['.r', '.R']:
        # Matches 'library(package)' or 'require(package)'
        deps = re.findall(r"(?:library|require)\(([a-zA-Z0-9\.]+)\)", content)
    elif file_ext in ['.sh', '.bash']:
        # Matches 'apt-get install package'
        deps = re.findall(r"apt-get\s+install\s+(?:-y\s+)?([\w\-\s]+)", content)
    return deps

def analyze_full_repo(github_url):
    match = re.search(r"github\.com/([^/]+)/([^/]+)", github_url)
    if not match: return
    owner, repo = match.groups()
    repo = repo.replace(".git", "")

    print(f"--- Deep Scanning Repository: {owner}/{repo} ---")
    all_files = get_repo_files(owner, repo)
    
    software_requirements = set()
    
    for file in all_files:
        file_name = file['name']
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Only scan relevant source/config files
        if file_ext in ['.py', '.r', '.sh', '.json', '.md']:
            response = requests.get(file['download_url'])
            if response.status_code == 200:
                content = response.text
                
                # 1. Scan README for manual prerequisites
                if 'README' in file_name.upper():
                    # Look for bullet points in Setup/Usage/Prerequisites
                    prereq_section = re.search(r"(?i)#+\s*(?:Prerequisites|Setup|Usage)(.*?)(?=\n#+|$)", content, re.DOTALL)
                    if prereq_section:
                        items = re.findall(r"^[ \t]*[\*\-]\s+(.*)", prereq_section.group(1), re.MULTILINE)
                        for i in items:
                            software_requirements.add(re.sub(r"\[(.*?)\]\(.*?\)", r"\1", i).strip())

                # 2. Scan source code for imports/libraries
                code_deps = extract_from_source(content, file_ext)
                for d in code_deps:
                    software_requirements.add(f"{d} ({file_ext[1:]} library)")

    # Output Results
    print(f"\n[FINAL CONSOLIDATED REQUIREMENTS]")
    if software_requirements:
        for sw in sorted(software_requirements):
            print(f" • {sw}")
    else:
        print("No specific software identified in code or README.")

if __name__ == "__main__":
    import os
    url = "https://github.com/rug-compling/Alpino.git"
    analyze_full_repo(url)