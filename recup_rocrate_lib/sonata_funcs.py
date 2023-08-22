import provdb_python.provdb_interact as pi
#import provdb_python.provdb_analyze as pa
#import provdb_python.provdb_counter_analyze as pca
#import provdb_python.provdb_between_run_analyze as pbr
#import provdb_python.provdb_viz_validate as pvv

import pymargo
from pymargo.core import Engine

#from pysonata.provider import SonataProvider
#from pysonata.client import SonataClient
#from pysonata.admin import SonataAdmin

import os
import glob
#os.chdir('/home/bld/AD/develop2/benchmark_suite/func_multimodal/chimbuko/provdb')

def get_raw_db_access() :
    dbs = glob.glob("provdb.*.unqlite")
    nshards=len(dbs)-1 #get the number of shards in the directory (exclude the global dir)
    print("Found %d shards" % nshards)
    engine = Engine('na+sm', pymargo.server) 
    db = pi.provDBinterface(engine, 'provdb.%d.unqlite', nshards)
    return db

def get_chimbuko_generator(directory: str, filename_glob: str) :  
    # NOTE :
    # this was initially to provide JSON from the db entries as a generator.
    # I think it should be reworked to provide the entries themselves as a 
    #   generator, because that way we don't combine RO-crate and sonata
    #   concerns.

    # should also still keep raw db access in case someone wants to only
    #   handle a specific entry & they know how to access it.

    os.chdir(directory)
    # TODO: filename_glob use; need to use it here and in provDBinterface w/ numbers...
    dbs = glob.glob('provdb.*.unqlite')
    
    nshards=len(dbs)-1
    print("Found %d shards" % nshards)
    engine = Engine('na+sm', pymargo.server)
    db = pi.provDBinterface(engine, 'provdb.%d.unqlite', nshards)
    
    anom_coll = 'anomalies'
    for shard_id in range(0, nshards) :
        anom_coll_sz = db.getShard(shard_id).size(anom_coll)
        print("Found %d anomalies in shard 0" % anom_coll_sz)

        # now we iterate through the anomaly columns.
        for i in range(0, anom_coll_sz) :
            dat = db.getShard(shard_id).fetch(anom_coll, i)

            # reformat the output
            properties = {}
            properties['@type'] = "CHIMBUKO_EVENT" # TODO: ??
            properties['name'] = dat['event_id']   # set name to Chimbuko event id
            properties['sonata_id'] = dat['__id']  # keep sonata id for posterity
            
            # ..
            
            # annotate which algorithm is being represented.
            if 'histogram' in dat['algo_params'].keys() :
                properties['algo'] = 'HBOS/COPOD'
            else :
                properties['algo'] = 'SSTD'
            
            # NOTE: At least 1 anomaly in every call stack? (maybe exactly 1?)
                
            yield properties