#!/usr/bin/env python3

import collections
import glob
import re
import os
import copy
import numpy as np
import datetime
import string
import shutil
import subprocess
import pickle
import math
import json
import ast
import sys
import csv

import ROOT
from ROOT import gPad, gStyle, gROOT

# class defining the plotting parameters for different measures (e.g. movement) and different variables (e.g. Xpos)
# the colors for different subdetectors are defined as well
class Parameter:
    name = ""     # variable name
    label = ""    # axis label
    cut = 0       # threshold value
    veto = 0      # veto value
    minDraw = 0   # x-axis lower limit
    maxDraw = 0   # x-axis upper limit
    def __init__(self, n, l, c, v, minDraw, maxDraw):
        self.name = n
        self.label = l
        self.cut = c
        self.veto = v
        self.minDraw = minDraw
        self.maxDraw = maxDraw
parameters = [    # movements
    Parameter("Xpos", "#Deltax [#mum]", 5, 200, -30, 30 ), \
    Parameter("Ypos", "#Deltay [#mum]", 10, 200, -30, 30 ), \
    Parameter("Zpos", "#Deltaz [#mum]", 15, 200, -30, 30 ), \
    Parameter("Xrot", "#Delta#theta_{x} [#murad]", 30, 200, -50, 50 ), \
    Parameter("Yrot", "#Delta#theta_{y} [#murad]", 30, 200, -50, 50 ), \
    Parameter("Zrot", "#Delta#theta_{z} [#murad]", 30, 200, -50, 50 )
    ]
parameters_e = [  # errors
    Parameter("Xpos", "#sigma_{#Deltax} [#mum]", 0, 10, -30, 30 ), \
    Parameter("Ypos", "#sigma_{#Deltay} [#mum]", 0, 10, -30, 30 ), \
    Parameter("Zpos", "#sigma_{#Deltaz} [#mum]", 0, 10, -30, 30 ), \
    Parameter("Xrot", "#sigma_{#Delta#theta_{x}} [#murad]", 0, 10, -50, 50 ), \
    Parameter("Yrot", "#sigma_{#Delta#theta_{y}} [#murad]", 0, 10, -50, 50 ), \
    Parameter("Zrot", "#sigma_{#Delta#theta_{z}} [#murad]", 0, 10, -50, 50 )
    ]
parameters_sig = [ # significances
    Parameter("Xpos", "#Deltax/#sigma_{#Deltax}", 2.5, 0, -30, 30 ), \
    Parameter("Ypos", "#Deltay/#sigma_{#Deltay}", 2.5, 0, -30, 30 ), \
    Parameter("Zpos", "#Deltaz/#sigma_{#Deltaz}", 2.5, 0, -30, 30 ), \
    Parameter("Xrot", "#Delta#theta_{x}/#sigma_{#Delta#theta_{x}}", 2.5, 0, -50, 50 ), \
    Parameter("Yrot", "#Delta#theta_{y}/#sigma_{#Delta#theta_{y}}", 2.5, 0, -50, 50 ), \
    Parameter("Zrot", "#Delta#theta_{z}/#sigma_{#Delta#theta_{z}}", 2.5, 0, -50, 50 )
    ]
parDict = collections.OrderedDict( (p.name, p) for p in parameters )
objects = [    # define color for different subdetectors
    ("Disk-1", ROOT.kBlack),
    ("Disk-2", ROOT.kCyan),
    ("Disk-3", ROOT.kBlue),
    ("Disk1", ROOT.kBlack+3),
    ("Disk2", ROOT.kCyan+2),
    ("Disk3", ROOT.kBlue+2),
    ("Layer1", ROOT.kRed),
    ("Layer2", ROOT.kGreen+2),
    ("Layer3", ROOT.kMagenta),
    ("Layer4", ROOT.kOrange),
]

# method to save plots and create saving path if not exists
def save(name, folder="plots", endings=[".pdf"]):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for ending in endings:
        ROOT.gPad.GetCanvas().SaveAs(os.path.join(folder,name+ending))

# method to get the runNo from a filename
def runFromFilename(filename):
    m = re.match(".*run(\d+)/", filename)
    if m:
        return int(m.group(1))
    else:
        print("Could not find run number for file", filename)
        return 0

# method to sort dictionary by key value
def sortedDict(d):
    return collections.OrderedDict(sorted(d.items(), key=lambda t: t[0]))

# method to get root object from DQM file
def getFromFile(filename, objectname):
    f = ROOT.TFile(filename)
    if f.GetSize()<50000: # DQM files sometimes are empty
        return None
    h = f.Get(objectname)
    h = ROOT.gROOT.CloneObject(h)
    return h

def randomName():
    """
    Generate a random string. This function is useful to give ROOT objects
    different names to avoid overwriting.
    """
    from random import randint
    from sys import maxsize
    return "%x"%(randint(0, maxsize))

# method to merge overflow (and underflow) of a given histogram
def mergeOverflow(h,includeUnderflow):
    N=h.GetNbinsX()
    entries=h.GetEntries()
    #overflow
    cont=h.GetBinContent(N)+h.GetBinContent(N+1)
    err2=np.sqrt(h.GetBinError(N)**2+h.GetBinError(N+1)**2)
    #set content+error of last bin
    h.SetBinContent(N,cont)
    h.SetBinError(N,np.sqrt(err2))
    #clear overflow
    h.SetBinContent(N+1,0)
    h.SetBinError(N+1,0)
    #underflow
    if includeUnderflow:
        cont=h.GetBinContent(0)+h.GetBinContent(1)
        err2=np.sqrt(h.GetBinError(0)**2+h.GetBinError(1)**2)
        #set content+error of first bin
        h.SetBinContent(1,cont)
        h.SetBinError(1,np.sqrt(err2))
        #clear overflow
        h.SetBinContent(0,0)
        h.SetBinError(0,0)
        #restore correct number of entries
        h.SetEntries(entries)
    return h

# method to get histograms from list a given search path (returns multiple histograms per run)
def getInputHists(searchPath):
    hists = {}
    statusHists = {}
    for filename in glob.glob(searchPath):
        runNr = runFromFilename(filename)
        #  ~if runNr!=317182: continue
        print(runNr)
        path_in_file="DQMData/Run "+str(runNr)+"/AlCaReco/Run summary/SiPixelAliHG/"
        newHists = {}
        #  ~if runNr<=355120:       # currently used for debugging, should be changed to true if all runs in search path should be considered
        if True:
            for p in parameters:
                for structure in objects:
                    histName=p.name+"_HG_"+structure[0]
                    h = getFromFile(filename, path_in_file+histName)
                    if h:
                        newHists[histName] = h
            if newHists: hists[runNr] = newHists
            
            statusHists[runNr] = getFromFile(filename, path_in_file+"statusResults")
            
    return sortedDict(hists),sortedDict(statusHists)

# method to produce one histogram per variable and subdetector from multiple runs
def getCombinedHist(inputHists, minRun=-1):
    inputHists = sortedDict(dict((key,value) for key, value in inputHists.items() if key >= minRun))
    hists = {}
    hists_e = {}
    hists_sig = {}
    isbpix = False
    islayer4 = False
    vetoeList = []
    for iRun, (runNr, hmap) in enumerate(inputHists.items()):
        print(runNr)
        for hname, h in hmap.items():
            
            isbpix = hname.find("Layer")!=-1
            islayer4 = hname.find("Layer4")!=-1
            
            # this part defines the lower and upper limits of the histograms
            limit = 100
            limit_e = 30
            if isbpix==False and hname.find("Xrot")!=-1: 
                limit = 600
                limit_e = 400
            elif isbpix==False and hname.find("Zrot")!=-1: 
                limit = 600
                limit_e = 200
            elif hname.find("Yrot")!=-1: 
                limit=1000
                limit_e = 400
            
            #set overflow bin to zero (otherwise will be largest bin)
            h.SetBinContent(h.GetMaximumBin(),0.)
            
            if((abs(h.GetBinContent(h.GetMaximumBin()))>h.GetBinContent(h.GetNbinsX()-1)) or (abs(h.GetBinContent(h.GetMinimumBin()))>h.GetBinContent(h.GetNbinsX()-1))):
                print("Veto in ",hname,h.GetMaximumBin())
                if runNr not in vetoeList:
                    vetoeList.append(runNr)
            
            hdefault = ROOT.TH1F("",";Movement;Entries",100,-limit,limit)
            hdefault_e = ROOT.TH1F("",";Error;Entries",100,0,limit_e)
            hdefault_sig = ROOT.TH1F("",";Error;Entries",100,-20,20)
            if isbpix==False:
                if hname not in hists:
                    hists[hname] = hdefault.Clone()
                    hists_e[hname] = hdefault_e.Clone()
                    hists_sig[hname] = hdefault_sig.Clone()
                if h.GetBinContent(1)==0:
                   failed = True 
                   continue  #alignment did not finish successfull
                for bin in range(1,h.GetNbinsX()+1):
                    c = h.GetBinContent(bin)
                    e = h.GetBinError(bin)
                    hists[hname].Fill(c)
                    hists_e[hname].Fill(e)
                    hists_sig[hname].Fill(c/e if e>0 else 0)
            else:   # results in bpix are separated in outer and inner ladders
                if hname+"_out" not in hists:
                    hists[hname+"_out"] = hdefault.Clone()
                    hists_e[hname+"_out"] = hdefault_e.Clone()
                    hists_sig[hname+"_out"] = hdefault_sig.Clone()
                if hname+"_in" not in hists:
                    hists[hname+"_in"] = hdefault.Clone()
                    hists_e[hname+"_in"] = hdefault_e.Clone()
                    hists_sig[hname+"_in"] = hdefault_sig.Clone()
                for bin in range(1,h.GetNbinsX()-4):    # Last bins store thresholds etc.
                    c = h.GetBinContent(bin)
                    e = h.GetBinError(bin)
                    i = 0
                    if islayer4: i=1    # numbering of inner and outer ladders in layer4 is inverted
                    if bin%2==i:
                        hists[hname+"_out"].Fill(c)
                        hists_e[hname+"_out"].Fill(e)
                        hists_sig[hname+"_out"].Fill(c/e if e>0 else 0)     # avoid dividing by zero
                    else:
                        hists[hname+"_in"].Fill(c)
                        hists_e[hname+"_in"].Fill(e)
                        hists_sig[hname+"_in"].Fill(c/e if e>0 else 0)      # avoid dividing by zero
    return [hists,hists_e,hists_sig],vetoeList
    
# method to get combined status hist
def getCombinedStatus(statusHist, vetoeList, minRun=-1):
    statusHist = sortedDict(dict((key,value) for key, value in statusHist.items() if key >= minRun))
    combinedStatus = ROOT.gROOT.CloneObject(list(statusHist.values())[0])
    combinedStatus.Reset()
    combinedStatus_singleTrigger = ROOT.gROOT.CloneObject(combinedStatus)
    totalUpates = 0;
    
    for iRun, (runNr, hmap) in enumerate(statusHist.items()):   # add status histograms of all runs
        updateTriggered = False
        nTriggered = 0
        #  ~if runNr in [355100,355127,357268,357271,357698,357759]
        if(hmap):
            for i in range(1,hmap.GetNbinsX()+1):
                for j in range(1,hmap.GetNbinsY()+1):
                    if (hmap.GetBinContent(i,j)>0):
                        updateTriggered = True
                        nTriggered += 1
            
            if updateTriggered and runNr in vetoeList:
                print("Veto ",runNr)
                continue
            
            combinedStatus.Add(hmap)
            if(nTriggered == 1):
                combinedStatus_singleTrigger.Add(hmap)
            if(updateTriggered):
                totalUpates+=1
    
    combinedStatus_unscaled = ROOT.gROOT.CloneObject(combinedStatus)
    combinedStatus.Scale(1./totalUpates)    # scale by total number of updates
    return combinedStatus,combinedStatus_unscaled,combinedStatus_singleTrigger
            
            
# method to draw the combined histograms
def drawCombinedHists(hmaps,plotDir):
    for ih,hmap in enumerate(hmaps):    # ih loops over movement, error and significance hists
        objectDict = {}
        for structure in objects:
            objectDict[structure[0]] = structure[1]
        
        paramDict = {}
        parameters_temp = parameters
        if ih==1 : parameters_temp=parameters_e     # get correct parameters
        elif ih==2 : parameters_temp=parameters_sig
        for param in parameters_temp:
            paramDict[param.name] = param
        if not hmap: return
        gROOT.SetBatch(True)
        line = ROOT.TLine()
        line.SetLineStyle(2)
        line_e = ROOT.TLine()
        line_e.SetLineStyle(2)
        line_e.SetLineColor(ROOT.kRed)
        leg = ROOT.TLegend(.61, .78, .969, .929)
        leg.SetNColumns(2)
        leg.SetBorderSize(1)
        leg.SetLineWidth(2)
        #  ~leg.AddEntry(line, "Threshold", "l")
        gStyle.SetFrameLineWidth(2)
        c = ROOT.TCanvas(randomName(),"",700,600)
        hists = {}
        isbpix = False
        for ig,(name,hist) in enumerate(hmap.items()):      # ig loops over the combination of different detector parts and variables
            print(name)
            isbpix = name.find("Layer")!=-1
            structure = name.split("_")[2]      # get structure from name (e.g. Layer1)
            param = name.split("_")[0]      # get histogram type from name (e.g. movement)
            hist = mergeOverflow(hist,True)
            hists[ig] = hist.Clone()
            hists[ig].SetStats(0)
            hists[ig].SetTitle(";{};{}".format(paramDict[param].label,"Entries"))
            gPad.SetLeftMargin(100)
            hists[ig].SetMarkerColor(objectDict[structure])
            hists[ig].SetLineColor(objectDict[structure])
            hists[ig].SetLineWidth(2)
            hists[ig].SetMaximum(1.3*hists[ig].GetMaximum())
            hists[ig].Draw("hist")
            hists[ig].GetYaxis().SetTitleOffset(0.95)
            gStyle.SetHistTopMargin(0.)
            if ih==0 or ih==2:  # show different thresholds/veto lines depending on the histogram type
                line.DrawLine(-paramDict[param].cut, 0, -paramDict[param].cut,hists[ig].GetMaximum())
                line.DrawLine(+paramDict[param].cut, 0, +paramDict[param].cut,hists[ig].GetMaximum())
            if ih==0 or ih==1:
                if ih==0: line_e.DrawLine(-paramDict[param].veto, 0, -paramDict[param].veto,hists[ig].GetMaximum())
                line_e.DrawLine(+paramDict[param].veto, 0, +paramDict[param].veto,hists[ig].GetMaximum())
            gPad.RedrawAxis()
            text = ROOT.TLatex()
            text.SetTextSize(0.04)
            text.DrawLatexNDC(.1, .91, "#scale[1.2]{#font[61]{CMS}} #font[52]{Private Work}")
            text.DrawLatexNDC(.6, .91, "2022 pp collisions")
            text.DrawLatexNDC(.59, .645, structure+name.split("_")[3] if isbpix else structure)
            if ih!=1:       # show different percentages depending on the histogram type
                text.DrawLatexNDC(.55, .445, "{:3.0f} % above update threshold".format(100*(hists[ig].Integral(0,hists[ig].GetXaxis().FindBin(-paramDict[param].cut)-1)+hists[ig].Integral(hists[ig].GetXaxis().FindBin(+paramDict[param].cut),hists[ig].GetNbinsX()+1))/hists[ig].GetEntries()))
            if (ih==0 and paramDict[param].veto<hists[ig].GetXaxis().GetXmax()):
                text.DrawLatexNDC(.55, .345, "{:3.0f} % above veto threshold".format(100*(hists[ig].Integral(0,hists[ig].GetXaxis().FindBin(-paramDict[param].veto)-1)+hists[ig].Integral(hists[ig].GetXaxis().FindBin(+paramDict[param].veto),hists[ig].GetNbinsX()+1))/hists[ig].GetEntries()))
            elif (ih==1 and paramDict[param].veto<hists[ig].GetXaxis().GetXmax()):
                text.DrawLatexNDC(.55, .345, "{:3.0f} % above veto threshold".format(100*hists[ig].Integral(hists[ig].GetXaxis().FindBin(+paramDict[param].veto),hists[ig].GetNbinsX()+1)/hists[ig].GetEntries()))
            if ih==0 : save(name, plotDir+"/movements", endings=[".pdf",".root"])
            elif ih==1 : save(name, plotDir+"/errors", endings=[".pdf",".root"])
            else : save(name, plotDir+"/significance", endings=[".pdf",".root"])
            c.Clear()
            leg.Clear()

# method to draw the combined histograms
def drawCombinedStatus(combinedStatus,plotDir,saveName,zTitle):
    gROOT.SetBatch(True)
    c = ROOT.TCanvas(randomName(),"",800,600)
    gPad.SetLeftMargin(0.15)
    gPad.SetRightMargin(0.15)
    combinedStatus.SetStats(0)
    combinedStatus.GetZaxis().SetTitle(zTitle)
    combinedStatus.Draw("colz text")
    save(saveName, plotDir, endings=[".pdf",".root"])
    

if __name__ == "__main__":
    #########Define the output directory#############
    plotDir = "./plots/Rerun_2022_vetoesApplies"

    #########Define path of histograms###############
    searchPath="/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2022/output/HG_run*/DQM*.root"
    #  ~searchPath="/eos/cms/store/caf/user/dmeuser/PCL/condor_PCL_2022/Rerun_2022B_2022D/HG_run*/DQM*.root"
    
    # get input histograms from one DQM file per run
    inputHists,statusHists = getInputHists(searchPath)
    
    # prepare combined histograms from multiple runs
    combinedHists,vetoeList = getCombinedHist(inputHists)
    
    print(vetoeList)
    
    # prepare combined status hist from multiple runs
    combinedStatus,combinedStatus_unscaled,combinedStatus_singleTrigger = getCombinedStatus(statusHists,vetoeList)
    
    # draw combined histograms
    drawCombinedHists(combinedHists,plotDir)
    
    # draw combined status
    drawCombinedStatus(combinedStatus,plotDir,"combinedStatus","Included in x% of the updates")
    drawCombinedStatus(combinedStatus_unscaled,plotDir,"combinedStatus_unscaled","Number of updates triggered")
    drawCombinedStatus(combinedStatus_singleTrigger,plotDir,"combinedStatus_singleTrigger","Number of single triggered updates")
