import requests
import csv
import time

# --- CONFIGURATION ---
DATAVERSE_BASE_URL = "https://datasets.iisg.amsterdam"
DATAVERSE_ALIAS = "globalise"
# Correct POST endpoint for current FAIR-checker version
FAIR_CHECKER_API = "http://fair-checker.france-bioinformatique.fr/api/check/metrics"
OUTPUT_FILE = "globalise_fair_results.csv"

def get_globalise_datasets():
    """Fetches the 23 dataset IDs from Globalise."""
    print("Step 1: Fetching datasets from Amsterdam Dataverse...")
    search_url = f"{DATAVERSE_BASE_URL}/api/v1/search"
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
    """Sends the PID to FAIR-checker using the required POST method."""
    # Resolve 'hdl:' or 'doi:' to a full URL so the checker can crawl it
    resolved_url = pid
    if pid.startswith("hdl:"):
        resolved_url = f"https://hdl.handle.net/{pid.split('hdl:')[1]}"
    elif pid.startswith("doi:"):
        resolved_url = f"https://doi.org/{pid.split('doi:')[1]}"

    print(f"Evaluating: {resolved_url}...")
    
    try:
        # The API often requires a POST with a JSON body
        payload = {"url": resolved_url}
        response = requests.post(FAIR_CHECKER_API, json=payload, timeout=120)
        
        if response.status_code == 200:
            metrics = response.json()
            results = {"F": 0, "A": 0, "I": 0, "R": 0, "Total": 0}
            for m in metrics:
                score = 1 if m.get("status") in ["passed", "success", "1", 1] else 0
                # Principle is usually the first letter of the metric ID (e.g., F1)
                p_key = m.get("metric_id", "U")[0].upper()
                if p_key in results:
                    results[p_key] += score
                    results["Total"] += score
            return results
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return f"Request Failed: {str(e)}"

def main():
    datasets = get_globalise_datasets()
    if not datasets: return

    final_data = []
    for ds in datasets:
        score_data = run_fair_assessment(ds['pid'])
        row = {"Title": ds['title'], "Identifier": ds['pid']}
        
        if isinstance(score_data, dict):
            row.update(score_data)
        else:
            row["Total"] = score_data # Stores the error message
            
        final_data.append(row)
        time.sleep(2) # Prevent rate-limiting

    # Write to CSV
    keys = ["Title", "Identifier", "F", "A", "I", "R", "Total"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"\nSaved {len(final_data)} results to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()