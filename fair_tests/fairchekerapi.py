import requests
import csv
import time

# --- CONFIGURATION ---
DATAVERSE_BASE_URL = "https://datasets.iisg.amsterdam"
DATAVERSE_ALIAS = "globalise"
# The API endpoint as defined in the Swagger UI
FAIR_CHECKER_API = "https://fair-checker.france-bioinformatique.fr/api/check/legacy/metrics_all"
OUTPUT_FILE = "globalise_fair_results.csv"

def get_globalise_datasets():
    """Fetches the 23 datasets from the Globalise Dataverse."""
    print("Step 1: Fetching datasets from Amsterdam Dataverse...")
    search_url = f"{DATAVERSE_BASE_URL}/api/v1/search"
    # Filtering for datasets only within the globalise alias
    params = {"q": "*", "type": "dataset", "subtree": DATAVERSE_ALIAS, "per_page": 23}
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        items = response.json()['data']['items']
        return [{"title": i.get("name"), "pid": i.get("global_id")} for i in items]
    except Exception as e:
        print(f"Dataverse Error: {e}")
        return []

def run_fair_assessment(pid):
    """
    Evaluates a PID via FAIR-checker.
    Resolves Handles/DOIs to full URLs first to ensure the checker can crawl.
    """
    # Resolve Handle to a URL (FAIR-checker needs a resolvable web address)
    if pid.startswith("hdl:"):
        resolved_url = f"https://hdl.handle.net/{pid.split('hdl:')[1]}"
    elif pid.startswith("doi:"):
        resolved_url = f"https://doi.org/{pid.split('doi:')[1]}"
    else:
        resolved_url = pid

    print(f"Evaluating: {resolved_url}...")
    
    try:
        # According to Swagger, this endpoint expects a 'url' query parameter
        response = requests.get(FAIR_CHECKER_API, params={"url": resolved_url}, timeout=120)
        
        if response.status_code == 200:
            metrics_results = response.json()
            # Initialize score counters
            summary = {"F": 0, "A": 0, "I": 0, "R": 0, "Total_Passed": 0}
            
            for test in metrics_results:
                # The API returns 'status': 'passed' or 'failed'
                is_passed = 1 if test.get("status") == "passed" else 0
                
                # Identify the FAIR principle from the metric_id (e.g., "F1A")
                metric_id = test.get("metric_id", "U")
                principle = metric_id[0].upper() 
                
                if principle in summary:
                    summary[principle] += is_passed
                    summary["Total_Passed"] += is_passed
            return summary
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return f"Failed: {str(e)}"

def main():
    datasets = get_globalise_datasets()
    if not datasets:
        return

    all_results = []
    for ds in datasets:
        score_data = run_fair_assessment(ds['pid'])
        
        # Format the row for CSV
        row = {
            "Dataset Title": ds['title'],
            "Identifier": ds['pid']
        }
        
        if isinstance(score_data, dict):
            row.update(score_data)
        else:
            row["Total_Passed"] = score_data # Capture the error message
            
        all_results.append(row)
        # Pause to avoid rate-limiting on the FAIR-checker server
        time.sleep(1.5)

    # Save to CSV
    headers = ["Dataset Title", "Identifier", "F", "A", "I", "R", "Total_Passed"]
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"\nSuccess! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()