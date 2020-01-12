import geopandas as gpd
import os
import pickle
import numpy as np
import gerrychain as gc

indices=['01',
        '04',
        '05',
        '06',
        '08',
        '09',
        '10',
        '11',
        '12',
        '13',
        '16',
        '17',
        '18',
        '19',
        '20',
        '21',
        '22',
        '23',
        '24',
        '25',
        '26',
        '27',
        '28',
        '29',
        '31',
        '32',
        '33',
        '34',
        '35',
        '36',
        '37',
        '38',
        '39',
        '40',
        '42',
        '44',
        '45',
        '46',
        '47',
        '48',
        '49',
        '50',
        '51',
        '53',
        '54',
        '55',
        '56']
        
        
for state_fips in indices:

    graph = Graph.from_json(f"../20_intermediate_files/precinct_graphs/precinct_graphs_{state_fips}_seed0.json")
    
    election = Election("PRES2008", {"Dem": "P2008_D", "Rep": "P2008_R"})

    initial_partition = Partition(
        graph,
        assignment='district',
        updaters={
            "cut_edges": cut_edges,
            "population": Tally("population", alias="population"),
            "PRES2008": election
        }
    )
    

    
    
    
    
