import os
import csv

import pandas as pd

import collect
import transform

local_path = '/home/milosh-dr/code/MPs'

def main():
    files = os.listdir(local_path)
    # Parse information on votings if necessary
    if 'votes_info.csv' not in files:
        print('No file with vote urls in the path. Starting to parse those...')
        all_sessions = collect.get_sessions_info()
        all_votes = collect.get_votes_info(all_sessions)

        pd.DataFrame(all_votes).to_csv(os.path.join(local_path, 'votes_info.csv'), index=False)

    # Read list of dictionaries from file
    all_votes=[]
    with open(os.path.join(local_path, 'votes_info.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            all_votes.append(row)

    results = collect.get_results(all_votes, sleep_time=1)
    collect.save(results)
    df = collect.concatenate()
    transform.transform(df)
    return

main()