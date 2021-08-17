import subprocess
import os
import shutil
import pickle
import fileinput
import urllib
import json
import collections

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def getFileList_run(run):
    run=int(run)
    if run<317080 or run>325175:
        print "Dataset to run "+run+" not defined"
    elif run<=319311:
        output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2018B-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    elif run<=320393:
        output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2018C-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    elif run<=325175:
        output=subprocess.check_output(["dasgoclient -query='lumi,file dataset=/StreamExpress/Run2018D-TkAlMinBias-Express-v1/ALCARECO run={}'".format(run)], shell=True)
    fileDict={}
    for line in output.split("\n"):
        if len(line.split("["))==2 :
            runs = line.split("[")[1].split("]")[0].split(",")
            fileName = line.split("[")[0]
            for i in range(len(runs)):
                if int(runs[i])<20: continue
                fileDict[int(runs[i])]=fileName
    with open("./testDict.pkl","wb") as f:            
        pickle.dump(fileDict, f, pickle.HIGHEST_PROTOCOL)
    return fileDict
    

def createLogFolder(run,lumi,HG_bool):
    if HG_bool:
        dirname="/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2018/logs/HG_run"+str(run)+"/lumi_"+str(lumi)
    else :
        dirname="/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2018/logs_LG/run"+str(run)+"/lumi_"+str(lumi)
        
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    return dirname

def createRunFolder(run,lumi,HG_bool):
    if HG_bool:
        dirname="/afs/cern.ch/work/d/dmeuser/alignment/PCL/condor_PCL_2018/run_directories/HG_run"+str(run)+"/lumi_"+str(lumi)
    else :
        dirname="/afs/cern.ch/work/d/dmeuser/alignment/PCL/condor_PCL_2018/run_directories/run"+str(run)+"/lumi_"+str(lumi)
        
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    return dirname

def createRunFolder_pede(run,HG_bool):
    if HG_bool:
        dirname="/afs/cern.ch/work/d/dmeuser/alignment/PCL/condor_PCL_2018/run_directories/HG_run"+str(run)
    else :
        dirname="/afs/cern.ch/work/d/dmeuser/alignment/PCL/condor_PCL_2018/run_directories/run"+str(run)
        
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    return dirname
    
def cleanOutputFolder(run,HG_bool,complete):
    if HG_bool:
        dirname="/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output/HG_run"+str(run)
    else :
        dirname="/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2018/output/run"+str(run)
    if os.path.exists(dirname):
        if complete:
            shutil.rmtree(dirname)
        else:
            if os.path.exists(dirname+"/promptCalibConditions.db"):
                os.remove(dirname+"/promptCalibConditions.db")
            if os.path.exists(dirname+"/treeFile.root"):
                os.remove(dirname+"/treeFile.root")
            
    

def getFileList_job(fileDict,lumi,LumisPerJob):
    fileList=""
    for i in range(0,LumisPerJob):
        if lumi+i in fileDict.keys():
            if fileDict[lumi+i] not in fileList:
                fileList+="'"+fileDict[lumi+i]+"',\n"
    return fileList
    

def writeMilleConfig(run,HG_bool,lumi,LumisPerJob,fileList,dirRun):
    if HG_bool:
        fileName="milleStep_ALCA_HG.py"
    else:
        fileName="milleStep_ALCA.py"
    
    f = open("/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2018/templates/"+fileName,'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace("'file:milleStep_RECO.root'",fileList)
    newdata = newdata.replace("run:startLumi-run:endLumi",str(run)+":"+str(lumi)+"-"+str(run)+":"+str(lumi+LumisPerJob-1))

    f = open(dirRun+"/"+fileName,'w')
    f.write(newdata)
    f.close()
    

def writeMilleSubmit(run,HG_bool,lumi,fileList,dirname):
    with open(dirname+"/submit_mille.sub","w") as f:
        f.write("""
Universe   = vanilla
Executable = milleStep.sh
Arguments  = {0} {1} {3}
Log        = {2}/log_mille.log
Output     = {2}/out_mille.out
Error      = {2}/error_mille.error
x509userproxy = $ENV(X509_USER_PROXY)
+JobFlavour = "microcentury"
+AccountingGroup = "group_u_CMS.CAF.ALCA"
Queue
""".format(run,HG_bool,dirname,lumi))
    return dirname+"/submit_mille.sub"


def writePedeSubmit(run,HG_bool,dirname):
    with open(dirname+"/submit_pede.sub","w") as f:
        f.write("""
Universe   = vanilla
Executable = pedeStep.sh
Arguments  = {0} {1}
Log        = {2}/log_pede.log
Output     = {2}/out_pede.out
Error      = {2}/error_pede.error
+JobFlavour = "microcentury"
+AccountingGroup = "group_u_CMS.CAF.ALCA"
Queue
""".format(run,HG_bool,dirname))
    return dirname+"/submit_pede.sub"


def writeDag(dirname):
    dirList=os.listdir(dirname)
    dag=""
    for dir in dirList:
        if "lumi" in dir:
            dag+="JOB mille_"+dir+" "+dirname+"/"+dir+"/submit_mille.sub\n"
    dag+= "JOB pedeStep "+dirname+"/submit_pede.sub\n"
    dag+="PARENT"
    for dir in dirList:
        if "lumi" in dir:
            dag+=" mille_"+dir
    dag+=" CHILD pedeStep"
    
    with open(dirname+"/dag_submit.dag","w") as f:
        f.write(dag)
    return "dag_submit.dag"

def writeDag_Trend(dirname):
    dirList=sorted(os.listdir(dirname))
    dag=""
    firstRun=True
    pedeStep_before=""
    for dir_run in dirList:
        if "run" not in dir_run: continue
        for dir_lumi in os.listdir(dirname+"/"+dir_run):
            if "lumi" in dir_lumi:
                dag+="JOB mille_"+dir_run+"_"+dir_lumi+" "+dirname+"/"+dir_run+"/"+dir_lumi+"/submit_mille.sub\n"
        dag+= "JOB pedeStep_"+dir_run+" "+dirname+"/"+dir_run+"/submit_pede.sub\n"
        if firstRun==False:
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
    


def submitRun(run,HG_bool,LumisMax,LumisPerJob,StartLumi,SingleRun=True):
    print "Submitting run",run
    fileDict=getFileList_run(run)
    if len(fileDict)>100:
        
        LumisMax=min(max(fileDict.keys()),LumisMax)
        
        cleanOutputFolder(run,HG_bool,True)
        
        for lumi in range(StartLumi,LumisMax+StartLumi,LumisPerJob):
            dirname_log=createLogFolder(run,lumi,HG_bool)
            dirname_run=createRunFolder(run,lumi,HG_bool)
            fileList=getFileList_job(fileDict,lumi,LumisPerJob)
            
            writeMilleConfig(run,HG_bool,lumi,LumisPerJob,fileList,dirname_run)
            
            writeMilleSubmit(run,HG_bool,lumi,fileList,dirname_log)
    
        dirname_totalRun=os.path.dirname(dirname_log)
        writePedeSubmit(run,HG_bool,dirname_totalRun)
        if SingleRun:
            dugSubmit=writeDag(dirname_totalRun)
            subprocess.call(["condor_submit_dag", "-f", dirname_totalRun+"/"+dugSubmit])
        return True
    else:
        print "Not enough LumiSections"
        return False
    
def submitLumi_Mille(run,HG_bool,lumi,LumisPerJob):
    fileDict=getFileList_run(run)
    
    dirname_log=createLogFolder(run,lumi,HG_bool)
    dirname_run=createRunFolder(run,lumi,HG_bool)
    
    fileList=getFileList_job(fileDict,lumi,LumisPerJob)
    
    writeMilleConfig(run,HG_bool,lumi,fileList,dirname_run)
    milleSubmit=writeMilleSubmit(run,HG_bool,lumi,fileList,dirname_log)
    
    subprocess.call(["condor_submit", milleSubmit])
    
def submit_Pede(run,HG_bool):
    
    cleanOutputFolder(run,HG_bool,False)
    dirname_totalRun=createRunFolder_pede(run,HG_bool)
    pedeSubmit=writePedeSubmit(run,HG_bool,dirname_totalRun)
    
    subprocess.call(["condor_submit", pedeSubmit])

print "!!!!!!Check if correct SG is loaded in the beginning and if study can be iterative (payloads already in output folder)!!!!!!!!"


#################### 2018C 100LS #########################

#  ~submitRun(319347,1,100,5,50)
#  ~submitRun(319349,1,100,5,50)
#  ~submitRun(319449,1,100,5,50)
#  ~submitRun(319450,1,100,5,50)
#  ~submitRun(319503,1,100,5,50)

#  ~submitRun(319526,1,100,5,50)
#  ~submitRun(319528,1,100,5,50)
#  ~submitRun(319625,1,100,5,50)
#  ~submitRun(319656,1,100,5,50)
#  ~submitRun(319657,1,100,5,50)

#  ~submitRun(319347,0,100,5,50)
#  ~submitRun(319349,0,100,5,50)
#  ~submitRun(319449,0,100,5,50)
#  ~submitRun(319450,0,100,5,50)
#  ~submitRun(319503,0,100,5,50)

#  ~submitRun(319526,0,100,5,50)
#  ~submitRun(319528,0,100,5,50)
#  ~submitRun(319625,0,100,5,50)
#  ~submitRun(319656,0,100,5,50)
#  ~submitRun(319657,0,100,5,50)

#  ~submitLumi_Mille(319625,1,80,5)

#  ~submit_Pede(319625,1)

#########################2018B long range with template update#################################
url = "https://test-eos-cms-service-dqm.web.cern.ch/test-eos-cms-service-dqm/CAF/certification/Collisions18/13TeV/DCSOnly/json_DCSONLY.txt"
url_lowPU = "https://test-eos-cms-service-dqm.web.cern.ch/test-eos-cms-service-dqm/CAF/certification/Collisions18/13TeV/PromptReco/Cert_318939-319488_13TeV_PromptReco_SpecialCollisions18_JSON_LOWPU.txt"

response = urllib.urlopen(url)
response_lowPU = urllib.urlopen(url_lowPU)

data = json.loads(response.read())
data_lowPU = json.loads(response_lowPU.read())
data = merge_two_dicts(data,data_lowPU)

data = collections.OrderedDict(sorted(data.items()))

#Run2018B
startingRun=317087
stoppingRun=317090
#  ~stoppingRun=318877
#Run2018C
#  ~startingRun=319337
#  ~stoppingRun=320065
#Run2018D partly
#  ~startingRun=320500
#  ~stoppingRun=321177

#Across Run2018B and Run2018C (used for lowPU included study)
#  ~startingRun=317626
#  ~stoppingRun=319699
longestRange=0
totalLS=0
startLongestRange=0

numberOfLS=100

for run in data:
    if int(run)>=startingRun and int(run)<stoppingRun:
        for lsRange in data[run]:
            if lsRange[1]-lsRange[0]>longestRange: 
                longestRange=lsRange[1]-lsRange[0]
                startLongestRange=lsRange[0]
            totalLS+=lsRange[1]-lsRange[0]
        if longestRange>100:
            if startLongestRange<20:startLongestRange=20 
            #  ~submitRun(run,1,numberOfLS,5,startLongestRange,True)
            #  ~submitRun(run,0,numberOfLS,5,startLongestRange,True)
            #  ~submitRun(run,0,numberOfLS,5,startLongestRange,False)
            submitRun(run,1,numberOfLS,5,startLongestRange,False)
        longestRange=0
        totalLS=0


writeDag_Trend("/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2018/logs")
#  ~writeDag_Trend("/afs/cern.ch/user/d/dmeuser/alignment/PCL/condor_PCL_2018/logs_LG")

#Getting payload for UL: conddb_import -f frontier://FrontierProd/CMS_CONDITIONS -i TrackerAlignment_v28_offline -c sqlite:file.db -b 317626 -e 317626 -t SiPixelAli_pcl
#Getting payload for PR: conddb_import -f frontier://FrontierProd/CMS_CONDITIONS -i TrackerAlignment_PCL_byRun_v2_express -c sqlite:file.db -b 317080 -e 317080 -t SiPixelAli_pcl

#load t0 setting: module load lxbatch/tzero

