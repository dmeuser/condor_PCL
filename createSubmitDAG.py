import subprocess
import os
import shutil
import pickle
import fileinput
import urllib.request
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
        #  ~print("Dataset to run "+run+" not defined")
    #  ~elif run<=355769:
        #  ~output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2022B-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    #  ~elif run<=357482:
        #  ~output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2022C-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    #  ~elif run<=357815:
        #  ~output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2022D-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    if run<378981 or run>379618:    # check which run era has to be used 
        print("Dataset to run ",run," not defined")
    elif run<=379391:
        if Zmumu_bool:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2024B-TkAlZMuMu-Express-v1/ALCARECO run={}'".format(run)], shell=True)
        else:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2024B-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    elif run<=379618:
        if Zmumu_bool:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2024C-TkAlZMuMu-Express-v1/ALCARECO run={}'".format(run)], shell=True)
        else:
            output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2024C-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    fileDict={}
    for line in output.split(b"\n"):     #create dictionary to save filenames per lumi (each line corresponds to one file)
        line = line.decode()  # Convert bytes to string
        if len(line.split("["))==2 :
            lumi = line.split("[")[1].split("]")[0].split(",")      # get list of lumiNo from das output
            fileName = line.split("[")[0]
            for i in range(len(lumi)):
                if int(lumi[i])<20: continue    # first 20 lumi section should not be used for study
                if int(lumi[i]) in fileDict:
                    fileDict[int(lumi[i])]+="','"+fileName.strip()
                else:
                    fileDict[int(lumi[i])]=fileName.strip()
    with open("./testDict.pkl","wb") as f:      # write dictionary to pkl               
        pickle.dump(fileDict, f, pickle.HIGHEST_PROTOCOL)
    return fileDict
    
# method do import starting geometry from global tag
def getSGfromTag(tag,run,HG_bool,Zmumu_bool,fromPrevios=True):
    print("Import starting geomtry from tag "+tag)
    
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
    if fromPrevios:
        output=subprocess.check_output(["conddb_import -f frontier://FrontierProd/CMS_CONDITIONS -i {0} -c sqlite:{1} -b {2} -e {2} -t {3}".format(tag,outputFile,run-1,outputName)], shell=True)
    else:
        output=subprocess.check_output(["conddb_import -f frontier://FrontierProd/CMS_CONDITIONS -i {0} -c sqlite:{1} -b {2} -e {2} -t {3}".format(tag,outputFile,run,outputName)], shell=True)
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
Proxy_path = $ENV(X509_USER_PROXY)
+JobFlavour = "microcentury"
+AccountingGroup = "group_u_CMS.CAF.ALCA"
Queue
""".format(run,HG_bool,dirname,lumi,Zmumu_bool,int(dirname.find("lumi_Zmumu")>0),projectName))
    return dirname+"/submit_mille.sub"

# method to write condor submit script for pede job to log folder(needs argument used for pedeStep.sh)
def writePedeSubmit(run,HG_bool,Zmumu_bool,dirname,weightZmumu):
    with open(dirname+"/submit_pede.sub","w") as f:
        f.write("""
Universe   = vanilla
Executable = pedeStep.sh
Arguments  = {0} {1} {3} {4} {5}
Log        = {2}/log_pede.log
Output     = {2}/out_pede.out
Error      = {2}/error_pede.error
+JobFlavour = "workday"
+AccountingGroup = "group_u_CMS.CAF.ALCA"
Queue
""".format(run,HG_bool,dirname,Zmumu_bool,projectName,weightZmumu))
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

def submitRunTotal(run,HG_bool,Zmumu_bool,LumisMax,LumisPerJob,weightZmumu=1):
    print("Preparing run",run)
    fileDict=getFileList_run(run)
    if Zmumu_bool: fileDict_Zmumu=getFileList_run(run,Zmumu_bool)
    
    
    submittedLumis = [];
    
    if bool(fileDict):
        for lumi in fileDict:
            if lumi in submittedLumis:      #skip lumis already submitted
                continue        
            cleanOutputFolder(run,HG_bool,Zmumu_bool,True)     # clean output folder in case some run before fails
            
            dirname_log=createLogFolder(run,lumi,HG_bool,Zmumu_bool)
            dirname_run=createRunFolder(run,lumi,HG_bool,Zmumu_bool)
            fileList=getFileList_job(fileDict,lumi,LumisPerJob)
            if Zmumu_bool: fileList_Zmumu=getFileList_job(fileDict_Zmumu,lumi,LumisPerJob)     #additional file list for Zmumu samples
            
            for nextLumi in range(lumi,lumi+LumisPerJob):
                if nextLumi in fileDict:
                    submittedLumis.append(nextLumi)
            
            writeMilleConfig(run,HG_bool,Zmumu_bool,lumi,LumisPerJob,fileList,dirname_run)
            if Zmumu_bool: writeMilleConfig(run,HG_bool,Zmumu_bool,lumi,LumisPerJob,fileList_Zmumu,dirname_run.replace("lumi_","lumi_Zmumu_"))
            
            writeMilleSubmit(run,HG_bool,Zmumu_bool,lumi,fileList,dirname_log)
            if Zmumu_bool: writeMilleSubmit(run,HG_bool,Zmumu_bool,lumi,fileList,dirname_log.replace("lumi_","lumi_Zmumu_"))
            
            if len(submittedLumis)>=LumisMax: break
        
        dirname_totalRun=os.path.dirname(dirname_log)
        writePedeSubmit(run,HG_bool,Zmumu_bool,dirname_totalRun,weightZmumu)       # write pede submit (not config needed since cmsDriver.py is used in pedeStep.sh)
    else:
        print("Lumi list empty")

if __name__ == "__main__":
        
    ################################# Config Part ###############################################################
    
    # define workspace, base directory and output directory (has to be changed for different user)
    #  ~workPath = "/afs/cern.ch/work/d/dmeuser/alignment/PCL/condor_PCL_2024/run_directories"
    workPath = "/eos/cms/store/caf/user/dmeuser/PCL/workspace/condor_PCL_2024/run_directories"
    basePath = "/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2024/condor_PCL"
    logPath = "/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2024/condor_PCL/logs"
    outputPath = "/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2024/output"

    # set json
    url = "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions24/DCSOnly_JSONS/dailyDCSOnlyJSON/Collisions24_13p6TeV_378981_379618_DCSOnly_TkPx.json"
    
    # define project name
    projectName = "SG_beforeCycle_starting_379238_379530_noZMuMu"
    
    # define tag for import of SG
    #  ~tag = "TrackerAlignment_PCL_byRun_v2_express"
    tag = "TrackerAlignment_collisions24_v0"
    
    # set alignment options
    useHG = True
    #  ~useZmumu = True
    useZmumu = False
    
    # set weight for Zmumu
    weightZmumu = 10
    
    # define the number of lumi sections to be used per run
    #  ~numberOfLS=100
    #  ~numberOfLS=20
    numberOfLS=99999
    
    # define run range (different eras are usually run in different dag jobs)
    startingRun=379238
    stoppingRun=379530
    
    ################################# End Config Part ###############################################################
    
    # append project name to paths
    workPath = workPath+"/"+projectName
    logPath = logPath+"/"+projectName
    outputPath = outputPath+"/"+projectName
    
    # get starting geometry from tag
    #  ~getSGfromTag(tag,startingRun,useHG,useZmumu)
    getSGfromTag(tag,startingRun,useHG,useZmumu,False)
    
    # clean log/run folder
    if os.path.exists(logPath): shutil.rmtree(logPath)
    if os.path.exists(workPath): shutil.rmtree(workPath)

    # Open URL
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    # get ordered dictionary with {run:"lumiRange1, lumiRange2"}
    data = collections.OrderedDict(sorted(data.items()))

    # set helper variables
    longestRange=0
    totalLS=0
    startLongestRange=0

    # prepare each run in the selected range
    for run in data:
        if int(run)>=startingRun and int(run)<=stoppingRun:
            submitRunTotal(run,int(useHG),int(useZmumu),numberOfLS,5,weightZmumu)
            
    
    # write dag submits for trends
    writeDag_Trend(logPath)

    #load t0 setting: module load lxbatch/tzero
