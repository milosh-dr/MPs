import collect
import os
import csv
import pandas as pd

# home = 'https://www.sejm.gov.pl/sejm9.nsf/'
local_path = '/home/milosh-dr/code/MPs'

def main():
    files = os.listdir(local_path)
    if 'votes_info.csv' not in files:
        all_sessions = collect.get_sessions_info()
        all_votes = collect.get_votes_info(all_sessions)

        pd.DataFrame(all_votes).to_csv('votes_info.csv', index=False)

    # Read list of dictionary from file
    all_votes=[]
    with open('votes_info.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            all_votes.append(row)

    results = collect.get_results(all_votes)
    if not results:
        # TODO: Run script that clears crontab and concatenate data from all files
        # TODO: Find a way to check if all is done or we didn't even start
        return

    # TODO: Make it function in separate file
    # Check how many files with parsed data already exist in the path
    files = os.listdir(local_path)
    i=0
    for filename in files:
        if filename.startswith('results'):
            i+=1
    results.to_csv(f'results_{i+1}.csv', index=False)
    return

main()