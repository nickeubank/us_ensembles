import geopandas as gpd
import os

os.chdir('/users/nick/github/us_ensembles')
precincts = gpd.read_file("./00_source_data/2008_presidential_precinct_counts.shp")


precincts = precincts[['OBJECTID', 'P2008_D', 'P2008_R', 'STATE', 'COUNTY', 'geometry']]

##########
# Get sequential to FIPS cross-walk
# (SLURM likes to work with sequential counters)
##########

state_codes = precincts.STATE.drop_duplicates().sort_values().reset_index(drop=True)
fips = state_codes.to_dict()

# Couple stability tests
assert len(state_codes) == 50
assert state_codes.loc[0] == '01'
assert state_codes.loc[15] == '19'
assert state_codes.loc[47] == '54'
assert fips[0] == '01'
assert fips[15] == '19'
assert fips[47] == '54'

import pickle
with open('20_intermediate_files/sequential_to_fips.pickle', 'wb') as f:
    pickle.dump(fips, f)
    
