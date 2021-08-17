#!/bin/bash 
RunNo="$1"
HG_bool=$2

cmsswDir=/afs/cern.ch/user/d/dmeuser/alignment/PCL/hgPCL/CMSSW_11_1_0_pre3/src
cd $cmsswDir
eval `scramv1 runtime -sh`

if [ $HG_bool -eq 1 ]
then
    echo "Running with HG"
    outputDir=/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output/HG_run$RunNo
    cd $outputDir
    
    ls PromptCalibProdSiPixelAli_*.root | sed 's/Prompt/file:Prompt/g' > AlcaFiles.txt

    cmsDriver.py pedeStep --data --conditions 106X_dataRun3_Express_v2 --scenario pp --era Run2_2018 -s ALCAHARVEST:SiPixelAli --filein filelist:AlcaFiles.txt --procModifiers high_granularity_pcl --customise_commands "process.GlobalTag.toGet = cms.VPSet(cms.PSet(record = cms.string('AlignPCLThresholdsRcd'),tag = cms.string('PCLThresholds_express_v0'),connect = cms.string('sqlite_file:/afs/cern.ch/user/d/dmeuser/alignment/PCL/hgPCL/CMSSW_11_1_0_pre3/src/CondFormats/PCLConfig/test/mythresholds_HG.db')),cms.PSet(record = cms.string('TrackerAlignmentRcd'),tag = cms.string('SiPixelAli_pcl'),connect = cms.string('sqlite_file:/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output/payloads_HG.db')))"
    
    # ~cmsDriver.py pedeStep --data --conditions 106X_dataRun3_Express_v2 --scenario pp --era Run2_2018 -s ALCAHARVEST:SiPixelAli --filein filelist:AlcaFiles.txt --procModifiers high_granularity_pcl --customise_commands "process.GlobalTag.toGet = cms.VPSet(cms.PSet(record = cms.string('AlignPCLThresholdsRcd'),tag = cms.string('PCLThresholds_express_v0'),connect = cms.string('sqlite_file:/afs/cern.ch/user/d/dmeuser/alignment/PCL/hgPCL/CMSSW_11_1_0_pre3/src/CondFormats/PCLConfig/test/mythresholds_HG.db')))"
    
    conddb_import -f sqlite:promptCalibConditions.db -c sqlite:../payloads_HG.db -i SiPixelAli_pcl
else
    echo "Running with nominal granularity"
    outputDir=/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output/run$RunNo
    cd $outputDir
    
    ls PromptCalibProdSiPixelAli_*.root | sed 's/Prompt/file:Prompt/g' > AlcaFiles.txt
    
    cmsDriver.py pedeStep --data --conditions 106X_dataRun3_Express_v2 --scenario pp --era Run2_2018 -s ALCAHARVEST:SiPixelAli --filein filelist:AlcaFiles.txt --customise_commands "process.GlobalTag.toGet = cms.VPSet(cms.PSet(record = cms.string('AlignPCLThresholdsRcd'),tag = cms.string('PCLThresholds_express_v0'),connect = cms.string('sqlite_file:/afs/cern.ch/user/d/dmeuser/alignment/PCL/hgPCL/CMSSW_11_1_0_pre3/src/CondFormats/PCLConfig/test/mythresholds.db')),cms.PSet(record = cms.string('TrackerAlignmentRcd'),tag = cms.string('SiPixelAli_pcl'),connect = cms.string('sqlite_file:/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output/payloads.db')))"
    
    # ~cmsDriver.py pedeStep --data --conditions 106X_dataRun3_Express_v2 --scenario pp --era Run2_2018 -s ALCAHARVEST:SiPixelAli --filein filelist:AlcaFiles.txt --customise_commands "process.GlobalTag.toGet = cms.VPSet(cms.PSet(record = cms.string('AlignPCLThresholdsRcd'),tag = cms.string('PCLThresholds_express_v0'),connect = cms.string('sqlite_file:/afs/cern.ch/user/d/dmeuser/alignment/PCL/hgPCL/CMSSW_11_1_0_pre3/src/CondFormats/PCLConfig/test/mythresholds.db')))"
    
    conddb_import -f sqlite:promptCalibConditions.db -c sqlite:../payloads.db -i SiPixelAli_pcl || echo "no Update produced"
fi



