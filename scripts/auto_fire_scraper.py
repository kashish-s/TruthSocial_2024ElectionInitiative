import json
import subprocess
import concurrent.futures
import os
import time

# Function to run the scrape_one_keyword.py script with a given keyword
def run_scrape_script(keyword):
    script_path = 'scrape_one_keyword.py'
    subprocess.run(['python', script_path, '--keyword', keyword])

# Function to manage the list and run the scripts
def manage_keywords(json_file):
    while True:
        # Load the current list of keywords from the JSON file
        with open(json_file, 'r') as file:
            keywords = json.load(file)
        
        # If the list is empty, break the loop
        if not keywords:
            print("All keywords have been processed.")
            break
        
        # Grab the first keyword from the list
        keyword = keywords.pop(0)
        
        # Save the updated list back to the JSON file
        with open(json_file, 'w') as file:
            json.dump(keywords, file)
        
        # Run the scrape script with the keyword
        print(f"Starting process for keyword: {keyword}")
        run_scrape_script(keyword)

# Main function to manage concurrent execution
def main():
    json_file = '/keywords_tracker/today_keywords.json'
    
    # Use ThreadPoolExecutor to limit to 2 concurrent processes
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        while True:
            # Load the current list of keywords from the JSON file
            with open(json_file, 'r') as file:
                keywords = json.load(file)
            
            # If the list is empty, break the loop
            if not keywords:
                break
            
            # Submit a new task to the executor for each keyword
            for _ in range(2 - len(futures)):
                if keywords:
                    keyword = keywords.pop(0)
                    print(f"Sending off a process for {keyword}")
                    time.sleep(30)
                    
                    # Save the updated list back to the JSON file
                    with open(json_file, 'w') as file:
                        json.dump(keywords, file)
                    
                    futures.append(executor.submit(run_scrape_script, keyword))
            
            # Check for completed futures
            for future in concurrent.futures.as_completed(futures):
                futures.remove(future)
                if future.exception():
                    print(f"Process generated an exception: {future.exception()}")
    
    print("All keywords processed.")

if __name__ == "__main__":
    main()
