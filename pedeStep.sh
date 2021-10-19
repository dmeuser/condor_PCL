#!/bin/bash
# script which takes care of running the pede step for the HG PCL studies
# takes run number and boolean for HG running as command line arguments
RunNo="$1"
HG_bool=$2

# source CMSSW (has to be changed for different user)
cmsswDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/hgPCL/CMSSW_11_1_0_pre3/src
cd $cmsswDir
eval `scramv1 runtime -sh`

# set path to CAF (has to be changed for different user)
cafPath=/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output

# check if running HG or LG
if [ $HG_bool -eq 1 ]
then
    # go to correct output directory
    echo "Running with HG"
    outputDir=$cafPath/HG_run$RunNo
    cd $outputDir
    
    # put all input files name for pede step to txt file
    ls PromptCalibProdSiPixelAli_*.root | sed 's/Prompt/file:Prompt/g' > AlcaFiles.txt
    
    # run pede step with HGprocess modifier, adapted thresholds using alignment from previous run (stored in payloads_HG.db)
    cmsDriver.py pedeStep --data --conditions 106X_dataRun3_Express_v2 --scenario pp --era Run2_2018 -s ALCAHARVEST:SiPixelAli --filein filelist:AlcaFiles.txt --procModifiers high_granularity_pcl --customise_commands "process.GlobalTag.toGet = cms.VPSet(cms.PSet(record = cms.string('AlignPCLThresholdsRcd'),tag = cms.string('PCLThresholds_express_v0'),connect = cms.string('sqlite_file:$cmsswDir/CondFormats/PCLConfig/test/mythresholds_test.db')),cms.PSet(record = cms.string('TrackerAlignmentRcd'),tag = cms.string('SiPixelAli_pcl'),connect = cms.string('sqlite_file:$cafPath/payloads_HG.db')))"
    
    # import new alignment to db file
    conddb_import -f sqlite:promptCalibConditions.db -c sqlite:../payloads_HG.db -i SiPixelAli_pcl || echo "no Update produced"
else
    # go to correct output directory
    echo "Running with nominal granularity"
    outputDir=$cafPath/run$RunNo
    cd $outputDir
    
    # put all input files name for pede step to txt file
    ls PromptCalibProdSiPixelAli_*.root | sed 's/Prompt/file:Prompt/g' > AlcaFiles.txt
    
    # run pede step using alignment from previous run (stored in payloads_HG.db)
    cmsDriver.py pedeStep --data --conditions 106X_dataRun3_Express_v2 --scenario pp --era Run2_2018 -s ALCAHARVEST:SiPixelAli --filein filelist:AlcaFiles.txt --customise_commands "process.GlobalTag.toGet = cms.VPSet(cms.PSet(record = cms.string('AlignPCLThresholdsRcd'),tag = cms.string('PCLThresholds_express_v0'),connect = cms.string('sqlite_file:$cmsswDir/CondFormats/PCLConfig/test/mythresholds.db')),cms.PSet(record = cms.string('TrackerAlignmentRcd'),tag = cms.string('SiPixelAli_pcl'),connect = cms.string('sqlite_file:$cafPath/payloads.db')))"
    
    # import new alignment to db file
    conddb_import -f sqlite:promptCalibConditions.db -c sqlite:../payloads.db -i SiPixelAli_pcl || echo "no Update produced"
fi



