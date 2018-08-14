import FWCore.ParameterSet.Config as cms


from Configuration.Generator.Pythia8CommonSettings_cfi import *
#from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.Pythia8CUEP8M1Settings_cfi import *


# Avoid to have multiple lumi in the same job and therefore auto-cleaning
# This means that it need an argument to be run
# from FWCore.ParameterSet.VarParsing import VarParsing
# options = VarParsing ('analysis')
# options.register('jobNum', 0, VarParsing.multiplicity.singleton,VarParsing.varType.int,"jobNum")
# options.parseArguments ()
# firstLumi=10*options.jobNum+1 ## eventsPerJob/eventsPerLumi*jobNum +1
# source = cms.Source("EmptySource",
#         firstLuminosityBlock  = cms.untracked.uint32(firstLumi),
#         numberEventsInLuminosityBlock = cms.untracked.uint32(100)
#         )




# External LHE producer configuration
#externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
#    args = cms.vstring( 'THISDIR' + '/GRIDPACKNAME'),
#    nEvents = cms.untracked.uint32(5000),
#    numberOfParameters = cms.uint32(1),
#    outputFile = cms.string('cmsgrid_final.lhe'),
#    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
#)


# Hadronizer configuration
generator = cms.EDFilter("Pythia8HadronizerFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CUEP8M1SettingsBlock,
        processParameters = cms.vstring(
            'JetMatching:setMad = off',
            'JetMatching:scheme = 1',
            'JetMatching:merge = on',
            'JetMatching:jetAlgorithm = 2',
            'JetMatching:etaJetMax = 5.',
            'JetMatching:coneRadius = 1.',
            'JetMatching:slowJetPower = 1',
            'JetMatching:qCut = 30', #this is the actual merging scale
            'JetMatching:nQmatch = 4', #4 for 4-flavour scheme (no matching of b-quarks)
            'JetMatching:nJetMax = 1', #number of partons in born matrix element for highest multiplicity
            'JetMatching:doShowerKt = off', #off for MLM matching, turn on for shower-kT matching
						'Check:epTolErr = 0.0003',
            '9100000:new  = MED MED 3 0 0 X_MMed_X 0 0 0 99999',
            '9100022:new  = DM  DM  2 0 0 X_MFM_X  0 0 0 99999',
            '9100022:mayDecay = off'
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CUEP8M1Settings',
                                    'processParameters',
                                    )
    )
)