#! /bin/bash

## Usage: ./runOffGridpack.sh SIDMmumu_Mps-200_MZp-1p2_ctau-0p1.tar.xz 1

export BASEDIR=`pwd`
GP_f=$1
#CTau_mm=$2
GRIDPACKDIR=${BASEDIR}/gridpacks
LHEDIR=${BASEDIR}/mylhes
SAMPLEDIR=${BASEDIR}/samples
[ -d ${LHEDIR} ] || mkdir ${LHEDIR}

HADRONIZER="externalLHEProducer_and_PYTHIA8_Hadronizer.py"
namebase=${GP_f/.tar.xz/}
#nevent=2
nevent=1000

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

export SCRAM_ARCH=slc6_amd64_gcc481
if ! [ -r CMSSW_9_4_9/src ] ; then
    scram p CMSSW CMSSW_9_4_9
fi
cd CMSSW_9_4_9/src
eval `scram runtime -sh`
scram b -j 4
tar xaf ${GRIDPACKDIR}/${GP_f}
sed -i 's/exit 0//g' runcmsgrid.sh
ls -lrth

RANDOMSEED=`od -vAn -N4 -tu4 < /dev/urandom`
#Sometimes the RANDOMSEED is too long for madgraph
RANDOMSEED=`echo $RANDOMSEED | rev | cut -c 3- | rev`

echo "0.) Generating LHE"
sh runcmsgrid.sh ${nevent} ${RANDOMSEED} 4
namebase=${namebase}_$RANDOMSEED
for CTau_mm in 1 10 100 1000 10000
do
	namebase1=${namebase}_ctau-${CTau_mm}
	echo "    Replace lifetime for LHE.. ${CTau_mm}"
	python ${BASEDIR}/replaceLHELifetime.py -i cmsgrid_final.lhe -t ${CTau_mm}
	cp cmsgrid_final.lhe ${LHEDIR}/${namebase1}.lhe
	echo "${LHEDIR}/${namebase1}.lhe" 
	allpacks+=("${namebase1}")
done
rm -rf *
cd ${BASEDIR}
echo ${allpacks[@]}

export SCRAM_ARCH=slc6_amd64_gcc630
if ! [ -r CMSSW_9_4_9/src ] ; then
    scram p CMSSW CMSSW_9_4_9
fi
cd CMSSW_9_4_9/src
rm -rf *
mkdir -p Configuration/GenProduction/python/
cp ${BASEDIR}/conf/${HADRONIZER} Configuration/GenProduction/python/
eval `scram runtime -sh`
scram b -j 4
for namebase in ${allpacks[@]}
do
echo "${namebase}"
echo "1.) Generating GEN-SIM"
genfragment=${namebase}_GENSIM_cfg.py
cmsDriver.py Configuration/GenProduction/python/${HADRONIZER} \
    --filein file:${LHEDIR}/${namebase}.lhe \
    --fileout file:${namebase}_GENSIM.root \
    --mc --eventcontent RAWSIM --datatier GEN-SIM \
    --conditions auto:phase1_2017_realistic --beamspot Realistic25ns13TeVEarly2017Collision \
    --step GEN,SIM --era Run2_2017 --nThreads 8 \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --python_filename ${genfragment} --no_exec -n ${nevent} || exit $?;

#Make each file unique to make later publication possible
linenumber=`grep -n 'process.source' ${genfragment} | awk '{print $1}'`
linenumber=${linenumber%:*}
total_linenumber=`cat ${genfragment} | wc -l`
bottom_linenumber=$((total_linenumber - $linenumber ))
tail -n $bottom_linenumber ${genfragment} > tail.py
head -n $linenumber ${genfragment} > head.py
echo "    firstRun = cms.untracked.uint32(1)," >> head.py
echo "    firstLuminosityBlock = cms.untracked.uint32($RANDOMSEED)," >> head.py
cat tail.py >> head.py
mv head.py ${genfragment}
rm -rf tail.py

cmsRun -p ${genfragment}

echo "2.) Generating DIGI-RAW-HLT"
cmsDriver.py step1 \
    --filein file:${namebase}_GENSIM.root \
    --fileout file:${namebase}_DIGIRAWHLT.root \
    --era Run2_2017 --conditions 94X_mc2017_realistic_v12 \
    --mc --step DIGI,L1,DIGI2RAW,HLT:2e34v40 \
    --datatier GEN-SIM-DIGI-RAWHLTDEBUG --eventcontent FEVTDEBUGHLT \
    --number ${nevent} \
    --geometry DB:Extended --nThreads 8 \
    --python_filename ${namebase}_DIGIRAWHLT_cfg.py \
    --customise Configuration/DataProcessing/Utils.addMonitoring \
    --no_exec || exit $?;
cmsRun -p ${namebase}_DIGIRAWHLT_cfg.py

echo "3.) Generating AOD"
cmsDriver.py step2 \
    --filein file:${namebase}_DIGIRAWHLT.root \
    --fileout file:${namebase}_AOD.root \
    --mc --eventcontent AODSIM --datatier AODSIM --runUnscheduled \
    --conditions auto:phase1_2017_realistic --step RAW2DIGI,L1Reco,RECO \
    --nThreads 8 --era Run2_2017 --python_filename ${namebase}_AOD_cfg.py --no_exec \
    --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevent} || exit $?;
cmsRun -p ${namebase}_AOD_cfg.py

#echo "4.) Generating MINIAOD"
#cmsDriver.py step3 \
#    --filein file:${namebase}_AOD.root \
#    --fileout file:${namebase}_MINIAOD.root \
#    --mc --eventcontent MINIAODSIM --datatier MINIAODSIM --runUnscheduled \
#    --conditions auto:phase1_2017_realistic --step PAT \
#    --nThreads 8 --era Run2_2017 --python_filename ${namebase}_MINIAOD_cfg.py --no_exec \
#    --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevent} || exit $?;
#cmsRun -p ${namebase}_MINIAOD_cfg.py

pwd
cmd="ls -arlth *.root"
echo $cmd && eval $cmd

echo "DONE."
#done
#echo "ALL Done"

remoteDIR="/store/user/mreid/standaloneComp/iDM/redone"
for f in `ls *AOD*.root`; do
    cmd="xrdcp -vf file:///$PWD/$f root://cmseos.fnal.gov/$remoteDIR/$f"
    echo $cmd && eval $cmd
done
done
echo "all Done"
