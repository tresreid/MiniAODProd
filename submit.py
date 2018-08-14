#!/usr/bin/env python

import os, sys
import getpass

'''Usage: ./submit.py <LHE/gridpack filename> [njobs]
'''

def buildSubmit(infile, workpath, mode, uid, user):
    '''A series of actions to prepare submit dir'''

#    stageOutPiece = '''
#for h in `ls *GENSIM_cfg*`; do
#    cmd="xrdcp -vf file:///$PWD/$h root://cmseos.fnal.gov/$remoteDIR/ggF/$h"
#    echo $cmd && eval $cmd
#done
#remoteDIR="/store/user/%s/standaloneComp"
#for f in `ls *AOD*.root`; do
#    cmd="xrdcp -vf file:///$PWD/$f root://cmseos.fnal.gov/$remoteDIR/$f"
#    echo $cmd && eval $cmd
#done''' % user
    stageOutPiece = '''
remoteDIR="/store/user/%s/standaloneComp/iDM/redone"
for f in `ls *AOD*.root`; do
    cmd="xrdcp -vf file:///$PWD/$f root://cmseos.fnal.gov/$remoteDIR/$f"
    echo $cmd && eval $cmd
done
done
echo "all Done"
''' % user

    os.makedirs(workpath+'/submit/conf')
    os.system('cp conf/* %s/submit/conf/' % workpath)
    try:
        if mode=='lhe':
            os.makedirs(workpath+'/submit/mgLHEs')
            os.system('cp mgLHEs/%s %s/submit/mgLHEs' % (infile, workpath))
            os.system('cp runOffLHE.sh %s/submit' % workpath)
            with open('%s/submit/runOffLHE.sh' % workpath, 'a') as f:
                f.write(stageOutPiece)
        else:
            os.makedirs(workpath+'/submit/gridpacks')
            os.system('cp gridpacks/%s %s/submit/gridpacks' % (infile, workpath))
            os.system('cp replaceLHELifetime.py %s/submit' % workpath)
            os.system('cp runOffGridpack.sh %s/submit' % workpath)
            with open('%s/submit/runOffGridpack.sh' % workpath, 'a') as f:
                f.write(stageOutPiece)
    except:
        print "%s probably not exist." % infile
        cmd = ['ls -lrth '+s for s in ('.', 'mgLHES', 'gridpacks')]
        for c in cmd:
            print cmd
            os.system(cmd)
        raise


    os.system('cp /tmp/x509up_u%d %s/x509up' % (uid, workpath))
    print "Tarring up submit..."
    os.chdir(workpath)
    os.system('tar -chzf submit.tgz submit')
    os.chdir('..')



def buildExec(infile, workpath, mode):
    '''Given the workpath, write a exec.sh in it, to be used by condor'''

    execF = '''
#!/bin/bash

export X509_USER_PROXY=${PWD}/x509up
export HOME=${PWD}

tar xvaf submit.tgz
cd submit
sh %s.sh %s
cd ${HOME}
rm -r submit/

exit 0'''
    with open(workpath + '/exec.sh', 'w') as f:
        if mode == 'lhe':
            f.write(execF % ('runOffLHE', infile))
        else:
            # Deduce decay length [mm] from gridpack name..
            # e.g. SIDMmumu_Mps-200_MZp-1p2_ctau-0p1.tar.xz
            ctau = '0'
            if 'iDM' in infile and False:
                nameTags = infile.split('.')[0].split('_')
                for t in nameTags:
                    if 'ctau' in t:
                        ctau = t.split('-', 1)[-1]
                        ctau = str( float(ctau.replace('p','.'))*10 )
            f.write(execF % ('runOffGridpack', infile+' '+ctau))



def buildCondor(process, workpath, logpath, uid, user, njobs=1):
    '''build the condor file, return the abs path'''

    condorF = '''
universe = vanilla
executable = {0}/exec.sh
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = {0}/submit.tgz,{0}/x509up
transfer_output_files = ""
input = /dev/null
output = {1}/$(Cluster)_$(Process).out
error = {1}/$(Cluster)_$(Process).err
log = {1}/$(Cluster)_$(Process).log
rank = Mips
request_memory = 8000
arguments = $(Process)
use_x509userproxy = True
x509userproxy = /tmp/x509up_u{2}
#on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)
notify_user = {3}@FNAL.GOV
+AccountingGroup = "analysis.{3}"
+AcctGroup = "analysis"
+ProjectName = "DarkMatterSimulation"
queue {4}'''.format(workpath, logpath, uid, user, njobs)
    condorFN = 'condor_%s.jdl' % process

    with open(logpath + '/' + condorFN, 'w') as jdlfile:
        jdlfile.write(condorF)

    return os.path.join(logpath, condorFN)


if __name__ == "__main__":

    inf = sys.argv[1]
    Mode = 'lhe' if 'lhe' in inf else 'gridpack'
    Process = inf.split('.')[0]

    Njobs = 1 if len(sys.argv) == 2 else sys.argv[2]

    Logpath = os.getcwd() + '/Logs'
    if not os.path.isdir(Logpath): os.mkdir(Logpath)
    Workpath = os.getcwd() + '/submit_' + Process
    if os.path.isdir(Workpath): os.system('rm -rf %s' % Workpath)
    os.mkdir(Workpath)
    Uid = os.getuid()
    User = getpass.getuser()

    buildSubmit(infile=inf, workpath=Workpath, mode=Mode, uid=Uid, user=User)
    buildExec(infile=inf, workpath=Workpath, mode=Mode)
    theCondor = buildCondor(process=Process, workpath=Workpath,
            logpath=Logpath, uid=Uid, user=User, njobs=Njobs)
    os.system('condor_submit %s' % theCondor)
