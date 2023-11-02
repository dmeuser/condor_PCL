# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: milleStepZmumu -s ALCA:PromptCalibProdSiPixelAliHGComb --conditions 130X_dataRun3_Prompt_v2 --datatier ALCARECO --eventcontent ALCARECO --triggerResultsProcess RECO --customise_commands process.MessageLogger.cerr.FwkReport.reportEvery = 1000 --processName=ReALCA -n -1 --no_exec
import FWCore.ParameterSet.Config as cms



process = cms.Process('ReALCA')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.AlCaRecoStreams_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:milleStep_RECO.root'),
    secondaryFileNames = cms.untracked.vstring(),
    lumisToProcess = cms.untracked.VLuminosityBlockRange("run:startLumi-run:endLumi"),
)

process.options = cms.untracked.PSet(
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    TryToContinue = cms.untracked.vstring(),
    accelerators = cms.untracked.vstring('*'),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(1)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    holdsReferencesToDeleteEarly = cms.untracked.VPSet(),
    makeTriggerResults = cms.obsolete.untracked.bool,
    modulesToCallForTryToContinue = cms.untracked.vstring(),
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(1),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('milleStepZmumu nevts:-1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition


# Additional output definition
process.ALCARECOStreamPromptCalibProdSiPixelAliHGComb = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring(
            'pathALCARECOPromptCalibProdSiPixelAliHG',
            'pathALCARECOPromptCalibProdSiPixelAliHGDiMu'
        )
    ),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('ALCARECO'),
        filterName = cms.untracked.string('PromptCalibProdSiPixelAliHGComb')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    fileName = cms.untracked.string('PromptCalibProdSiPixelAliHGComb.root'),
    outputCommands = cms.untracked.vstring(
        'drop *',
        'keep *_SiPixelAliMillePedeFileConverterHGDimuon_*_*',
        'keep *_SiPixelAliMillePedeFileConverterHG_*_*'
    )
)

# Other statements
process.ALCARECOEventContent.outputCommands.extend(process.OutALCARECOPromptCalibProdSiPixelAliHGComb_noDrop.outputCommands)
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '130X_dataRun3_Prompt_v2', '')
# Use different Starting Geometry and different Thresholds
process.GlobalTag.toGet = cms.VPSet(
    cms.PSet(
        record = cms.string('TrackerAlignmentRcd'),
        tag = cms.string('SiPixelAliHGCombined_pcl'),
        connect = cms.string('sqlite_file:<outputPath>/payloads_HG_Zmumu.db')),
    cms.PSet(
        record = cms.string('AlignPCLThresholdsHGRcd'),
        tag = cms.string('PCLThresholds_express_v0'),
        connect = cms.string('sqlite_file:/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2023/CMSSW_13_3_0_pre4/src/CondFormats/PCLConfig/test/mythresholds_HG.db')),
        )

# Path and EndPath definitions
process.endjob_step = cms.EndPath(process.endOfProcess)
process.ALCARECOStreamPromptCalibProdSiPixelAliHGCombOutPath = cms.EndPath(process.ALCARECOStreamPromptCalibProdSiPixelAliHGComb)

# Schedule definition
process.schedule = cms.Schedule(process.pathALCARECOPromptCalibProdSiPixelAliHG,process.pathALCARECOPromptCalibProdSiPixelAliHGDiMu,process.endjob_step,process.ALCARECOStreamPromptCalibProdSiPixelAliHGCombOutPath)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)



# Customisation from command line

process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.ALCARECOTkAlMinBiasFilterForSiPixelAliHG.throw = False
process.ALCARECOTkAlZMuMuFilterForSiPixelAli.throw = False
# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
