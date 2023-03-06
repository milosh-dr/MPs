import os
import csv
import requests
import re
import time
import subprocess

from bs4 import BeautifulSoup

import pandas as pd
import numpy as np

"""
This module provides functionality for collecting and saving the data on
all parliamentary voting outcomes in 2022 and corresponding information.

Functions
---------
    get_sessions_info() -> List[Dict[str, Any]]:
    Returns a list of dictionaries with information on all parliamentary sessions in 2022.
    
    get_votes_info(sessions_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    Returns a list of dictionaries with information on all votings at all given sessions.

    get_results(votes_info: List[Dict[str, Any]]) -> pd.DataFrame:
    Parses data from URLs found in votes_info list and returns a Pandas DataFrame including all corresponding voting results.
    
    save(results: pd.DataFrame):
    Saves currently parsed portion of data to the CSV file.
    
    concatenate():
    Loads data from all files and returns it as a single Pandas DataFrame, while also savomg it to a CSV file.
"""


home = 'https://www.sejm.gov.pl/sejm9.nsf/'
local_path = '/home/milosh-dr/code/MPs'


def get_sessions_info():
    """
    Returns a list of dictionaries with information on all parliamentary sessions in 2022.

    Returns
    -------
    list
        A list of dictionaries containing the following keys:
        - 'no': the session number.
        - 'url': the URL of the session page on the parliament's website.
        - 'date': the date of the session.
    """
    req = requests.get('https://www.sejm.gov.pl/sejm9.nsf/agent.xsp?symbol=posglos&NrKadencji=9')
    soup = BeautifulSoup(req.text, 'html.parser')
    session_info = soup.find('tbody').find_all('tr')
    all_sessions = []
    for row in session_info:
        session_dict = {}
        cells = row.find_all('td')
        
        # Parse only information on sessions in 2022
        if '2022' not in cells[1].a.text:
            continue

        session_dict['no'] = cells[0].text.strip()
        session_dict['url'] = os.path.join(home, cells[1].a['href'])
        session_dict['date'] = cells[1].text
        all_sessions.append(session_dict)

    # Fill missing sessions' numbers if necessary
    for session in all_sessions:
        if session['no']:
            current = session['no']
        else:
            session['no'] = current
    return all_sessions


def get_votes_info(sessions):
    """
    Returns a list of dictionaries with information on all votings at given sessions.

    Parameters
    ----------
    sessions : list
        A list of dictionaries with information on parliament sessions in 2022,
        including session number, session URL, and date.

    Returns
    -------
    list
        A list of dictionaries with corresponding voting information, including:
        - session_no: session number
        - session_url: session URL
        - date: date of the session
        - vote_no: voting number
        - vote_url: URL of the voting
        - vote_time: time of the voting
        - vote_topic: topic of the voting
        - vote_type: type of the voting

    """
    all_votes = []
    for session in sessions:
        
        # Go to the current session's URL
        req = requests.get(session['url'])
        soup = BeautifulSoup(req.text, 'html.parser')
        vote_info = soup.find('tbody').find_all('tr')

        for row in vote_info:
            cells = row.find_all('td')

            # Parse all information on the current voting 
            vote_dict = {
                'session_no': session['no'],
                'session_url': session['url'],
                'date': session['date'],
                'vote_no': cells[0].text.strip(),
                'vote_url': os.path.join(home, cells[0].a['href']),
                'vote_time': cells[1].text,
                'vote_topic': cells[2].text,
                'vote_type': cells[2].a.text
            }
            all_votes.append(vote_dict)
    return all_votes


def get_results(votes, start=None, stop=None, sleep_time=1):
    '''
    Returns a Pandas DataFrame including all corresponding voting results
    obtained from parsing data from the URLs provided in a list of dictionaries.

    Parameters
    ----------
    votes : List[Dict[str, Any]]
        List of dictionaries with information about the votings to be parsed.
    start : int, optional
        The index of the first voting to be parsed. Defaults to None, which means it will start from the first vote.
    stop : int, optional
        The index of the last voting to be parsed. Defaults to None, which means it will continue until the last vote.
    sleep_time : int, optional
        The time to wait in seconds before parsing the next page. Defaults to 1.

    Returns
    -------
    pd.DataFrame
        DataFrame including all corresponding results.

    Notes
    -----
    - The function saves the status of the process to the status.txt file in the given path.
    - The function prints error messages in case of problems.
    - Encountering errors with five consecutive pages stops the process due to possible server limitations.
    - When restarting, the function reads the current status.
    '''
    # Create a list to hold all parsed data
    vote_dfs = []
    # Create a list to keep track of any errors
    errors = []
    # Read the current status if the start value is not given
    if type(start) != int:
        try:
            print('Start value not given. Loading the current status...')
            print('-'*30)
            with open(os.path.join(local_path, 'status.txt'), 'r') as file:
                status = file.read()
                if status=='Done':
                    print('All data have been already parsed.')
                    return
                start = int(status)
                print(f'Current status: {start}')
        except FileNotFoundError:
            start = 0
            print('Status file not in the path. Starting from the beginning.')

    if not stop:
        stop = len(votes)
        print('Stop value not given. Trying to parse all data.')

    for i in range(start, stop):
        
        # Go to the current voting's URL
        time.sleep(sleep_time)
        try:
            req = requests.get(votes[i]['vote_url'])
            soup = BeautifulSoup(req.text, 'html.parser')
        except:
            print('Problem with retrieving page no: {} (at vote level)'.format(i))
            print(f"Problematic url: {votes[i]['vote_url']}")
            # Update errors list
            errors.append(i)
            if len(errors) < 5:
                continue
            last5_errors = errors[-5:]
            # Check if the last five errors occured on five consecutive pages to update the status and stop the process if necessary
            if list(range(last5_errors[0], last5_errors[-1]+1)) == last5_errors:
                with open(os.path.join(local_path, 'status.txt'), 'w') as file:
                    file.write(str(last5_errors[0]))
                if not vote_dfs:
                    return
                return pd.concat(vote_dfs, axis=1)
            continue
            
        parties = soup.find_all('td', class_='left')

        # Create empty pd.DataFrame to hold information on current voting
        cols=['Party', 'MPS', f"{votes[i]['session_no']}/{votes[i]['vote_no']}"]
        if i!=0:
            cols=cols[-1:]
        vote_df = pd.DataFrame(columns=cols)
        
        for party in parties:
            # Parse party name and URL
            party_name = party.a.text
            party_url = os.path.join(home, party.a['href'])

            # Go to the current party's results URL
            time.sleep(sleep_time)
            try:
                req = requests.get(party_url)
                soup = BeautifulSoup(req.text, 'html.parser')
            except:
                print('Problem with retrieving page no: {} (at party-{} level)'.format(i, party_name))
                print(f'Problematic url: {party_url}')
                # We handled errors at the voting level, so here at party level we continue looping through all the parties
                continue

            # Parse MPs' names
            mps = soup.find_all('td', class_='left', style='')
            # Parse voting results
            vote_results = soup.find_all('td', class_='left', style=re.compile(r'.+'))
            for mp, result in zip(mps, vote_results):
                if i==0:
                    vote_df.loc[len(vote_df)] = party_name, mp.text, result.text
                else:
                    vote_df.loc[len(vote_df)] = result.text

        # Add vote_df to the list
        if vote_df.shape[0] != 0:
            vote_dfs.append(vote_df)

    print('All done!')
    # Update status
    with open(os.path.join(local_path, 'status.txt'), 'w') as file:
        file.write('Done')

    results = pd.concat(vote_dfs, axis=1)
    return results


def save(results):
    """
    Save the provided Pandas DataFrame to a file.

    Parameters
    ----------
    results : pandas DataFrame
        The DataFrame to be saved.

    Returns
    -------
    None

    """
    if results is None:
        print('No results to be saved')
        return

    # Check the number of existing files with data in the path.
    files = os.listdir(local_path)
    i=0
    for filename in files:
        if filename.startswith('results'):
            i+=1
    # Save the data with appropriate name and index
    results.to_csv(os.path.join(local_path, f'results_{i+1}.csv'), index=False)
    return


def concatenate():
    """
    Loads data from multiple files and concatenate it into a single pandas DataFrame.

    Returns
    -------
    pandas.DataFrame
        The concatenated DataFrame containing data from all files.

    Notes
    -----
    This function assumes that the data is stored in multiple CSV files with the same format, all located in the same directory.
    It starts concatenating only when the status.txt file is updated to 'Done'.
    It clears the crontab from the task of repeatedly parsing the data launching stop.sh script.
    

    """
    # Check the status
    with open(os.path.join(local_path, 'status.txt'), 'r') as file:
        if file.read().strip() != 'Done':
            print("You miss some data...")
            return
    results = []
    dfs = []
    files = os.listdir(local_path)
    for filename in files:
        if filename.startswith('results'):
            results.append(filename)

    for filename in sorted(results):
        df = pd.read_csv(os.path.join(local_path, filename))
        dfs.append(df)
    df = pd.concat(dfs, axis=1)
    
    # Clear the crontab from the current process
    script_stop = os.path.join(local_path, 'stop.sh')
    os.chmod(script_stop, 0o755)
    subprocess.call(script_stop)
    return df
