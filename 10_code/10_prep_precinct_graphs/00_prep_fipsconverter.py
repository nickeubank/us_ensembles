import geopandas as gpd
import os

precincts = gpd.read_file("../00_source_data/votes/2008_presidential_precinct_counts.shp")


##########
# Get sequential to FIPS cross-walk
# (SLURM likes to work with sequential counters)
##########

state_codes = precincts.STATE.drop_duplicates().sort_values()

# Now let's ignore Alaska and Hawaii
state_codes = state_codes[~state_codes.isin(['02', '15'])].reset_index(drop=True)

fips = state_codes.to_dict()

# Couple stability tests
assert len(state_codes) == len(fips)
assert state_codes.loc[0] == '01'
assert state_codes.loc[15] == '21'
assert state_codes.loc[47] == '56'
assert fips[0] == '01'
assert fips[15] == '21'
assert fips[47] == '56'

import pickle
with open('../20_intermediate_files/sequential_to_fips.pickle', 'wb') as f:
    pickle.dump(fips, f)
    
