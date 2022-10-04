import collect
import pandas as pd

home = 'https://www.sejm.gov.pl/sejm9.nsf/'

all_sessions = collect.get_sessions_info()
all_votes = collect.get_votes_info(all_sessions)
results = collect.get_results(all_votes[:10])
results.to_csv('sample_results.csv', index=False)
pd.DataFrame(all_votes).to_csv('votes_info.csv', index=False)
print('Done!')
