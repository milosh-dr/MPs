import os

import pandas as pd

local_path = '/home/milosh-dr/code/MPs'

def transform():
    df = pd.read_csv(os.path.join(local_path, 'final_results.csv'))

    # Getting rid of parsing errors
    nans = df.isna().sum()
    errors = nans[nans>0].index.tolist()
    df.drop(errors, axis=1, inplace=True)

    # Mapping string descriptions into numeric representations
    mapping = {}
    current_values = df.iloc[:,5].value_counts().index.tolist()
    new_values = [0, 1 , np.nan, .5]

    for value, new_value in zip(current_values, new_values):
        mapping[value] = new_value

    for col in df.columns[2:]:
        df[col] = df[col].map(mapping)


    # Computing party sizes
    party_sizes = df[['Party', 'MPS']].groupby('Party').agg(len)['MPS']

    # Computing total absences for all parties and all votes
    not_present = df.groupby('Party').apply(lambda x: x.isna().sum())
    not_present['party_size'] = party_sizes

    # Helper function for df.apply
    def absence_checker(row):
        """As a rule of thumb we decide to take a closer look whenever more then 75% of party members were absent.
        Considering only parties having more then 5 members"""
        
        if row['party_size'] < 6:
            row[:]=np.nan
            return row
        
        row[~(row>.75*row['party_size'])] = np.nan
        return row

    meaningful_absence = not_present.apply(absence_checker, axis=1)
    subset = meaningful_absence.columns[1:-1].tolist()
    meaningful_absence = (meaningful_absence
                        .dropna(axis=0, how='all', subset=subset)
                        .dropna(axis=1, how='all')
                        .drop('party_size', axis=1))

    # Filling missing values with 0 whenever 75% of party members were absent (big parties only)
    for vote in meaningful_absence.columns:
        for party in meaningful_absence.index:
            df.loc[(df['Party']==party), vote] = df.loc[(df['Party']== party), vote].fillna(0)

    # In other cases filling missing values according to the voting strategy of the party
    df = df.groupby('Party', group_keys=False).apply(lambda x: x.fillna(round(x.mean(numeric_only=True))))

    # For very small parties we fill nans with 0.5
    nans = df.isna().sum()
    to_fill = nans[nans>0].index
    for col in to_fill:
        df[col] = df[col].fillna(0.5)
    return df