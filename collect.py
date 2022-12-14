import os
import csv
import requests
import re
import time
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np


home = 'https://www.sejm.gov.pl/sejm9.nsf/'
local_path = '/home/milosh-dr/code/MPs'


def get_sessions_info():
    '''Returns list of dictionaries with info about all parliament sessions in 2022
    including no, url and a date'''
    req = requests.get('https://www.sejm.gov.pl/sejm9.nsf/agent.xsp?symbol=posglos&NrKadencji=9')
    soup = BeautifulSoup(req.text, 'html.parser')
    session_info = soup.find('tbody').find_all('tr')
    all_sessions = []
    for row in session_info:
        session_dict = {}
        cells = row.find_all('td')
        
        # Get only info about sessions in 2022
        if '2022' not in cells[1].a.text:
            continue

        session_dict['no'] = cells[0].text.strip()
        session_dict['url'] = os.path.join(home, cells[1].a['href'])
        session_dict['date'] = cells[1].text
        all_sessions.append(session_dict)

    # Fill missing session numbers
    for session in all_sessions:
        if session['no']:
            current = session['no']
        else:
            session['no'] = current
    return all_sessions


def get_votes_info(sessions):
    '''Takes list of dictionaries with sessions info and
    returns list of dictionaries with corresponding votes info'''
    all_votes = []
    for session in sessions:
        
        # Go to the current session url
        req = requests.get(session['url'])
        soup = BeautifulSoup(req.text, 'html.parser')
        vote_info = soup.find('tbody').find_all('tr')

        for row in vote_info:
            cells = row.find_all('td')

            # This dictionary will serve us later as a mapping for vote topics
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
    '''Takes list of dictionaries with votes info and returns DataFrame including all corresponding results'''
    vote_dfs = []
    if type(start) != int:
        try:
            print('Start value not given. Loading the current status...')
            print('-'*30)
            with open(os.path.join(local_path, 'status.txt'), 'r') as file:
                status = file.read()
                if status=='Done':
                    print('All data has been already parsed.')
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
        
        # Go to the current vote url
        time.sleep(sleep_time)
        try:
            req = requests.get(votes[i]['vote_url'])
            soup = BeautifulSoup(req.text, 'html.parser')
        except:
            print('Problem with retrieving page no: {} (at vote level)'.format(i))
            print(f"Problematic url: {votes[i]['vote_url']}")

            with open(os.path.join(local_path, 'status.txt'), 'w') as file:
                file.write(str(i))
            if not vote_dfs:
                return
            return pd.concat(vote_dfs, axis=1)
            
        parties = soup.find_all('td', class_='left')

        # Create empty df for current vote
        cols=['Party', 'MPS', f"{votes[i]['session_no']}/{votes[i]['vote_no']}"]
        if i!=0:
            cols=cols[-1:]
        vote_df = pd.DataFrame(columns=cols)
        
        for party in parties:
            # Get party name and url
            party_name = party.a.text
            party_url = os.path.join(home, party.a['href'])

            # Go to current party results url
            time.sleep(sleep_time)
            try:
                req = requests.get(party_url)
                soup = BeautifulSoup(req.text, 'html.parser')
            except:
                print('Problem with retrieving page no: {} (at party-{} level)'.format(i, party_name))
                print(f'Problematic url: {party_url}')
                
                with open(os.path.join(local_path, 'status.txt'), 'w') as file:
                    file.write(str(i))
                if not vote_dfs:
                    return
                return pd.concat(vote_dfs, axis=1) 

            # Get mp names
            mps = soup.find_all('td', class_='left', style='')
            # Get results to current vote df
            vote_results = soup.find_all('td', class_='left', style=re.compile(r'.+'))
            for mp, result in zip(mps, vote_results):
                if i==0:
                    vote_df.loc[len(vote_df)] = party_name, mp.text, result.text
                else:
                    vote_df.loc[len(vote_df)] = result.text

        # Add vote to the list
        vote_dfs.append(vote_df)
    print('All done!')
    with open(os.path.join(local_path, 'status.txt'), 'w') as file:
        file.write('Done')
    return pd.concat(vote_dfs, axis=1)


def save(results):
    if results is None:
        print('No results to be saved')
        return

    # Check how many files with data already exist in the path
    files = os.listdir(local_path)
    i=0
    for filename in files:
        if filename.startswith('results'):
            i+=1
    results.to_csv(f'results_{i+1}.csv', index=False)
    return


def concatenate():
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
        df = pd.read_csv(filename)
        dfs.append(df)
    df = pd.concat(dfs, axis=1)
    if 'final_results.csv' not in files:
        df.to_csv('final_results.csv', index=False)
    else:
        print('File already exists.')
    return df


def import_data():
    '''Returns data from parliament's website'''
    all_sessions = get_sessions_info()
    all_votes = get_votes_info(all_sessions)
    all_results = get_results(all_votes)

    return all_votes, all_results

