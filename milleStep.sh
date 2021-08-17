#!/bin/bash 
# script which takes care of running the mille step for the HG PCL studies
# takes run number, boolean for HG running and start_lumi(only for proper folder/file names) as command line arguments
RunNo="$1"
HG_bool=$2
Start_Lumi=$3

# source CMSSW (has to be changed for different user)
cmsswDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/hgPCL/CMSSW_11_1_0_pre3/src
cd $cmsswDir
eval `scramv1 runtime -sh`

# set home directory (has to be changed for different user)
export HOME=/afs/cern.ch/user/d/dmeuser

# set base directory (has to be changed for different user)
baseDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2018
cd $baseDir

# set path to CAF (has to be changed for different user)
cafPath=/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output

# set path to working space (has to be changed for different user)
workPath=/afs/cern.ch/work/d/dmeuser/alignment/PCL/condor_PCL_2018/run_directories

# check if running HG or LG
if [ $HG_bool -eq 1 ]
then
    echo "Running with HG"
    
    # prepare output directory
    outputDir=$cafPath/HG_run$RunNo/lumi_$Start_Lumi
    mkdir $outputDir -p
    
    # define running directory (should already exist due to running createSubmitDAG.py)
    runDir=$workPath/HG_run$RunNo/lumi_$Start_Lumi
    cd $runDir
    
    # run mille step in run directory (py script already produced in createSubmitDAG.py)
    cmsRun milleStep_ALCA_HG.py
else
    echo "Running with nominal granularity"
    
    # prepare output directory
    outputDir=$cafPath/run$RunNo/lumi_$Start_Lumi
    mkdir $outputDir -p
    
    # define running directory (should already exist due to running createSubmitDAG.py)
    runDir=$workPaths/run$RunNo/lumi_$Start_Lumi
    cd $runDir
    
    # run mille step in run directory (py script already produced in createSubmitDAG.py)
    cmsRun milleStep_ALCA.py
fi

# move everything from running directory to output directory (mille step is not working on eos/caf)
mv $runDir/* $outputDir

# rename and move mille step output to be able to use it in the pede step
cd $outputDir
mv PromptCalibProdSiPixelAli.root PromptCalibProdSiPixelAli_$Start_Lumi.root
cp PromptCalibProdSiPixelAli_$Start_Lumi.root ../

# go back to base directory
cd $baseDir

# clean run directory
rm -r $runDir
