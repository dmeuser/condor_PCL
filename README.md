### Purpose

This code can be used to perform studies regarding the high granularity (HG) PCL alignment. The main function is to setup the config and condor submission script for running the PCL alignment with the nominal (low granularity) and the new configuration (high granularity). In addition, including Zmumu data in the HG PCL alignment can be tested. Once setup the jobs can be used in a dagman job to run the alignment for multiple runs iteratively, which in a way mimics the setup used during data taking.

### Installation/Requirements
Run the following lines to setup CMSSW_13_3_0_pre4 and add the package containing the threshold config:
```
cmsrel CMSSW_13_3_0_pre4
cd CMSSW_13_3_0_pre4/src/
cmsenv
git cms-init
git cms-merge-topic mmusich:devel_ZMuMuInHGPCL_from-CMSSW_13_3_0_pre4
git cms-addpkg CondFormats/PCLConfig
scram b -j7
cmsenv
```
To setup the code of this repository first of all clone it using:
```
git clone git@github.com:dmeuser/condor_PCL.git
```
To run the alignment payloads containing the PCL alignment thresholds are needed. In this setup the payload is required to be stored in `$CMSSW_BASE/src/CondFormats/PCLConfig/test/mythresholds_HG.db`. To get the payload produce the payload by running the following steps (config is taken from current CMSSW version, but can also be adapted in `$CMSSW_BASE/src/CondFormats/PCLConfig/python/ThresholdsHG_cff.py` to use individual thresholds)
```
cd $CMSSW_BASE/src/CondFormats/PCLConfig/test
cmsRun AlignPCLThresholdsWriter_cfg.py
```
There are some files in the code where the paths have to be changed when a different user is running the scripts. These parts are indicated by comments and are present in the following files:
```
milleStep.sh
pedeStep.sh
createSubmitDAG.py
```
In addition also the path to the db file for the milleStep has to be adapted in `templates/milleStep_ALCA<PCLtype>.py`

### Structure
Using the code on lxplus there are two constraints, which led to the fact that the code is currently basically running in three different places.
* The nominal home directory `/afs/cern.ch/user/` does not offer enough storage for the code to be executed since large root files are produced while running the code. This is why the run directories are located at `/afs/cern.ch/work/`.

* Since `/afs/cern.ch/work/` also has only quite limited storage, the output after running the milleStep is copied to `/eos/cms/store/caf/user/`. Running the milleStep directly in `/eos/cms/store/caf/user/` does not work (at least at the time of developing the code).

Thus, in the files mentioned above the path to the home directory, the run directory and the output directory have to be defined.

### Code
* `createSubmitDAG.py`: Main script which prepares all necessary configs and submit scripts for the studies. Run ranges, HG/LG option etc. are defined in the lower part of the script. The script can only be executed with active proxy since the `dasgoclient` is used to find the proper input files for a given run. The scripts runs roughly the following steps
    * Dictionary of `{run:[lumiRange1,lumiRange2]}` is created using an input json
    * Log and run folders and the condor submits are prepared for each mille job (e.g. 20 mille jobs when using 100LS and 5LS per job) and for the final pede job (repeated for each run of the study)
    * `milleStep_ALCA<PCLtype>.py` is setup based on the templates in `templates/` by defining the input files as well as the lumi
    * The config for the dagman job is produced looping over the mille and pede submitting script prepared before


* `milleStep.sh`: Bash script which is executed for each milleJob. It takes care of running `milleStep_ALCA<PCLtype>.py`, which was setup by `createSubmitDAG.py` for each milleJob. At the end of each milleJob the output is copied to CAF and the run directory is cleaned.

* `pedeStep.sh`: Bash script which is executed for each pedeJob. First the outputs of the previously finished milleJobs are collected and stored in `AlcaFiles.txt`. Then the `cmsDriver.py` is used to execute the pedeStep based on the input list, the thresholds stored in `$cmsswDir/CondFormats/PCLConfig/test/mythresholds(_HG).db` and the previously generated alignment found in `payloads<PCLtype>.db`.
 
* `templates/`: Templates for the milleStep (one for LG, one for HG and one for HG+Zmumu). The inputs are set by `createSubmitDAG.py`. The path to `payloads<PCLtype>.db` has to be set when changing the user.
 
* `watch_condor_q`: Simple bash scripts which check the job status every 30 second.
 
* `combinedHists/`: Code to plot histograms for the movement, error and significance for a given study. Histograms for different settings can be compared with `compareDiffHits.py`. `makeLatex.py` can be used to prepare latex beamer slides for a given set of histograms.


### Example of running 
In the following an example of running the PCL alignment for a given run range iteratively (the alignment for each run is based on the result of the previous run due to loading `payloads<PCLtype>.db`) is shown. 
Before producing the configs and submits for any study, the proxy has to be set up using:
```
voms-proxy-init --voms cms --valid 192:00
```
Furthermore the proxy has to be copied to a path accesible by all condor nodes and this path has to be defined in the `X509_USER_PROXY` variable. This can for example be done by adding the following command to your `.bashrc`:
```
alias voms="voms-proxy-init --voms cms --valid 192:00 && cp /tmp/x509up_u91806 ~/proxy && export X509_USER_PROXY=/afs/cern.ch/user/d/dmeuser/proxy/x509up_u91806"
```
Here, `/d/dmeuser/` has to be replaced by your personal path and the `proxy` folder has to be created. Afterwards, one should be able to use `voms` to create the proxy, copy it to the `proxy` folder and set the `X509_USER_PROXY` variable.
After this the configs and submits can be prepared using:
```
python createSubmitDAG.py
```
Here the run range as well as the LG/HG option and the Zmumu option are specified in the python script directly. The method `writeDag_Trend` in `createSubmitDAG.py` write a dagman submit script which can then be submitted by:
```
condor_submit_dag logs/dag_submit.dag
```
The status of the running job can be checked by:
```
./watch_condor_q
```
If one aims to submit the condor jobs to the `group_u_CMS.CAF.ALCA` accounting group (only available for members of the `cms-caf-alca-TRACKERALIGN` e-group), the job have to be submitted from a t0 node. For this before submitting the jobs the t0 configuration can be setup by:
```
module load lxbatch/tzero
```
