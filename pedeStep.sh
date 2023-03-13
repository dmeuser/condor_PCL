#!/bin/bash
# script which takes care of running the pede step for the HG PCL studies
# takes run number and boolean for HG running as command line arguments
RunNo="$1"
HG_bool=$2

# source CMSSW (has to be changed for different user)
cmsswDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2022/CMSSW_12_4_9/src
cd $cmsswDir
eval `scramv1 runtime -sh`

# set path to CAF (has to be changed for different user)
cafPath=/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2022/output

# check if running HG or LG
if [ $HG_bool -eq 1 ]
then
    # go to correct output directory
    echo "Running with HG"
    outputDir=$cafPath/HG_run$RunNo
    cd $outputDir
    
    # put all input files name for pede step to txt file
    ls PromptCalibProdSiPixelAliHG_*.root | sed 's/Prompt/file:Prompt/g' > AlcaFiles.txt
    
    # run pede step with HGprocess modifier, adapted thresholds using alignment from previous run (stored in payloads_HG.db)
    cmsDriver.py pedeStep --data --conditions 124X_dataRun3_Prompt_v4 --scenario pp -s ALCAHARVEST:SiPixelAliHG --filein filelist:AlcaFiles.txt --customise_commands "process.GlobalTag.toGet=cms.VPSet(cms.PSet(record=cms.string('TrackerAlignmentRcd'),tag=cms.string('SiPixelAliHG_pcl'),connect=cms.string('sqlite_file:/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2022/output/payloads_HG.db')),cms.PSet(record=cms.string('TrackerAlignmentExtendedErrorRcd'),tag=cms.string('TrackerAlignmentExtendedErrors_collisions22_v2_multiIOV'),connect=cms.string('frontier://FrontierPrep/CMS_CONDITIONS')),cms.PSet(record=cms.string('AlignPCLThresholdsHGRcd'),tag=cms.string('PCLThresholds_express_v0'),connect=cms.string('sqlite_file:$cmsswDir/CondFormats/PCLConfig/test/mythresholds_HG.db')),cms.PSet(record=cms.string('SiPixelTemplateDBObjectRcd'),tag=cms.string('SiPixelTemplateDBObject_phase1_38T_2022_forAlignment_v2')),cms.PSet(record=cms.string('SiPixel2DTemplateDBObjectRcd'),tag=cms.string('SiPixel2DTemplateDBObject_phase1_38T_2022_forAlignment_v2'),label=cms.untracked.string('numerator')))"
    
    # import new alignment to db file
    conddb_import -f sqlite:promptCalibConditions.db -c sqlite:../payloads_HG.db -i SiPixelAliHG_pcl || echo "no Update produced"
else
    # go to correct output directory
    echo "Running with nominal granularity"
    outputDir=$cafPath/run$RunNo
    cd $outputDir
    
    # put all input files name for pede step to txt file
    ls PromptCalibProdSiPixelAli_*.root | sed 's/Prompt/file:Prompt/g' > AlcaFiles.txt
    
    # run pede step using alignment from previous run (stored in payloads_HG.db)
    cmsDriver.py pedeStep --data --conditions 124X_dataRun3_Express_v5 --scenario pp -s ALCAHARVEST:SiPixelAli --filein filelist:AlcaFiles.txt --customise_commands "process.GlobalTag.toGet = cms.VPSet(cms.PSet(record = cms.string('AlignPCLThresholdsHGRcd'),tag = cms.string('PCLThresholds_express_v0'),connect = cms.string('sqlite_file:$cmsswDir/CondFormats/PCLConfig/test/mythresholds.db')),cms.PSet(record = cms.string('TrackerAlignmentRcd'),tag = cms.string('SiPixelAli_pcl'),connect = cms.string('sqlite_file:$cafPath/payloads.db')))"
    
    # import new alignment to db file
    conddb_import -f sqlite:promptCalibConditions.db -c sqlite:../payloads.db -i SiPixelAli_pcl || echo "no Update produced"
fi



