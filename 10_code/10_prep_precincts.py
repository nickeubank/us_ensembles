import geopandas as gpd
import os
import pickle

os.chdir('/users/nick/github/us_ensembles')


###########
# Get environment var from SLURM
# and convert
###########

# state = os.getenv('STATE')
state = 0  
f='20_intermediate_files/sequential_to_fips.pickle'
state_fips = pickle.load(open(f, "rb" ))[state]

###########
# Bring in precincts, population, 
# and current districts
###########

# Precinct
precincts = gpd.read_file("./00_source_data/votes/"
                          "2008_presidential_precinct_counts2.shp")

precincts = precincts[['OBJECTID', 'P2008_D', 'P2008_R', 
                       'STATE', 'COUNTY', 'geometry']]
(~precincts.is_valid).sum()
precincts = precincts[precincts.STATE == state_fips]
assert str(precincts.crs) == "{'init': 'epsg:3085'}"
precincts.loc[~precincts.is_valid, 'geometry'] = precincts.loc[~precincts.is_valid, 'geometry'].simplify(0.00005, preserve_topology=False)
assert precincts.is_valid.all()


# Census blocks
f_blocks = f'./00_source_data/census_blocks/tabblock2010_{state_fips}'\
           f'_pophu/tabblock2010_{state_fips}_pophu.shp'

census_blocks = gpd.read_file(f_blocks)

assert census_blocks.is_valid.all()

# Legislative Districts
districts = gpd.read_file('./00_source_data/legislative_districts/'
                          'nhgis0190_shapefile_tl2014_us_cd114th_2014/'
                          'US_cd114th_2014.shp')

districts = districts[districts['STATEFP'] == state_fips]

districts = districts[['STATEFP', 'CD114FP', 'GEOID', 'geometry']]

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

# import maup
# district_assignment = maup.assign(precincts, districts)
# precincts["DISTRICT"] = district_assignment

# assignment = maup.assign(census_blocks, precincts)
# precincts[variables] = blocks[variables].groupby(assignment).sum()
# precincts[variables].head()