#!/bin/bash 
RunNo="$1"
HG_bool=$2
Start_Lumi=$3

cmsswDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/hgPCL/CMSSW_11_1_0_pre3/src
cd $cmsswDir
eval `scramv1 runtime -sh`

export HOME=/afs/cern.ch/user/d/dmeuser

baseDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2018
cd $baseDir

if [ $HG_bool -eq 1 ]
then
    echo "Running with HG"
    
    outputDir=/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output/HG_run$RunNo/lumi_$Start_Lumi
    mkdir $outputDir -p
    
    runDir=/afs/cern.ch/work/d/dmeuser/alignment/PCL/condor_PCL_2018/run_directories/HG_run$RunNo/lumi_$Start_Lumi
    cd $runDir
    
    cmsRun milleStep_ALCA_HG.py
else
    echo "Running with nominal granularity"
    
    outputDir=/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output/run$RunNo/lumi_$Start_Lumi
    mkdir $outputDir -p
    
    runDir=/afs/cern.ch/work/d/dmeuser/alignment/PCL/condor_PCL_2018/run_directories/run$RunNo/lumi_$Start_Lumi
    cd $runDir
    
    cmsRun milleStep_ALCA.py
fi

mv $runDir/* $outputDir

cd $outputDir
mv PromptCalibProdSiPixelAli.root PromptCalibProdSiPixelAli_$Start_Lumi.root
cp PromptCalibProdSiPixelAli_$Start_Lumi.root ../

cd $baseDir

rm -r $runDir
