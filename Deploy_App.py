import time
import pandas as pd
from subprocess import Popen
from tqdm import tqdm

# Function to print messages with timestamps
def print_with_timestamp(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def run_with_progress(command, description, total_seconds):
    process = Popen(command)
    for _ in tqdm(range(total_seconds), desc=description):
        if process.poll() is not None:  # Process has finished
            break
        time.sleep(1)  # Sleep for 1 second between updates
    process.wait()  # Wait for process to complete if not already done
    print_with_timestamp(f"Finished: {description}")

start_time_overall = time.time()
print_with_timestamp("Starting: Collect_API_Data")

run_with_progress(["python", "Collect_API_Data.py"], "Collect_API_Data", 200)

print_with_timestamp("Starting: CPI_CALCS")
run_with_progress(["python", "CPI_CALCS.py"], "CPI_CALCS", 200)

print_with_timestamp("Starting: LTRATES_Calcs")
run_with_progress(["python", "LTRATES_Calcs.py"], "LTRATES_Calcs", 200)

# End time for overall process
end_time_overall = time.time()
print_with_timestamp(f"Overall process completed in {end_time_overall - start_time_overall:.2f} seconds")

print_with_timestamp("Starting: app")
Popen(["python", "app.py"])




