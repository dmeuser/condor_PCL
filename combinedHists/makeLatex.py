#!/usr/bin/env python2

import numpy as np
import os

def latexSlideTemplate_BPIX(direction,detector):
   out = """
\\begin{{frame}}
   \\frametitle{{{3} {0}}}
   \\begin{{columns}}
      \\begin{{column}}{{0.3\\textwidth}}
         \centering
         \includegraphics[width=\\textwidth]{{input/movements/{0}_HG_{1}.pdf}}\\
         \includegraphics[width=\\textwidth]{{input/movements/{0}_HG_{2}.pdf}}
      \end{{column}}
      \\begin{{column}}{{0.3\\textwidth}}
         \centering
         \includegraphics[width=\\textwidth]{{input/errors/{0}_HG_{1}.pdf}}\\
         \includegraphics[width=\\textwidth]{{input/errors/{0}_HG_{2}.pdf}}
      \\end{{column}}
      \\begin{{column}}{{0.3\\textwidth}}
         \centering
         \includegraphics[width=\\textwidth]{{input/significance/{0}_HG_{1}.pdf}}\\
         \includegraphics[width=\\textwidth]{{input/significance/{0}_HG_{2}.pdf}}
      \\end{{column}}
   \\end{{columns}}
\\end{{frame}}
""".format(direction,detector+"_in",detector+"_out",detector)
   return out
   
def latexSlideTemplate_FPIX(direction,detector):
   out = """
\\begin{{frame}}
   \\frametitle{{{1} {0}}}
   \\begin{{columns}}
      \\begin{{column}}{{0.3\\textwidth}}
         \centering
         \includegraphics[width=\\textwidth]{{input/movements/{0}_HG_{1}.pdf}}
      \end{{column}}
      \\begin{{column}}{{0.3\\textwidth}}
         \centering
         \includegraphics[width=\\textwidth]{{input/errors/{0}_HG_{1}.pdf}}
      \\end{{column}}
      \\begin{{column}}{{0.3\\textwidth}}
         \centering
         \includegraphics[width=\\textwidth]{{input/significance/{0}_HG_{1}.pdf}}
      \\end{{column}}
   \\end{{columns}}
\\end{{frame}}
""".format(direction,detector)
   return out
   

#  ~def getLatexSlides(path="plots/PR_starting_2018B_mid2018D/"):
def getLatexSlides(path="plots/PR_starting_2018B_diffHits/"):
   f = open(path+"out.tex","w+")
   
   for direction in ["Xpos","Ypos","Zpos","Xrot","Yrot","Zrot"]:
      f.write("\n\section{%s}\n" %direction)
      for detector in ["Layer1","Layer2","Layer3","Layer4"]:
         f.write(latexSlideTemplate_BPIX(direction,detector))
      for detector in ["Disk-3","Disk-2","Disk-1","Disk3","Disk2","Disk1"]:
         f.write(latexSlideTemplate_FPIX(direction,detector))
      
   f.close()

if __name__ == "__main__":
   getLatexSlides()
