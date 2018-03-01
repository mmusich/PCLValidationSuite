#!/bin/sh
clean_up () {
    ls -l
    rm -fr tree*.root
    rm -fr *.db
    rm -fr pede*
    rm -fr mille*
    ls -l
    exit
}

#LSF signals according to http://batch.web.cern.ch/batch/lsf-return-codes.html
trap clean_up HUP INT TERM SEGV USR2 XCPU XFSZ IO

cd ${CMSSW_BASE}/src
echo $CMSSW_BASE
eval `scramv1 runtime -sh`
#cmsRun step8_ALCAHARVEST.py &
cd -
cmsRun step3_ALCAOUTPUT_ALCA.py &
#./memoryGF.sh 1 cmsRun RSS.out
./memoryCheck.sh 1 cmsRun RSS_tar.out
#tail -f RSS.out
clean_up
