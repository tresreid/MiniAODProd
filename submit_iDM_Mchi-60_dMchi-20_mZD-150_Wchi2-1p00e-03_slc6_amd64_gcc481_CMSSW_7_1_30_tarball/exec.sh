
#!/bin/bash

export X509_USER_PROXY=${PWD}/x509up
export HOME=${PWD}

tar xvaf submit.tgz
cd submit
sh runOffGridpack3.sh iDM_Mchi-60_dMchi-20_mZD-150_Wchi2-1p00e-03_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz 0
cd ${HOME}
rm -r submit/

exit 0