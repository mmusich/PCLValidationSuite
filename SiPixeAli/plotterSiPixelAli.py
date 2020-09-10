#!/usr/bin/env python2

import collections
import glob
import re
import os
import copy
import numpy
import datetime
import string
import shutil
import subprocess
import pickle
import math
import json

#with suppressor.suppress_stdout_stderr(): 
import ROOT
import style

class Parameter:
    name = ""
    label = ""
    cut = 0
    minDraw = 0
    maxDraw = 0
    def __init__(self, n, l, c, minDraw, maxDraw):
        self.name = n
        self.label = l
        self.cut = c
        self.minDraw = minDraw
        self.maxDraw = maxDraw
parameters = [
    Parameter("Xpos", "#Deltax (#mum)", 5, -30, 30 ), \
    Parameter("Ypos", "#Deltay (#mum)", 10, -30, 30 ), \
    Parameter("Zpos", "#Deltaz (#mum)", 15, -30, 30 ), \
    Parameter("Xrot", "#Delta#theta_{x} (#murad)", 30, -50, 50 ), \
    Parameter("Yrot", "#Delta#theta_{y} (#murad)", 30, -50, 50 ), \
    Parameter("Zrot", "#Delta#theta_{z} (#murad)", 30, -70, 70 )
    ]
parDict = collections.OrderedDict( (p.name, p) for p in parameters )
objects = [
    ("FPIX(x+,z-)", ROOT.kBlack),
    ("FPIX(x-,z-)", ROOT.kRed),
    ("BPIX(x+)", ROOT.kBlue),
    ("BPIX(x-)", ROOT.kCyan),
    ("FPIX(x+,z+)", ROOT.kGreen+2),
    ("FPIX(x-,z+)", ROOT.kMagenta),
    ]

plotDir="./"

def exceedsCuts(h, cutDict=False):
    maxErrCut = 10
    sigCut = 2.5
    maxCut = 200
    var = h.GetName().split("_")[0]
    cut = parDict[var].cut

    binInfos = []
    for bin in range(1,h.GetNbinsX()+1):
        c = abs(h.GetBinContent(bin))
        e = h.GetBinError(bin)
        if c > maxCut or e > maxErrCut:
            binInfos.append("fail")
        elif c > cut and e and c/e > sigCut:
            binInfos.append("update")
        else:
            binInfos.append("good")
    if "fail" in binInfos:
        return "fail"
    elif "update" in binInfos:
        return "update"
    else:
        return "good"

def save(name, folder="plots", endings=[".png"]):
    for ending in endings:
        ROOT.gPad.GetCanvas().SaveAs(os.path.join(folder,name+ending))

def randomName():
    """
    Generate a random string. This function is useful to give ROOT objects
    different names to avoid overwriting.
    """
    from random import randint
    from sys import maxint
    return "%x"%(randint(0, maxint))

def runFromFilename(filename):
    tokens = filename.split("_")
    for tok in tokens:
        if "R" in tok:
            return tok[-6:]
    print "Could not find run number for file", filename
    return 0

def getFromFile(filename, objectname):
    print filename
    f = ROOT.TFile(filename)
    #print f.ls()
    if f.GetSize()<5000: # DQM files sometimes are empty
        return None
    h = f.Get("DQMData/Run "+runFromFilename(filename)+"/AlCaReco/Run summary/SiPixelAli/"+objectname)
    print h.GetName() 
    h = ROOT.gROOT.CloneObject(h)
    return h

def sortedDict(d):
    return collections.OrderedDict(sorted(d.items(), key=lambda t: t[0]))

def getInputHists(searchPath="./DQM*.root"):
    hists = {}
    for filename in glob.glob(searchPath):
        runNr = runFromFilename(filename)
        newHists = {}
        if searchPath.endswith("pippo.root"):
            c = getFromFile(filename, "Xpos")
            for pad in c.GetListOfPrimitives():
                pad.cd()
                for x in pad.GetListOfPrimitives():
                    if isinstance(x, ROOT.TH1F):
                        newHists[x.GetName()] = x.Clone()
                        break
        else: # dqm plots
            print "these are DQM plots"
            for p in parameters:
                h = getFromFile(filename, p.name)
                if h:
                    newHists[p.name] = h
        if newHists: hists[runNr] = newHists
    return sortedDict(hists)


def drawHists(hmap, savename, run):
    hnames = ["Xpos", "Ypos","Zpos", "Xrot", "Yrot", "Zrot"]
    line = ROOT.TLine()
    line.SetLineColor(ROOT.kRed)
    c = ROOT.TCanvas(randomName(),"",1200,600)
    c.Divide(3,2)
    dbUpdated = False
    for ih, hname in enumerate(hnames):
        c.cd(ih+1)
        c.cd(ih+1).SetTopMargin(1.)
        c.cd(ih+1).SetLeftMargin(0.1)
        c.cd(ih+1).SetRightMargin(0.02)
        h = hmap[hname]
        h.SetLineColor(ROOT.kBlack)
        h.SetFillColor(ROOT.kGreen-7)
        h.GetYaxis().SetTitleOffset(0.9)
        cutStatus = exceedsCuts(h)
        if cutStatus == "update":
            h.SetFillColor(ROOT.kOrange-9)
            dbUpdated = True
        elif cutStatus == "fail":
            h.SetFillColor(ROOT.kRed)
        for bin in range(1,7):
            h.GetXaxis().SetBinLabel(bin,objects[bin-1][0])
        h.GetXaxis().SetRange(1,6)
        h.GetYaxis().SetRangeUser(-50,50)
        h.SetTitle("")
        h.GetYaxis().SetTitle(parameters[ih].label)
        h.Draw("histe")
        cut = h.GetBinContent(8)
        if not cut:
            cuts = {"Xpos":5, "Ypos":10, "Zpos":15, "Xrot":30, "Yrot":30, "Zrot":30}
            cut = cuts[h.GetName().split("_")[0]]
        line.DrawLine(0,-cut,6,-cut)
        line.DrawLine(0,+cut,6,+cut)
    c.cd(0)
    text = ROOT.TLatex()
    text.SetTextSize(.75*text.GetTextSize())
    text.DrawLatexNDC(.05, .95, "#scale[1.2]{#font[61]{CMS}} #font[52]{Internal}")
    text.DrawLatexNDC(.82, .95, "Run {} (13TeV)".format(run))
    save(savename, plotDir,[".png"])

if __name__ == "__main__":
    inputHists = getInputHists()

    # draw new runs:
    alreadyPlotted = [ int(x[3:9]) for x in os.listdir(plotDir) if x.endswith(".pdf") and x.startswith("Run")]
    for run, hmap in inputHists.iteritems():
        if run not in alreadyPlotted:
            drawHists(hmap, "Run{}".format(run), run)
