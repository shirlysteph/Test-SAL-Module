# Test SAL Module

## Overview
This sample SAL Module implements a new `salmodule:Task` subclass named `CommunityWaterSystemFeature` Public Water System Service Areas Boundary features from EPA's [Feature Service](https://www.epa.gov/ground-water-and-drinking-water/public-water-system-service-areas?tab=resources). 

## Assumptions

The following doc assume a unix command line environment.


## Usage

The following sections detail this SALModule's implementation of the SAL Module command line interface specification 

### Building the SAL Module

From this git repository's root directory run:

`docker build . -t sample-sal-module` 

### Fetching the SAL Module's ontology

`docker run sample-sal-module salmodule ontology`

### Running the SAL Modules Tasks

`docker run --rm \                  
  -e SALMODULE_TASK_INSTANCE="$(cat SALMODULE_TASK_INSTANCE.json)" \
  --mount type=bind,source="$(pwd)",target=/output \
  sample-sal-module \
  salmodule run
`
