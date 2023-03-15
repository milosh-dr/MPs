import os
import csv

import pandas as pd

import collect
import transform

def main():
    # Read configuration
    config = collect.get_config()
    start = config['start']
    stop = config['stop']
    sleep_time = config['sleep_time']
    local_path = config['local_path']
    home = config['home']

    files = os.listdir(local_path)
    # Parse information on votings if necessary
    if 'votes_info.csv' not in files:
        print('No file with vote urls in the path. Starting to parse those...')
        all_sessions = collect.get_sessions_info(home)
        all_votes = collect.get_votes_info(all_sessions, home)

        pd.DataFrame(all_votes).to_csv(os.path.join(local_path, 'votes_info.csv'), index=False)

    # Read list of dictionaries from file
    all_votes=[]
    with open(os.path.join(local_path, 'votes_info.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            all_votes.append(row)

    results = collect.get_results(all_votes, start=start, stop=stop, sleep_time=sleep_time, home=home, local_path=local_path)
    collect.save(results, local_path)
    df = collect.concatenate(local_path)
    transform.transform(df, local_path)
    return

if __name__ == "__main__":
    main()