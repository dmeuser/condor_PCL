#!/bin/bash
set -e
# script which takes care of running the pede step for the HG PCL studies
# takes run number and boolean for HG running as command line arguments
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh 

RunNo="$1"
HG_bool=$2
Zmumu_bool=$3
projectName=$4
weightZmumu=$5

# source CMSSW (has to be changed for different user)
cmsswDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2024/CMSSW_14_0_4/src
cd $cmsswDir
eval `scramv1 runtime -sh`

# set path to CAF (has to be changed for different user)
cafPath=/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2024/output/$projectName

# check if running HG or LG
if [ $HG_bool -eq 1 ]
then
    # check if running with Zmumu
    if [ $Zmumu_bool -eq 1 ]
    then
        # go to correct output directory
        echo "Running with HG including Zmumu"
        outputDir=$cafPath/HG_Zmumu_run$RunNo
        cd $outputDir
        
        # put all input files name for pede step to txt file
        for filename in $outputDir/PromptCalibProdSiPixelAliHGComb_*.root
        do
           echo "file:$filename" >> AlcaFiles.txt
        done
        
        # run pede step with HGprocess modifier, adapted thresholds using alignment from previous run (stored in payloads_HG_Zmumu.db)
        
        # Version for testing different Zmumu weights
        # ~cmsDriver.py pedeStep --data --conditions 140X_dataRun3_Express_v2 --scenario pp -s ALCAHARVEST:SiPixelAliHGCombined --filein filelist:AlcaFiles.txt --customise_commands "process.GlobalTag.toGet=cms.VPSet(cms.PSet(record=cms.string('TrackerAlignmentRcd'),tag=cms.string('SiPixelAliHGCombined_pcl'),connect=cms.string('sqlite_file:$cafPath/payloads_HG_Zmumu.db')),cms.PSet(record=cms.string('AlignPCLThresholdsHGRcd'),tag=cms.string('PCLThresholds_express_v0'),connect=cms.string('sqlite_file:$cmsswDir/CondFormats/PCLConfig/test/mythresholds_HG.db')));process.SiPixelAliPedeAlignmentProducerHGCombined.algoConfig.mergeBinaryFiles = ['pedeBinaryHGMinBias%04d.dat','pedeBinaryHGDiMuon%04d.dat -- $weightZmumu']"
        
        cmsDriver.py pedeStep --data --conditions 140X_dataRun3_Express_v3 --scenario pp -s ALCAHARVEST:SiPixelAliHGCombined --filein filelist:AlcaFiles.txt --customise_commands "process.GlobalTag.toGet=cms.VPSet(cms.PSet(record=cms.string('TrackerAlignmentRcd'),tag=cms.string('SiPixelAliHGCombined_pcl'),connect=cms.string('sqlite_file:$cafPath/payloads_HG_Zmumu.db')),cms.PSet(record=cms.string('AlignPCLThresholdsHGRcd'),tag=cms.string('PCLThresholds_express_v0'),connect=cms.string('sqlite_file:$cmsswDir/CondFormats/PCLConfig/test/mythresholds_HG.db')))"
        
        # import new alignment to db file
        conddb_import -f sqlite:promptCalibConditions.db -c sqlite:../payloads_HG_Zmumu.db -i SiPixelAliHGCombined_pcl || echo "no Update produced"
    else
        # go to correct output directory
        echo "Running with HG"
        outputDir=$cafPath/HG_run$RunNo
        cd $outputDir
        
        # put all input files name for pede step to txt file
        for filename in $outputDir/PromptCalibProdSiPixelAliHG_*.root
        do
           echo "file:$filename" >> AlcaFiles.txt
        done
        
        # run pede step with HGprocess modifier, adapted thresholds using alignment from previous run (stored in payloads_HG.db)
        cmsDriver.py pedeStep --data --conditions 140X_dataRun3_Express_v3 --scenario pp -s ALCAHARVEST:SiPixelAliHG --filein filelist:AlcaFiles.txt --customise_commands "process.GlobalTag.toGet=cms.VPSet(cms.PSet(record=cms.string('TrackerAlignmentRcd'),tag=cms.string('SiPixelAliHG_pcl'),connect=cms.string('sqlite_file:$cafPath/payloads_HG.db')),cms.PSet(record=cms.string('AlignPCLThresholdsHGRcd'),tag=cms.string('PCLThresholds_express_v0'),connect=cms.string('sqlite_file:$cmsswDir/CondFormats/PCLConfig/test/mythresholds_HG.db')))"
        
        # import new alignment to db file
        conddb_import -f sqlite:promptCalibConditions.db -c sqlite:../payloads_HG.db -i SiPixelAliHG_pcl || echo "no Update produced"
    fi
else
    # go to correct output directory
    echo "Running with nominal granularity"
    outputDir=$cafPath/run$RunNo
    cd $outputDir
    
    # put all input files name for pede step to txt file
    for filename in $outputDir/PromptCalibProdSiPixelAli*.root
    do
       echo "file:$filename" >> AlcaFiles.txt
    done
    
    # run pede step using alignment from previous run (stored in payloads_HG.db)
    cmsDriver.py pedeStep --data --conditions 140X_dataRun3_Express_v3 --scenario pp -s ALCAHARVEST:SiPixelAli --filein filelist:AlcaFiles.txt --customise_commands "process.GlobalTag.toGet = cms.VPSet(cms.PSet(record = cms.string('AlignPCLThresholdsHGRcd'),tag = cms.string('PCLThresholds_express_v0'),connect = cms.string('sqlite_file:$cmsswDir/CondFormats/PCLConfig/test/mythresholds_HG.db')),cms.PSet(record = cms.string('TrackerAlignmentRcd'),tag = cms.string('SiPixelAli_pcl'),connect = cms.string('sqlite_file:$cafPath/payloads.db')))"
    
    # import new alignment to db file
    conddb_import -f sqlite:promptCalibConditions.db -c sqlite:../payloads.db -i SiPixelAli_pcl || echo "no Update produced"
fi



