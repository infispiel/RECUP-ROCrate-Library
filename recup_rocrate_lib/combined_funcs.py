from rocrate_funcs import ct_rocrate_manager
from sonata_funcs import get_raw_db_access

def main() :
    db = get_raw_db_access()
    anom_coll = 'anomalies'
    anom_coll_sz = db.getShard(0).size(anom_coll)

    dat = db.getShard(0).fetch(anom_coll,1)
    dat

    mngr = ct_rocrate_manager()
    # for now this is just running on the very first anomaly in the very first shard.
    for shard in range(0, 1) :
        #for id in range(0, anom_coll_sz) :
        for id in range(0, 1) :
            dat = db.getShard(shard).fetch(anom_coll, id)
            function_descriptors = [entry['func'] for entry in dat['call_stack']]
            l_callstack = len(dat['call_stack'])
            print(function_descriptors)
            for i, entry in enumerate(dat['call_stack']): 
                res = mngr.chimbuko_strip_func_info(entry)
                mngr.add_all_function_info(*res, i, l_callstack, entry)
                
            mngr.export_crate()
            
if __name__ == "main" :
    # parse args
    main()
    pass
