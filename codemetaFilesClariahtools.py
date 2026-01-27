import requests
from bs4 import BeautifulSoup
import json
import re
import time

# Base URL for CLARIAH tools
TOOLS_URL = "https://tools.clariah.nl/"

def get_github_urls(url):
    """Scrapes the portal for GitHub repository links."""
    print(f"Fetching repository links from {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the portal: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    github_links = set()
    
    # Look for all anchor tags containing 'github.com'
    for a in soup.find_all('a', href=True):
        href = a['href']
        if "github.com" in href:
            # Clean the URL to get the base repository path (owner/repo)
            # Regex captures github.com/owner/repo
            match = re.search(r"github\.com/([\w\-\.]+)/([\w\-\.]+)", href)
            if match:
                owner, repo = match.groups()
                # Remove common suffixes like .git
                repo = repo.replace(".git", "")
                github_links.add(f"{owner}/{repo}")
    
    return list(github_links)

def fetch_codemeta(repo_path):
    """Attempts to fetch codemeta.json from the default branch of a repo."""
    # We try 'main' then 'master' as common default branch names
    branches = ['main', 'master']
    
    for branch in branches:
        raw_url = f"https://raw.githubusercontent.com/{repo_path}/{branch}/codemeta.json"
        try:
            response = requests.get(raw_url, timeout=5)
            if response.status_code == 200:
                print(f"[FOUND] {repo_path} (branch: {branch})")
                return response.json()
        except Exception:
            continue
            
    print(f"[NOT FOUND] {repo_path}")
    return None

def main():
    repo_paths = get_github_urls(TOOLS_URL)
    print(f"Found {len(repo_paths)} potential GitHub repositories.\n")
    
    results = {}

    for path in repo_paths:
        data = fetch_codemeta(path)
        if data:
            results[path] = data
        # Be nice to GitHub's servers
        time.sleep(0.5)

    # Save the collected data to a file
    with open("clariah_codemeta_collection.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\nProcessing complete. Data saved for {len(results)} repositories.")

if __name__ == "__main__":
    main()
