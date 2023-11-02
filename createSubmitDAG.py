import subprocess
import os
import shutil
import pickle
import fileinput
import urllib
import json
import collections


# method to merge two dictionaries (mostly used when adding lowPU runs into nominal range)
def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

# method to retrieve file list for given run in the form of {lumiNo: "file1, file2"}
def getFileList_run(run,Zmumu_bool=False):
    run=int(run)
    #  ~if run<355094 or run>357815:    # check which run era has to be used
        #  ~print "Dataset to run "+run+" not defined"
    #  ~elif run<=355769:
        #  ~output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2022B-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    #  ~elif run<=357482:
        #  ~output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2022C-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    #  ~elif run<=357815:
        #  ~output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2022D-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    if run<366403 or run>370580:    # check which run era has to be used 
        print "Dataset to run "+run+" not defined"
    elif run<=367079:
        if Zmumu_bool:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/Muon0/Run2023B-TkAlZMuMu-PromptReco-v1/ALCARECO run={}'".format(run)], shell=True)
        else:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/HLTPhysics/Run2023B-TkAlMinBias-PromptReco-v1/ALCARECO run={}'".format(run)], shell=True)
    elif run<=367619:
        if Zmumu_bool:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/Muon0/Run2023C-TkAlZMuMu-PromptReco-v1/ALCARECO run={}'".format(run)], shell=True)
        else:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/HLTPhysics/Run2023C-TkAlMinBias-PromptReco-v1/ALCARECO run={}'".format(run)], shell=True)
    elif run<=367840:
        if Zmumu_bool:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/Muon0/Run2023C-TkAlZMuMu-PromptReco-v2/ALCARECO run={}'".format(run)], shell=True)
        else:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/HLTPhysics/Run2023C-TkAlMinBias-PromptReco-v2/ALCARECO run={}'".format(run)], shell=True)
    elif run<=369802:
        if Zmumu_bool:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/Muon0/Run2023C-TkAlZMuMu-PromptReco-v4/ALCARECO run={}'".format(run)], shell=True)
        else:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/HLTPhysics/Run2023C-TkAlMinBias-PromptReco-v4/ALCARECO run={}'".format(run)], shell=True)
    elif run<=370580:
        if Zmumu_bool:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/Muon0/Run2023D-TkAlZMuMu-PromptReco-v1/ALCARECO run={}'".format(run)], shell=True)
        else:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/HLTPhysics/Run2023D-TkAlMinBias-PromptReco-v1/ALCARECO run={}'".format(run)], shell=True)
    elif run<=371227:
        if Zmumu_bool:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/Muon0/Run2023D-TkAlZMuMu-PromptReco-v2/ALCARECO run={}'".format(run)], shell=True)
        else:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/HLTPhysics/Run2023D-TkAlMinBias-PromptReco-v2/ALCARECO run={}'".format(run)], shell=True)
    fileDict={}
    for line in output.split("\n"):     #create dictionary to save filenames per lumi (each line corresponds to one file)
        if len(line.split("["))==2 :
            lumi = line.split("[")[1].split("]")[0].split(",")      # get list of lumiNo from das output
            fileName = line.split("[")[0]
            for i in range(len(lumi)):
                if int(lumi[i])<20: continue    # first 20 lumi section should not be used for study
                fileDict[int(lumi[i])]=fileName
    with open("./testDict.pkl","wb") as f:      # write dictionary to pkl               
        pickle.dump(fileDict, f, pickle.HIGHEST_PROTOCOL)
    return fileDict
    
# method do import starting geometry from global tag
def getSGfromTag(tag,run,HG_bool,Zmumu_bool):
    print "Import starting geomtry from tag "+tag
    
    if not os.path.exists(outputPath):  #create output path
        try:
            os.makedirs(outputPath)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
    if HG_bool:
        if Zmumu_bool:
            outputFile="payloads_HG_Zmumu.db"
            outputName="SiPixelAliHGCombined_pcl"
        else:
            outputFile="payloads_HG.db"
            outputName="SiPixelAliHG_pcl"
    else :
        outputFile="payloads.db"
        outputName="SiPixelAli_pcl"
    output=subprocess.check_output(["conddb_import -f frontier://FrontierProd/CMS_CONDITIONS -i {0} -c sqlite:{1} -b {2} -e {2} -t {3}".format(tag,outputFile,run-1,outputName)], shell=True)
    shutil.move(outputFile,outputPath+"/"+outputFile)
    
# method to create the log folder, returns path to log folder
def createLogFolder(run,lumi,HG_bool,Zmumu_bool):
    if HG_bool:
        if Zmumu_bool:
            dirname=logPath+"/HG_Zmumu_run"+str(run)+"/lumi_"+str(lumi)
            dirnameZmumu=logPath+"/HG_Zmumu_run"+str(run)+"/lumi_Zmumu_"+str(lumi)    #require additional folder for Zmumu data (not only minBias)
        else:
            dirname=logPath+"/HG_run"+str(run)+"/lumi_"+str(lumi)
    else :
        dirname=logPath+"/run"+str(run)+"/lumi_"+str(lumi)
        
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
    if Zmumu_bool:
        if not os.path.exists(dirnameZmumu):
            try:
                os.makedirs(dirnameZmumu)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
    
    return dirname

# method to create the run folder, returns path to run folder
def createRunFolder(run,lumi,HG_bool,Zmumu_bool):
    if HG_bool:
        if Zmumu_bool:
            dirname=workPath+"/HG_Zmumu_run"+str(run)+"/lumi_"+str(lumi)
            dirnameZmumu=workPath+"/HG_Zmumu_run"+str(run)+"/lumi_Zmumu_"+str(lumi) #require additional folder for Zmumu data (not only minBias)
        else:
            dirname=workPath+"/HG_run"+str(run)+"/lumi_"+str(lumi)
    else :
        dirname=workPath+"/run"+str(run)+"/lumi_"+str(lumi)
        
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
    if Zmumu_bool:
        if not os.path.exists(dirnameZmumu):
            try:
                os.makedirs(dirnameZmumu)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
    
    return dirname

# method to clean output folder folder(useful in case job are failing)
def cleanOutputFolder(run,HG_bool,Zmumu_bool,complete):
    if HG_bool:
        if Zmumu_bool:
            dirname=outputPath+"/HG_Zmumu_run"+str(run)
            logname=logPath+"/HG_Zmumu_run"+str(run)
        else:
            dirname=outputPath+"/HG_run"+str(run)
            logname=logPath+"/HG_run"+str(run)
    else :
        dirname=outputPath+"/run"+str(run)
        logname=logPath+"/run"+str(run)
    if os.path.exists(dirname):
        if complete:
            shutil.rmtree(dirname)
        else:
            if os.path.exists(dirname+"/promptCalibConditions.db"):
                os.remove(dirname+"/promptCalibConditions.db")
            if os.path.exists(dirname+"/treeFile.root"):
                os.remove(dirname+"/treeFile.root")
            

# method which return file list for a given starting lumi and given lumis per job
def getFileList_job(fileDict,lumi,LumisPerJob):
    fileList=""
    for i in range(0,LumisPerJob):      # loop over number of lumis per job
        if lumi+i in fileDict.keys():   # current lumi given bei start lumi + loop lumi
            if fileDict[lumi+i] not in fileList:    # only add file if not already in list
                fileList+="'"+fileDict[lumi+i]+"',\n"
    return fileList
    
# method which write mille config starting from template and replacing file list and start/stop lumi
def writeMilleConfig(run,HG_bool,Zmumu_bool,lumi,LumisPerJob,fileList,dirRun):
    if HG_bool:
        if Zmumu_bool:
            fileName="milleStep_ALCA_HG_Zmumu.py"
        else:
            fileName="milleStep_ALCA_HG.py"
    else:
        fileName="milleStep_ALCA.py"
    
    f = open(basePath+"/templates/"+fileName,'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace("'file:milleStep_RECO.root'",fileList)       # set file list
    newdata = newdata.replace("run:startLumi-run:endLumi",str(run)+":"+str(lumi)+"-"+str(run)+":"+str(lumi+LumisPerJob-1))      # set start and stop lumi
    newdata = newdata.replace("<outputPath>",outputPath)      # set output path to find payload file

    f = open(dirRun+"/"+fileName,'w')   # write config to run directory
    f.write(newdata)
    f.close()
    
# method to write condor submit script for mille job log folder(needs argument used for milleStep.sh)
def writeMilleSubmit(run,HG_bool,Zmumu_bool,lumi,fileList,dirname):
    with open(dirname+"/submit_mille.sub","w") as f:
        f.write("""
Universe   = vanilla
Executable = milleStep.sh
Arguments  = {0} {1} {4} {5} {3} {6}
Log        = {2}/log_mille.log
Output     = {2}/out_mille.out
Error      = {2}/error_mille.error
x509userproxy = $ENV(X509_USER_PROXY)
+JobFlavour = "microcentury"
+AccountingGroup = "group_u_CMS.CAF.ALCA"
Queue
""".format(run,HG_bool,dirname,lumi,Zmumu_bool,int(dirname.find("lumi_Zmumu")>0),projectName))
    return dirname+"/submit_mille.sub"

# method to write condor submit script for pede job to log folder(needs argument used for pedeStep.sh)
def writePedeSubmit(run,HG_bool,Zmumu_bool,dirname):
    with open(dirname+"/submit_pede.sub","w") as f:
        f.write("""
Universe   = vanilla
Executable = pedeStep.sh
Arguments  = {0} {1} {3} {4}
Log        = {2}/log_pede.log
Output     = {2}/out_pede.out
Error      = {2}/error_pede.error
+JobFlavour = "workday"
+AccountingGroup = "group_u_CMS.CAF.ALCA"
Queue
""".format(run,HG_bool,dirname,Zmumu_bool,projectName))
    return dirname+"/submit_pede.sub"

# method to write dag submit for single run
def writeDag(dirname):
    dirList=os.listdir(dirname)
    dag=""
    for dir in dirList:
        if "lumi" in dir:
            dag+="JOB mille_"+dir+" "+dirname+"/"+dir+"/submit_mille.sub\n"     # declare mille jobs
    dag+= "JOB pedeStep "+dirname+"/submit_pede.sub\n"      # declare pede job
    dag+="PARENT"
    for dir in dirList:
        if "lumi" in dir:
            dag+=" mille_"+dir
    dag+=" CHILD pedeStep"      # set pede job as child of mille jobs
    
    with open(dirname+"/dag_submit.dag","w") as f:
        f.write(dag)
    return "dag_submit.dag"

# method to write dag submit for several runs (running iteratively) Takes log folder as input, which has submits for mille and pede inside
def writeDag_Trend(dirname):
    dirList=sorted(os.listdir(dirname))
    dag=""
    firstRun=True       # check if run is first run of submit
    pedeStep_before=""
    for dir_run in dirList:
        if "run" not in dir_run: continue
        for dir_lumi in os.listdir(dirname+"/"+dir_run):
            if "lumi" in dir_lumi:
                dag+="JOB mille_"+dir_run+"_"+dir_lumi+" "+dirname+"/"+dir_run+"/"+dir_lumi+"/submit_mille.sub\n"
        dag+= "JOB pedeStep_"+dir_run+" "+dirname+"/"+dir_run+"/submit_pede.sub\n"
        if firstRun==False:     # if runs is not first run, the corresponding jobs have to wait for the previous run to finish
            dag+=pedeStep_before
            for dir_lumi in os.listdir(dirname+"/"+dir_run):
                if "lumi" in dir_lumi:
                    dag+=" mille_"+dir_run+"_"+dir_lumi
        dag+="\nPARENT"
        for dir_lumi in os.listdir(dirname+"/"+dir_run):
            if "lumi" in dir_lumi:
                dag+=" mille_"+dir_run+"_"+dir_lumi
        dag+=" CHILD pedeStep_"+dir_run+"\n\n"
        pedeStep_before="PARENT pedeStep_"+dir_run+" CHILD"
        firstRun=False
    
    with open(dirname+"/dag_submit.dag","w") as f:
        f.write(dag)
    return "dag_submit.dag"
    


def submitRun(run,HG_bool,Zmumu_bool,LumisMax,LumisPerJob,StartLumi,SingleRun=True):
    if(Zmumu_bool and HG_bool==False):
        print("Zmumu data can be only included in HG setup!!")
        raise
    
    print "Preparing run",run
    fileDict=getFileList_run(run)
    if Zmumu_bool: fileDict_Zmumu=getFileList_run(run,Zmumu_bool)
    if len(fileDict)>LumisMax:       # use only runs with at least 100 lumi sections
        
        LumisMax=min(max(fileDict.keys()),LumisMax)     # set maximal number of lumis to set value or maximum available lumis
        
        cleanOutputFolder(run,HG_bool,Zmumu_bool,True)     # clean output folder in case some run before fails
        
        for lumi in range(StartLumi,LumisMax+StartLumi,LumisPerJob):    # create run and log folder for each mille job and write config and submit
            dirname_log=createLogFolder(run,lumi,HG_bool,Zmumu_bool)
            dirname_run=createRunFolder(run,lumi,HG_bool,Zmumu_bool)
            fileList=getFileList_job(fileDict,lumi,LumisPerJob)
            if Zmumu_bool: fileList_Zmumu=getFileList_job(fileDict_Zmumu,lumi,LumisPerJob)     #additional file list for Zmumu samples
            
            writeMilleConfig(run,HG_bool,Zmumu_bool,lumi,LumisPerJob,fileList,dirname_run)
            if Zmumu_bool: writeMilleConfig(run,HG_bool,Zmumu_bool,lumi,LumisPerJob,fileList_Zmumu,dirname_run.replace("lumi_","lumi_Zmumu_"))
            
            writeMilleSubmit(run,HG_bool,Zmumu_bool,lumi,fileList,dirname_log)
            if Zmumu_bool: writeMilleSubmit(run,HG_bool,Zmumu_bool,lumi,fileList,dirname_log.replace("lumi_","lumi_Zmumu_"))
    
        dirname_totalRun=os.path.dirname(dirname_log)
        writePedeSubmit(run,HG_bool,Zmumu_bool,dirname_totalRun)       # write pede submit (not config needed since cmsDriver.py is used in pedeStep.sh)
        if SingleRun:   # single runs are currently submitted right away
            dugSubmit=writeDag(dirname_totalRun)
            print "Submitting run",run
            subprocess.call(["condor_submit_dag", "-f", dirname_totalRun+"/"+dugSubmit])
        return True
    else:
        print "Not enough LumiSections"
        return False

def submitRunTotal(run,HG_bool,LumisPerJob):
    print "Submitting run",run
    fileDict=getFileList_run(run)    
    
    submittedLumis = []; 
    
    if bool(fileDict):
        for lumi in fileDict:
            if lumi in submittedLumis:
                continue        
            cleanOutputFolder(run,HG_bool,True)     # clean output folder in case some run before fails
            
            dirname_log=createLogFolder(run,lumi,HG_bool)
            dirname_run=createRunFolder(run,lumi,HG_bool)
            fileList=getFileList_job(fileDict,lumi,LumisPerJob)
            
            for nextLumi in range(lumi,lumi+LumisPerJob):
                if nextLumi in fileDict:
                    submittedLumis.append(nextLumi)
            
            writeMilleConfig(run,HG_bool,lumi,LumisPerJob,fileList,dirname_run)
            writeMilleSubmit(run,HG_bool,lumi,fileList,dirname_log)
        
        dirname_totalRun=os.path.dirname(dirname_log)
        writePedeSubmit(run,HG_bool,dirname_totalRun)       # write pede submit (not config needed since cmsDriver.py is used in pedeStep.sh)
    else:
        print "Lumi list empty"

if __name__ == "__main__":
        
    ################################# Config Part ###############################################################
    
    # define workspace, base directory and output directory (has to be changed for different user)
    # $projectName ??
    workPath ="/afs/cern.ch/cms/CAF/CMSALCA/ALCA_TRACKERALIGN/data/commonValidation/alignmentObjects/phnattla/2023/PCL/condor_PCL/run_directories"
    basePath = "/afs/cern.ch/cms/CAF/CMSALCA/ALCA_TRACKERALIGN/data/commonValidation/alignmentObjects/phnattla/2023/PCL/condor_PCL"
    logPath = "/afs/cern.ch/cms/CAF/CMSALCA/ALCA_TRACKERALIGN/data/commonValidation/alignmentObjects/phnattla/2023/PCL/condor_PCL/logs"
    outputPath = "/eos/cms/store/group/alca_trackeralign/phnattla/condor_PCL_2023/output"

    # set json
    url = "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions23/DCSOnly_JSONS/Collisions23_13p6TeV_eraBCD_366403_370790_DCSOnly_TkPx.json"
    
    # define project name
    projectName = "testZmumu"
    
    # define tag for import of SG
    tag = "TrackerAlignment_PCL_byRun_v2_express"
    
    # set alignment options
    useHG = True
    useZmumu = True
    
    # define the number of lumi sections to be used per run
    #  ~numberOfLS=100
    numberOfLS=10
    
    # define run range (different eras are usually run in different dag jobs)
    startingRun=370300
    stoppingRun=370310
    
    ################################# End Config Part ###############################################################
    
    # append project name to paths
    workPath = workPath+"/"+projectName
    logPath = logPath+"/"+projectName
    outputPath = outputPath+"/"+projectName
    
    # get starting geometry from tag
    getSGfromTag(tag,startingRun,useHG,useZmumu)
    
    # clean log/run folder
    if os.path.exists(logPath): shutil.rmtree(logPath)
    if os.path.exists(workPath): shutil.rmtree(workPath)

    # open url
    response = urllib.urlopen(url)

    # read json (and merge with lowPU)
    data = json.loads(response.read())

    # get ordered dictionary with {run:"lumiRange1, lumiRange2"}
    data = collections.OrderedDict(sorted(data.items()))

    # set helper variables
    longestRange=0
    totalLS=0
    startLongestRange=0

    # loop over each run in the selected range
    for run in data:
        if int(run)>=startingRun and int(run)<=stoppingRun:
            for lsRange in data[run]:   # loop to find the longest range of lumis and store its length
                if lsRange[1]-lsRange[0]>longestRange: 
                    longestRange=lsRange[1]-lsRange[0]
                    startLongestRange=lsRange[0]
                totalLS+=lsRange[1]-lsRange[0]
            if longestRange>numberOfLS:    # use run only if there is a lumi range with more an numberOfLS LS
                if startLongestRange<20:startLongestRange=20    # do not use the first 20 Lumis (match PCL config)
                submitRun(run,int(useHG),int(useZmumu),numberOfLS,5,startLongestRange,False)   #prepare run
            longestRange=0      # set variables to zero for next run
            totalLS=0
            
    # Submit all runs with full LS (second argument of submitRunTotal defines LG or HG)
    '''
    for run in data:
        if int(run)>=startingRun and int(run)<=stoppingRun:
            #  ~submitRunTotal(run,1,5) #HG
            #  ~submitRunTotal(run,0,5) #LG
    '''
    
    # write dag submits for trends
    writeDag_Trend(logPath)

    #load t0 setting: module load lxbatch/tzero
