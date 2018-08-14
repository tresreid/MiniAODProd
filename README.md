# MiniAODProd w/o pileup mixing

Generating MiniAOD without pileup mixing from gridpack, by making use of CMSLPC condor system at FNAL.

## Notes
1. Hadronizer fragment defined in conf/ directory, customize according to needs.
2. In the end, condor will transfer AOD and MiniAOD file to your cmseos place at CMSLPC. 
[Look here](https://github.com/phylsix/MiniAODProd/blob/lpc-dev17-nopu/submit.py#L13-L15),
make sure it exists.
3. Place gridpack in gridpacks/ folder, submitting my calling `./submit.sh`. 
Inside, it will get voms certificate first, then calling
`./submit.py <gridpack name> <Njobs>`, each job will generate 1000 events, defined [here](https://github.com/phylsix/MiniAODProd/blob/lpc-dev17-nopu/runOffGridpack.sh#L15).
4. For SIDM, dark photon's lifetime needs to be externally replaced by calling this `replaceLHELifetime.py`, 
if this is not desired for you, comment out [this line](https://github.com/phylsix/MiniAODProd/blob/lpc-dev17-nopu/runOffGridpack.sh#L39).
