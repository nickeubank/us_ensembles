import geopandas as gpd
import os
import pickle
import numpy as np
import pandas as pd


shapes = gpd.read_file('../00_source_data/census_blocks_w_race/US_blck_grp_2010.shp')
data = pd.read_csv('../00_source_data/census_blocks_w_race/ds171_2010_blck_grp.csv',
                   encoding='latin-1')


########
# Gather appropriate numbers
########

data['pop_total'] = data.H7Q001
data['pop_VAP'] = data.H7S001
data['pop_BVAP'] = data.H7S004
data['pop_HVAP'] = data.H7T002

# Few checks...
assert (data['pop_HVAP'] <= data['pop_VAP']).all()
assert (data['pop_BVAP'] <= data['pop_VAP']).all()
assert (data['pop_VAP'] <= data['pop_total']).all()

data = data[['GISJOIN', 'pop_total', 'pop_VAP', 
            'pop_BVAP', 'pop_HVAP']]
#########
# Merge data with shapes
#########

census = shapes.merge(data, on='GISJOIN', how='outer', 
                      validate='1:1', indicator=True)
assert (census[census._merge == 'right_only'].pop_total == 0).all()
assert (census._merge != 'left_only').all()
census = census[census._merge == 'both']
census = census.drop('_merge', axis='columns')

census.to_file('../00_source_data/census_blocks_w_race/prepped_census.shp')

