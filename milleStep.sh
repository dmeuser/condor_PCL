#!/bin/bash 
# script which takes care of running the mille step for the HG PCL studies
# takes run number, boolean for HG running and start_lumi(only for proper folder/file names) as command line arguments
RunNo="$1"
HG_bool=$2
Zmumu_bool=$3   #running a campaign with Zmumu (can be also job with minBias input)
Zmumu_input_bool=$4     #this mille step runs on Zmumu input
Start_Lumi=$5
projectName=$6

# source CMSSW (has to be changed for different user)
cmsswDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2023/CMSSW_13_3_0_pre4/src
cd $cmsswDir
eval `scramv1 runtime -sh`

# set home directory (has to be changed for different user)
export HOME=/afs/cern.ch/user/d/dmeuser

# set base directory (has to be changed for different user)
baseDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2023/condor_PCL
cd $baseDir

# set path to CAF (has to be changed for different user and created manually)
cafPath=/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2023/output/$projectName

# set path to working space (has to be changed for different user and created manually)
workPath=/afs/cern.ch/work/d/dmeuser/alignment/PCL/condor_PCL_2023/run_directories/$projectName

# check if running HG or LG
if [ $HG_bool -eq 1 ]
then
    #check if running with Zmumu
    if [ $Zmumu_bool -eq 1 ]
    then
        echo "Running with HG including Zmumu"
        #check if Zmumu input
        if [ $Zmumu_input_bool -eq 1 ]
        then 
            folderName=lumi_Zmumu_$Start_Lumi
        else
            folderName=lumi_$Start_Lumi
        fi
        # prepare output directory
        outputDir=$cafPath/HG_Zmumu_run$RunNo/$folderName
        mkdir $outputDir -p
        
        # define running directory (should already exist due to running createSubmitDAG.py)
        runDir=$workPath/HG_Zmumu_run$RunNo/$folderName
        cd $runDir
        
        # run mille step in run directory (py script already produced in createSubmitDAG.py)
        cmsRun milleStep_ALCA_HG_Zmumu.py
    else
        echo "Running with HG"
        # prepare output directory
        outputDir=$cafPath/HG_run$RunNo/lumi_$Start_Lumi
        mkdir $outputDir -p
        
        # define running directory (should already exist due to running createSubmitDAG.py)
        runDir=$workPath/HG_run$RunNo/lumi_$Start_Lumi
        cd $runDir
        
        # run mille step in run directory (py script already produced in createSubmitDAG.py)
        cmsRun milleStep_ALCA_HG.py
    fi
else
    echo "Running with nominal granularity"
    
    # prepare output directory
    outputDir=$cafPath/run$RunNo/lumi_$Start_Lumi
    mkdir $outputDir -p
    
    # define running directory (should already exist due to running createSubmitDAG.py)
    runDir=$workPath/run$RunNo/lumi_$Start_Lumi
    cd $runDir
    
    # run mille step in run directory (py script already produced in createSubmitDAG.py)
    cmsRun milleStep_ALCA.py
fi

# move everything from running directory to output directory (mille step is not working on eos/caf)
mv $runDir/* $outputDir

# rename and move mille step output to be able to use it in the pede step
cd $outputDir
if [ $Zmumu_bool -eq 1 ]
then
    if [ $Zmumu_input_bool -eq 1 ]
    then
        mv PromptCalibProdSiPixelAliHGComb.root PromptCalibProdSiPixelAliHGComb_Zmumu_$Start_Lumi.root
        cp PromptCalibProdSiPixelAliHGComb_Zmumu_$Start_Lumi.root ../
    else
        mv PromptCalibProdSiPixelAliHGComb.root PromptCalibProdSiPixelAliHGComb_minBias_$Start_Lumi.root
        cp PromptCalibProdSiPixelAliHGComb_minBias_$Start_Lumi.root ../
    fi
else
    mv PromptCalibProdSiPixelAli.root PromptCalibProdSiPixelAli_$Start_Lumi.root
    cp PromptCalibProdSiPixelAli_$Start_Lumi.root ../
    mv PromptCalibProdSiPixelAliHG.root PromptCalibProdSiPixelAliHG_$Start_Lumi.root
    cp PromptCalibProdSiPixelAliHG_$Start_Lumi.root ../
fi

# go back to base directory
cd $baseDir

# clean run directory
rm -r $runDir
