import geopandas as gpd
import os
import pickle

###########
# Get environment var from SLURM
# and convert
###########

# state = os.getenv('STATE')

def setup_state_by_fips(bundle):

    # Unbundle args. Can only pass 1 to joblib. 
    state_fips, precincts, districts = bundle

    try: 
        ###########
        # Bring in precincts, population, 
        # and current districts
        ###########

        precincts = master_precincts[master_precincts.STATE == state_fips].copy()

        if len(precincts) == 0:
            raise ValueError(f"no precincts for fips {state_fips}")

        assert str(precincts.crs) == "{'init': 'epsg:3085'}"

        # Topology problems
        precincts.loc[~precincts.is_valid, 'geometry'] = precincts.loc[~precincts.is_valid, 'geometry'].buffer(0)
        assert precincts.is_valid.all()

        # Census blocks
        f_blocks = f'../00_source_data/census_blocks/tabblock2010_{state_fips}'\
                   f'_pophu/tabblock2010_{state_fips}_pophu.shp'

        census_blocks = gpd.read_file(f_blocks)

        assert census_blocks.is_valid.all()

        # Legislative Districts
        districts = master_districts[master_districts['STATEFP'] == state_fips].copy()

        # Topology problems
        districts.loc[~districts.is_valid, 'geometry'] = districts.loc[~districts.is_valid, 'geometry'].buffer(0)
        assert districts.is_valid.all()


        #########
        # Common reprojection
        #########

        crs = 'EPSG:3085'

        census_blocks = census_blocks.to_crs(crs)
        precincts = precincts.to_crs(crs)
        districts = districts.to_crs(crs)

        ###########
        # Put population and district
        # into precincts
        ###########

        import maup

        # Districts
        district_assignment = maup.assign(precincts, districts)
        precincts["district"] = district_assignment

        # Population 
        
        # have to drop census blocks that fully miss precincts (very rare, but happens.)
        # e.g. everglade reserve in FL
        precincts_unary = precincts.geometry.unary_union
        intersecting_census_blocks = gpd.sjoin(census_blocks, precincts[['district', 'geometry']], 
                                               how='inner', op='intersects')
        intersecting_census_blocks = intersecting_census_blocks.drop('district', axis='columns').drop_duplicates()
        assignment = maup.assign(intersecting_census_blocks, precincts)
        precincts['population'] = intersecting_census_blocks['POP10'].groupby(assignment).sum()
        precincts['population'].head()

        ###########
        # Fill gaps and overlaps
        ###########
        #precincts_no_overlaps = maup.resolve_overlaps(precincts)
        #precincts_no_overlaps_or_gaps = maup.resolve_gaps(precincts_no_overlaps)

        ###########
        # Deal with NAs
        ###########

        import pandas as pd

        missing = pd.isnull(precincts['district']) | pd.isnull(precincts['population'])

        if (missing.sum() / len(precincts)) > 0.005:
            raise ValueError("missing district or population data for more than 5% of precincts"
                             f"in state fips {state_fips}")

        precincts = precincts[~missing]

        ###########
        # Save
        ###########

        f = f'../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp'
        #precincts_no_overlaps_or_gaps.to_file(f)
        precincts.to_file(f)
        print(f'finished {state_fips}')
        return None
    except: 
        print(f'failed {state_fips}')
        return state_fips

#######
# Actual run
#######

from joblib import Parallel, delayed

f='../20_intermediate_files/sequential_to_fips.pickle'
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

#######
# And... EXECUTE!
#######

results = (Parallel(n_jobs=10, verbose=5, backend='multiprocessing')
           (delayed(setup_state_by_fips)
           ((fips, master_precincts, master_districts)) for fips in state_fips_codes)
          )