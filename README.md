### Purpose

This code can be used to perform studies regarding the high granularity (HG) PCL alignment. The main function is to setup the config and condor submission script for running the PCL alignment with the nominal (low granularity) and the new configuration (high granularity). Once setup the jobs can be used in a dagman job to run the alignment for multiple runs iteratively, which in a way mimics the setup used during data taking.

### Installation/Requirements
Run the following lines to setup CMSSW_11_1_0_pre3 and merge the private branch for the HG PCL:
```
cmsrel CMSSW_11_1_0_pre3
cd CMSSW_11_1_0_pre3/src/
cmsenv
git cms-init
git cms-merge-topic dmeuser:hgPCL
scram b -j7
```
To setup the code of this repository first of all clone it using:
```
git clone https://github.com/dmeuser/condor_PCL_2018.git
```
There are some files in the code where the paths have to be changed when a different user is running the scripts. These parts are indicated by comments and are present in the following files:
```
milleStep.sh
pedeStep.sh
createSubmitDAG.py
```
In addition also the path to the db file for the milleStep has to be adapted in `templates/milleStep_ALCA(_HG).py`

### Structure
Using the code on lxplus there are two constraints, which led to the fact that the code is currently basically running in three different places.
* The nominal home directory `/afs/cern.ch/user/` does not offer enough storage for the code to be executed since large root files are produced while running the code. This is why the run directories are located at `/afs/cern.ch/work/`.

* Since `/afs/cern.ch/work/` also has only quite limited storage, the output after running the milleStep is copied to `/eos/cms/store/caf/user/`. Running the milleStep directly in `/eos/cms/store/caf/user/` does not work (at least at the time of developing the code).

Thus, in the files mentioned above the path to the home directory, the run directory and the output directory have to be defined.

### Code
* `createSubmitDAG.py`: Main script which prepares all necessary configs and submit scripts for the studies. Run ranges, HG/LG option etc. are defined in the lower part of the script. The script can only be executed with active proxy since the `dasgoclient` is used to find the proper input files for a given run. The scripts runs roughly the following steps
    * Dictionary of `{run:[lumiRange1,lumiRange2]}` is created using an input json
    * The longest lumi range is defined and used to setup the following configs
    * Log and run folders and the condor submits are prepared for each mille job (e.g. 20 mille jobs when using 100LS and 5LS per job) and for the final pede job (repeated for each run of the study)
    * `milleStep_ALCA(_HG).py` is setup based on the templates in `templates/` by defining the input files as well as the lumi
    * The config for the dagman job is produced looping over the mille and pede submitting script prepared before


* `milleStep.sh`: Bash script which is executed for each milleJob. It takes care of running `milleStep_ALCA(_HG).py`, which was setup by `createSubmitDAG.py` for each milleJob. At the end of each milleJob the output is copied to CAF and the run directory is cleaned.

* `pedeStep.sh`: Bash script which is executed for each pedeJob. First the outputs of the previously finished milleJobs are collected and stored in `AlcaFiles.txt`. Then the `cmsDriver.py` is used to execute the pedeStep based on the input list, the thresholds stored in `$cmsswDir/CondFormats/PCLConfig/test/mythresholds(_HG).db` and the previously generated alignment found in `payloads(_HG).db`.
 
* `templates/`: Templates for the milleStep (one for LG and one for HG). The inputs are set by `createSubmitDAG.py`. The path to `payloads(_HG).db` has to be set when changing the user.
 
* `watch_condor_q`: Simple bash scripts which check the job status every 30 second.
 
* `combinedHists/`: Code to plot histograms for the movement, error and significance for a given study. Histograms for different settings can be compared with `compareDiffHits.py`. `makeLatex.py` can be used to prepare latex beamer slides for a given set of histograms.


### Example of running 
In the following an example of running the PCL alignment for a given run range iteratively (the alignment for each run is based on the result of the previous run due to loading `payloads(_HG).db`) is shown. 
Before producing the configs and submits for any study, the proxy has to be set up using:
```
voms-proxy-init --voms cms --valid 192:00
```
In addition one has to make sure, that the output folder contains a valid db file named `payloads.db`(for LG) or `payloads_HG.db`(forHG), where the starting geometry is stored. A db file with the starting geometry using PromptReco can always be produced by (remember to adapt the run and to rename the db file):
```
conddb_import -f frontier://FrontierProd/CMS_CONDITIONS -i TrackerAlignment_PCL_byRun_v2_express -c sqlite:payloads_HG.db -b 317080 -e 317080 -t SiPixelAli_pcl
```
After this the configs and submits can be prepared using:
```
python createSubmitDAG.py
```
Here the run range as well as the LG or HG option are specified in the python script directly. The method `writeDag_Trend` in `createSubmitDAG.py` write a dagman submit script which can then be submitted by:
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
