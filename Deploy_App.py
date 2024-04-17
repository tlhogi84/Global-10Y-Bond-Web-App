import time
import pandas as pd
from subprocess import call

# Function to print messages with timestamps
def print_with_timestamp(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

start_time_overall = time.time()
print_with_timestamp("Starting: Collect_API_Data")

# Run Collect_API_Data with a progress bar
progress_bar_length = 40
total_seconds = 200  # Estimated total time for Collect_API_Data
for i in range(progress_bar_length + 1):
    time.sleep(total_seconds / progress_bar_length)  # Simulate processing time
    print("\rCollect_API_Data: [{:<40}] {:.1f}%".format('=' * i, (i / progress_bar_length) * 100), end='', flush=True)
print_with_timestamp("Finished: Collect_API_Data")

print_with_timestamp("Starting: CPI_CALCS")
call(["python", "CPI_CALCS.py"])

print_with_timestamp("Starting: LTRATES_Calcs")
call(["python", "LTRATES_Calcs.py"])

# End time for overall process
end_time_overall = time.time()
print_with_timestamp(f"Overall process completed in {end_time_overall - start_time_overall:.2f} seconds")

print_with_timestamp("Starting: app")
call(["python", "app.py"])



