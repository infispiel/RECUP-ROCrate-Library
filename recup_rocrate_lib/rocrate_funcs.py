from rocrate.rocrate import ROCrate
from rocrate.model.contextentity import ContextEntity

import re
from rocrate.model.softwareapplication import SoftwareApplication
import os

class ct_rocrate_manager : #ct = chimbuko/tau
    crate = None
    wf_obj = None

    defined_func_files = {}
    defined_funcs = {}
    defined_func_call_objs = {}
    defined_func_calls = {}
    
    chimbuko_funcname_regex = re.compile('(?P<funcname>[^\s]+) \[\{(?P<funcfile>[^\s]+)\} \{(?P<funcline>[0-9]+),(?P<funccol>[0-9]+)\}\]')
    
    def __init__(self) :
        self.crate = ROCrate()
        
        # TODO : technically, a ComputationalWorkflow entity requires the SoftwareSource @type.
        #        but, that's not really applicable in this case. Find an alternative labelling? *DEFINE* an
        #        alternative labelling?
        self.wf_obj = ContextEntity(self.crate, None, properties={
            "@type": ["ComputationalWorkflow"]
            })
        self.crate.add(self.wf_obj)
        
    def no_duplicate_add(self, inp_dic, inp_key, inp_val) :
        '''
        Temporary function to ensure keys do not already exist when adding to a dictionary.
        '''
        if inp_key not in inp_dic.keys() :
            inp_dic[inp_key] = inp_val
        else :
            raise ValueError("Attempted to add key %s to dictionary where key already exists.\n" % inp_key)
        
    def chimbuko_strip_func_info(self, entry) :
        '''
        Strips out function name information from a Chimbuko Provenance DB CallStack entry.
        '''
        res = re.search(self.chimbuko_funcname_regex, entry['func'])

        # Create SoftwareApplication object for the function itself
        func_file = None
        func_loc = None
        func_filename = ""
        
        if res is not None :
            func_name = res.group('funcname')
            func_file = res.group('funcfile')
            func_loc = (int(res.group('funcline')), int(res.group('funccol')))
            func_filename = os.path.basename(func_file)

        else :
            func_name = entry['func']
            
        return (func_name, func_file, func_loc, func_filename)
    
    def add_all_function_info(self, func_name, func_file, func_loc, func_filename, n_entry, n_tot_entries, entry) :
        '''
        Given a function call, adds its:
        - defining function file
        - defined function
        - function call theoretical concept object
        - function call object

        To the relevant dictionaries and the workflow object.
        '''
        ff_tid = self.add_function_file(func_filename, entry)
        f_tid = self.add_func(func_name, func_file, func_loc, func_filename)
        fcc_tid = self.add_func_call_concept(f_tid, n_entry, n_tot_entries)
        fc_tid = self.add_func_call(entry, fcc_tid, f_tid)
        
    def add_function_file(self, func_filename) :
        '''
        Creates an ROCrate Profile SoftwareApplication object to store function file information.
        Adds this object to the corresponding dictionary (self.defined_func_files) and appends it to 
        the workflow object's hasPart property.
        '''
        tid = func_filename
        if tid in self.defined_func_files.keys() :
            pass
        else :
            temp_func = SoftwareApplication(self.crate, tid, 
                properties={
                    '@type': ['File', 'SoftwareApplication'],
                })
            self.no_duplicate_add(self.defined_func_files, tid, temp_func)
            self.wf_obj.append_to('hasPart', {'@id': temp_func['@id']})

        return tid
    
    def add_func(self, func_name, func_file, func_loc, func_filename) :
        '''
        Creates an ROCrate Profile SoftwareApplicatio nobject to sture function information.
        Adds this object to the corresponding dictionary (self.defined_funcs) and appends it to
        the parent function file's hasPart property.
        '''
        tid = func_filename + "#" + func_name
        temp_func = SoftwareApplication(self.crate, tid, properties={
            "name": func_name,
            "location": func_loc # TODO : check if exists equivalent attribute
        })
        
        self.no_duplicate_add(self.defined_funcs, tid, temp_func)
        self.defined_func_files[func_filename].append_to('hasPart', {'@id': tid})
        return tid
    
    def add_func_call_concept(self, f_tid, n_entry, n_tot_entries) :
        '''
        Creates an ROCrate Profile ContextEntity with type HowToStep to store theoretical function call information.
        Adds this object to the corresponding dictionary (self.defined_func_call_objs).
        '''
        tid = f_tid + ".STEP"
        temp_howto = ContextEntity(self.crate, tid,
            properties={
                "@type": "HowToStep",
                "workExample": {'@id': f_tid},
                "position": str((n_tot_entries - n_entry) - 1)
            })
        self.no_duplicate_add(self.defined_func_call_objs, tid, temp_howto)
        self.wf_obj.append_to('step', {'@id': temp_howto['@id']})
        return tid
    
    def add_func_call(self, entry, func_concept_tid, func_id) :
        tid = entry['event_id']
        temp_create = ContextEntity(self.crate, tid, properties={
            "@type": "CreateAction",
            # TODO: what format are entry, exit stored in? doesn't appear to be epoch
            "endTime": entry['exit'], #datetime.fromtimestamp(entry['exit']),
            "startTime": entry['entry'], #datetime.fromtimestamp(entry['entry']),
            "instrument": {"@id": func_concept_tid},
            "name": "Run of function " + self.defined_funcs[func_id]['name'],
            "is_anomaly": entry['is_anomaly'] 
            # TODO: I think there needs to be a better organization for is_anomaly.
            # Technically, can create a calling ControlAction, whose 'actionStatus' attribute
            #   can either be CompletedActionStatus or FailedActionStatus to represent
            #   (anomaly|non-anomalous).W
        })
        self.no_duplicate_add(self.defined_func_calls, tid, temp_create)
        return tid
        
    def export_crate(self):
        for k,v in self.defined_func_files.items() :
            self.crate.add(v)
        for k,v in self.defined_funcs.items() :
            self.crate.add(v)
        for k,v in self.defined_func_call_objs.items() :
            self.crate.add(v)
        for k,v in self.defined_func_calls.items() :
            self.crate.add(v)
        self.crate.write("exp_crate")
        