import geopandas as gpd
import os
import pickle

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
precincts = gpd.read_file("../00_source_data/votes/"
                          "2008_presidential_precinct_counts.shp")

precincts = precincts[['OBJECTID', 'P2008_D', 'P2008_R', 
                       'STATE', 'COUNTY', 'geometry']]

# District Maps
districts = gpd.read_file('../00_source_data/legislative_districts/'
                          'nhgis0190_shapefile_tl2014_us_cd114th_2014/'
                          'US_cd114th_2014.shp')

districts = districts[['STATEFP', 'CD114FP', 'GEOID', 'geometry']]

########
# Loopz
########

for idx, state_fips in enumerate(state_fips_codes):
    print(f'on step {idx}, fips {state_fips}')

    ###########
    # Bring in precincts, population, 
    # and current districts
    ###########
    
    precincts = precincts[precincts.STATE == state_fips].copy()
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
    districts = districts[districts['STATEFP'] == state_fips].copy()

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
    assignment = maup.assign(census_blocks, precincts)
    precincts['population'] = census_blocks['POP10'].groupby(assignment).sum()
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
    assert (missing.sum() / len(precincts)) < 0.005
    precincts = precincts[~missing]

    ###########
    # Save
    ###########

    f = f'../20_intermediate_files/pre_processed_precinct_maps/precincts_{state_fips}.shp'
    #precincts_no_overlaps_or_gaps.to_file(f)
    precincts.to_file(f)
    print(f'finished {state_fips}')
