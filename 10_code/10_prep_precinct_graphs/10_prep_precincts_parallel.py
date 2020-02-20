import geopandas as gpd
import os
import pickle
import numpy as np

###########
# Helper functions
###########

def check_intersection_validity(intersections, precincts, state_fips):
        assert (intersections['share_in_precinct'] <=1.01).all()
        intersections['current_fragment_area'] = intersections.area
        intersections['new_block_summed_area'] = intersections.groupby('GISJOIN'
                                                ).current_fragment_area.transform(sum)

        # Check area splits obey logical math
        if state_fips in ['12', '36']:
            # Florida has some small precinct overlaps
            # NY has one pair of precincts 
            # with same geography. Too small to hunt. 
            test = (intersections['new_block_summed_area'] / 
                    intersections['pre_split_area']) > 1.01
            assert test.sum() / len(intersections) < 0.01
        elif state_fips == '30':
            test = (intersections['new_block_summed_area'] / 
                    intersections['pre_split_area']) > 1.01
            assert test.sum() / len(intersections) < 0.03
        else: 
            assert ((intersections['new_block_summed_area'] / 
                    intersections['pre_split_area']) <= 1.01).all()

        assert (intersections['new_block_summed_area'] / 
                intersections['pre_split_area']).mean() > 0.8

        # Check more people -> more votes. 
        vote_totals = precincts['P2008_D'] + precincts['P2008_R']
        corr = np.corrcoef(vote_totals[precincts.pop_total > 10].values, 
                           precincts[precincts.pop_total > 10].pop_total.values)[0,1]
        
        if state_fips != '44':
            # Rhode Island doesn't have enough variation / N to 
            # get LLN. 
            assert corr > 0
            print(f'correlation between vote totals and'
                  f'population for fips {state_fips} is {corr:.3f}')

############
# Master function for
# prepping shapefile
# Written as try-except for 
# running quickly in parallel. 
############

def setup_state_by_fips(args):

    state_fips, master_precincts, master_districts = args

    try: 
        print(f'on fips {state_fips}', flush=True)

        ###########
        # Bring in precincts, population, 
        # and current districts
        ###########
        
        # Montana required extra processing in ArcGIS for
        # some bad tracing
        if state_fips == '30':
            master_precincts = gpd.read_file("../00_source_data/votes/"
                                             "montana_with_arcprocessing.shp")
        
        precincts = master_precincts[master_precincts.STATE == state_fips].copy()
        
        if len(precincts) == 0:
            raise ValueError(f"no precincts for fips {state_fips}")

        # Topology problems
        assert str(precincts.crs) == "{'init': 'epsg:3085'}"
        precincts.loc[~precincts.is_valid, 'geometry'] = precincts.loc[~precincts.is_valid, 
                                                                       'geometry'].buffer(0)
        assert precincts.is_valid.all()

        ######
        # Census blocks
        ######
        
        f_blocks = f'../00_source_data/census_blocks_w_race/prepped_census.shp'

        # FL and NY have some places with census blocks but no precincts (e.g. federal parks). 
        # Causes later problems.
        #if state_fips in ['12', '36']:
        #    f_blocks = f'../00_source_data/census_blocks/tabblock2010_{state_fips}'\
        #               f'_pophu_clipped/tabblock2010_{state_fips}_pophu_clipped.shp'
            
        census_blocks = gpd.read_file(f_blocks)
        census_blocks = census_blocks[census_blocks.STATEFP10 == state_fips]

        assert census_blocks.is_valid.mean() > 0.95
        
        census_blocks.loc[~census_blocks.is_valid, 'geometry'] = census_blocks.loc[ 
                                                                   ~census_blocks.is_valid, 
                                                                   'geometry'].buffer(0)
        assert census_blocks.is_valid.all()

        ######
        # Legislative Districts
        ######
        
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
        
        population_fields = ['pop_total', 'pop_VAP', 'pop_BVAP', 'pop_HVAP']
        census_blocks = census_blocks[population_fields + ['geometry', 'GISJOIN']]
        census_blocks['pre_split_area'] = census_blocks.area
 
        # Get all intersections
        intersections = gpd.overlay(census_blocks, precincts, how='intersection')
        
        # Do interpolations
        intersections['share_in_precinct'] = intersections.area / intersections['pre_split_area']

        for p in population_fields:
            intersections[p] = intersections[p] * intersections['share_in_precinct']
        
        precinct_pops = intersections[['OBJECTID'] + population_fields].groupby('OBJECTID',
                                                                   as_index=False).sum()
        
        precincts = precincts.merge(precinct_pops, on='OBJECTID', 
                                    how='outer', validate='1:1', 
                                    indicator=True)
        # Check re-merge. 
        assert precincts._merge.value_counts(normalize=True).loc['both'] > 0.99
        if not (precincts._merge == 'both').all():
            assert (precincts[precincts._merge == 'left_only'].P2008_D == 0).all()

        precincts = precincts.drop('_merge', axis='columns')
        
        # Check my work
        assert precincts.is_valid.mean() > 0.95
        
        precincts.loc[~precincts.is_valid, 
                      'geometry'] = precincts.loc[ ~precincts.is_valid, 
                                                  'geometry'].buffer(0)

        check_intersection_validity(intersections, precincts, state_fips)
                
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

        missing = pd.isnull(precincts['district']) | pd.isnull(precincts['pop_total'])

        # only one close is Washington with a few missing districts. 
        # in island land. 
        # But those get re-seeded later. 

        if (missing.sum() / len(precincts)) > 0.0025:
            raise ValueError("missing district or population data"
                             "for more than 0.25% of precincts"
                             f"in state fips {state_fips}")

        print(f'missing {missing.sum() / len(precincts)}', flush=True)
        precincts = precincts[~missing]

        ###########
        # Save
        ###########

        f = f'../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp'
        precincts.to_file(f)
        print(f'finished {state_fips}', flush=True)
        return None
    except: 
        print(f'FAILED FAILED FAILED {state_fips}')
        return state_fips

#######
# Actual run
#######

from joblib import Parallel, delayed

f='../20_intermediate_files/sequential_to_fips.pickle'
state_fips_codes = sorted(list(pickle.load(open(f, "rb" )).values()))

##
# Loads used for all passes
##

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

##
# And... EXECUTE!
##

results = (Parallel(n_jobs=4, verbose=10, backend='multiprocessing')
           (delayed(setup_state_by_fips)
           ((fips, master_precincts, master_districts)) for fips in state_fips_codes)
          )


