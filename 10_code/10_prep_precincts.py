import geopandas as gpd
import os
import pickle
import numpy as np

###########
# Get environment var from SLURM
# and convert
###########

# state = os.getenv('STATE')

f = '../20_intermediate_files/sequential_to_fips.pickle'
state_fips_codes = sorted(list(pickle.load(open(f, "rb" )).values()))


###########
# Loads used for all passes
###########

# Precinct
master_precincts = gpd.read_file("../00_source_data/votes/"
                                 "2008_presidential_precinct_counts.shp")

master_precincts = master_precincts[['OBJECTID', 'P2008_D', 'P2008_R', 
                                     'STATE', 'COUNTY', 'geometry']]

# District Maps
master_districts = gpd.read_file('../00_source_data/legislative_districts/'
                                 'nhgis0190_shapefile_tl2014_us_cd114th_2014/'
                                 'US_cd114th_2014.shp')

master_districts = master_districts[['STATEFP', 'CD114FP', 'GEOID', 'geometry']]

########
# Loopz
########


for idx, state_fips in enumerate(state_fips_codes):
    
        print(f'on step {idx}, fips {state_fips}')

        ###########
        # Bring in precincts, population, 
        # and current districts
        ###########

        precincts = master_precincts[master_precincts.STATE == state_fips].copy()

        if len(precincts) == 0:
            raise ValueError(f"no precincts for fips {state_fips}")

        # Topology problems
        assert str(precincts.crs) == "{'init': 'epsg:3085'}"
        precincts.loc[~precincts.is_valid, 'geometry'] = precincts.loc[~precincts.is_valid, 'geometry'].buffer(0)
        assert precincts.is_valid.all()

        # Census blocks
        f_blocks = f'../00_source_data/census_blocks/tabblock2010_{state_fips}'\
                   f'_pophu/tabblock2010_{state_fips}_pophu.shp'

        # FL and NY have some places with census blocks but no precincts (e.g. federal parks). 
        # Causes later problems.
        if state_fips in ['12', '36']:
            f_blocks = f'../00_source_data/census_blocks/tabblock2010_{state_fips}'\
                       f'_pophu_clipped/tabblock2010_{state_fips}_pophu_clipped.shp'
            
        census_blocks = gpd.read_file(f_blocks)

        assert census_blocks.is_valid.all()

        # Legislative Districts
        districts = master_districts[master_districts['STATEFP'] == state_fips].copy()

        # Topology problems
        districts.loc[~districts.is_valid, 'geometry'] = districts.loc[~districts.is_valid,
                                                                       'geometry'].buffer(0)
        assert districts.is_valid.all()


        #########
        # Common reprojection
        #########

        crs = 'EPSG:3085'

        census_blocks = census_blocks.to_crs(crs)
        precincts = precincts.to_crs(crs)
        districts = districts.to_crs(crs)

        ##########
        # Population
        # Add with interpolations
        ##########

        # Make sure OBJECTID unique
        assert not precincts.OBJECTID.duplicated().any()
        
        census_blocks = census_blocks[['POP10', 'BLOCKID10', 'geometry']]
        census_blocks['pre_split_area'] = census_blocks.area
 
        # Get all intersections
        intersections = gpd.overlay(census_blocks, precincts, how='intersection')
        
        # Do interpolations
        intersections['population'] = intersections.POP10 * (intersections.area / 
                                                             intersections['pre_split_area'])
        
        # More sanity checks, 'cause this stuff is easy to get wrong. 
        intersections['share_in_precinct'] = intersections.area / intersections['pre_split_area']
        assert (intersections['share_in_precinct'] <=1.01).all()
        intersections['current_fragment_area'] = intersections.area
        intersections['new_block_summed_area'] = intersections.groupby('BLOCKID10').current_fragment_area.transform(sum)
        assert ((intersections['new_block_summed_area'] / 
                intersections['pre_split_area']) <= 1.01).all()
        
        assert (intersections['new_block_summed_area'] / 
                intersections['pre_split_area']).mean() > 0.8
        
        # Actual population interpolation
        intersections['population'] = intersections.POP10 * intersections['share_in_precinct']
        
        precinct_pops = intersections[['OBJECTID', 'population']].groupby('OBJECTID',
                                                                   as_index=False).sum()
        
        precincts = precincts.merge(precinct_pops, on='OBJECTID', 
                                    how='outer', validate='1:1', indicator=True)
        # Check re-merge. 
        if state_fips == '30':
            assert precincts._merge.value_counts(normalize=True).loc['both'] > 0.99
        else: 
            assert (precincts._merge == 'both').all()

        precincts = precincts.drop('_merge', axis='columns')

        # Check my work
        vote_totals = precincts['P2008_D'] + precincts['P2008_R']
        corr = np.corrcoef(vote_totals[precincts.population > 10].values, 
                           precincts[precincts.population > 10].population.values)[0,1]
        
        assert corr > 0
        print(f'correlation between vote totals and'
              f'population for fips {state_fips} is {corr:.3f}')
                
        ###########
        # Put district
        # into precincts
        ###########

        import maup

        # Districts
        district_assignment = maup.assign(precincts, districts)
        precincts["district"] = district_assignment
        
        ###########
        # Deal with NAs
        ###########

        import pandas as pd

        missing = pd.isnull(precincts['district']) | pd.isnull(precincts['population'])

        if (missing.sum() / len(precincts)) > 0.001:
            raise ValueError("missing district or population data for more than 0.1% of precincts"
                             f"in state fips {state_fips}")

        print(f'missing {missing.sum() / len(precincts)}')
        precincts = precincts[~missing]

        ###########
        # Save
        ###########

        f = f'../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp'
        precincts.to_file(f)
        print(f'finished {state_fips}')
