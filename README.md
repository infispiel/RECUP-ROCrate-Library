TODO : move all my discussion/thoughts from the jupyter notebooks to this file.

# Converting Chimbuko Provenance Database Entries into Partial RO-Crates

## Requirements

This library requires the rocrate, provdb_python, and pymargo libraries. I recommend using the [chimbuko docker image](https://hub.docker.com/r/chimbuko/provdb-python/tags) created by Christopher Kelly, although you still need to install the `rocrate` library in this image.

(Note for myself, use the following commands to run this docker image on wsl:)

```sh
sudo dockerd > /dev/null 2>&1 &

docker run --rm -it -v ~/research/RECUP/chimbuko_metadata:/jupyter/external --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -p 8888:8888 chimbuko/provdb-python:ubuntu18.04
```


## Overview

The purpose of this library is to provide a set of tools with which a user can convert an entry in (or the entirety of) the Chimbuko provenance database into an RO-Crate Provenance Run Crate, described [here](https://www.researchobject.org/workflow-run-crate/profiles/provenance_run_crate).

A key thing to be aware of is that it is impossible to completely fulfill the requirements of the Provenance Run Crate only using metadata available to Chimbuko. Therefore, the intent is not to create a complete crate but rather a "Partial RO-Crate" (official specification pending). 

The overall expectation of the Provenance Run Crate is shown below. (Figure from the link above.)

<div>
<img src="https://www.researchobject.org/workflow-run-crate/profiles/img/er_diagram_provenance.svg" width="500"/>
</div>

Out of all of these portions, the Chimbuko provenance database is only able to describe the upper right triangle of requirements, as will be described below.

## Structure of Chimbuko Provenance Database Entries

Each database entry refers to an anomalous function event. This event contains information such as (algorithmic) and the call stack leading up to the anomalous function execution. Therefore, the overall call stack can be considered a representation of the full workflow that was in progress at time of anomaly, and each function can be considered a step of the workflow.

To represent this in the terms of the Provenance Run Crate, the overall workflow becomes the `ComputationalWorkflow`. It has Steps of `HowToStep`, which point to the functions that are represented as `SoftwareApplication`s. The files these functions are stored in are also stored as `SoftwareApplication`s. Finally, the actual result of running the application, including whether or not the execution was anomalous, is represented as a `CreateAction`. 

TODO: figure out whether OrganizeAction and ControlAction are representable, and also note down the annotation of other functions that were executing at the same time as the anomaly (event_window, exec_window). Anomaly information (e.g. histogram, etc) may be part of OrganizeAction?

## Additional Development

Chimbuko provenance database entries also contain hostname, tid, pid, and rid information. These peices of information may be able to link the function call back to the hardware used in the call, which may be used to obtain hardware metadata information. ("metadata" db information?)

The following metadata still needs to find an equivalent in the RO-Crate Profile:

- anomaly detection algorithm params/results
- exec_window function information
- comm_window information
- counter_events -> should this maybe be turned into a data file instead?
