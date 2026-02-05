import requests
import csv
import time

# --- CONFIGURATION ---
DATAVERSE_BASE_URL = "https://datasets.iisg.amsterdam"
DATAVERSE_ALIAS = "globalise"
# API endpoint for evaluating all metrics for a given resource
FAIR_CHECKER_URL = "http://fair-checker.france-bioinformatique.fr/api/check/metrics/all"
OUTPUT_FILE = "globalise_fair_results.csv"

def get_globalise_datasets():
    """Fetches the first 23 dataset PIDs from the Globalise Dataverse."""
    print("Connecting to Amsterdam Dataverse...")
    search_url = f"{DATAVERSE_BASE_URL}/api/v1/search"
    params = {
        "q": "*",
        "type": "dataset",
        "subtree": DATAVERSE_ALIAS,
        "per_page": 23 
    }
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        items = response.json()['data']['items']
        
        return [{
            "title": item.get("name"),
            "pid": item.get("global_id"),
            "url": item.get("url")
        } for item in items]
    except Exception as e:
        print(f"Failed to fetch datasets: {e}")
        return []

def run_fair_assessment(resource_id):
    """
    Sends the dataset ID to FAIR-checker.
    Returns a dictionary of counts for F, A, I, and R principles.
    """
    print(f"Evaluating FAIR metrics for: {resource_id}...")
    try:
        # We pass the PID as the 'url' parameter to the FAIR-checker
        response = requests.get(FAIR_CHECKER_URL, params={"url": resource_id}, timeout=90)
        
        if response.status_code == 200:
            metrics_data = response.json()
            summary = {"F": 0, "A": 0, "I": 0, "R": 0, "Total": 0}
            
            for metric in metrics_data:
                # FAIR-checker returns 'passed' or 'failed' for each metric
                score = 1 if metric.get("status") == "passed" else 0
                # Extract first letter of principle (e.g., 'Findable' -> 'F')
                principle = metric.get("principle", "Unknown")[0].upper()
                
                if principle in summary:
                    summary[principle] += score
                    summary["Total"] += score
            return summary
        else:
            return f"API Error ({response.status_code})"
    except Exception as e:
        return f"Timeout/Error: {str(e)}"

def save_to_csv(results, filename):
    """Writes the collected data to a local CSV file."""
    keys = ["Dataset Title", "PID", "Findable", "Accessible", "Interoperable", "Reusable", "Total Score"]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        
        for res in results:
            score = res['score']
            row = {
                "Dataset Title": res['title'],
                "PID": res['pid']
            }
            
            if isinstance(score, dict):
                row.update({
                    "Findable": score['F'],
                    "Accessible": score['A'],
                    "Interoperable": score['I'],
                    "Reusable": score['R'],
                    "Total Score": score['Total']
                })
            else:
                # In case of an error string
                row["Total Score"] = score
                
            writer.writerow(row)

def main():
    datasets = get_globalise_datasets()
    if not datasets:
        return

    all_results = []
    for ds in datasets:
        # Perform assessment
        report = run_fair_assessment(ds['pid'])
        all_results.append({
            "title": ds['title'],
            "pid": ds['pid'],
            "score": report
        })
        # Short sleep to avoid overwhelming the FAIR-checker server
        time.sleep(2)

    save_to_csv(all_results, OUTPUT_FILE)
    print(f"\nDone! Assessment complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()