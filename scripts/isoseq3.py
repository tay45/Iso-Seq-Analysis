#!/usr/bin/python

import os
import os.path
import subprocess
import fileinput
import argparse
import sys
import time
import gzip
import shutil

#Load modules
#module load smrtlink/10.1
#module load cDNA_Cupcake
#module load SQANTI3
#module load gffread/0.12.7

#Check the path of input files
def input_path (path):
	if os.path.isfile(path):
		return path
	else:
		parser.error("Doesn't exist the %s!" % path)
		
#Check the input file
def input_file (parser, arg):
	if os.path.isfile(arg):
		return open(arg, 'r')
	else:
		parser.error("Doesn't exist the %s!" % arg)

#Check the input files (no parser) 
def input_file2 (path):
	while True:
		if os.path.isfile(path):
			return
		else:
			path = input("Doesn't exist. Enter the path again: ")


#Commend line arguments in lima
parser = argparse.ArgumentParser(description = "Running Iso-Seq pipeline")
parser.add_argument("-c", dest="ccs", required=True, help='path of input ccs.bam', metavar="CCS File", type=input_path)
parser.add_argument("-p", dest="primers", required=True, help='path of input primers.fasta', metavar="Primer File", type=input_path)
parser.add_argument("-o", dest="output", required=True, help='output file (fl.bam)', metavar="fl.bam")
parser.add_argument("-pf", dest="primers_file", required=False, help='input primers.fasta', metavar="Primer File", type=lambda x: input_file(parser, x))
args = parser.parse_args()



#Confirm the setting of SMRT_Root
while True:
	answer = input("Have you loaded the required modules before running the pipeline?:")
	if answer.lower().startswith("y"):
		print("***Start the pipeline.***")
		time.sleep(2)
		break
	elif answer.lower().startswith("n"):
		print("***Please load 'smrtlink/10.1', 'cDNA_Cupcake', 'SQANTI3', and 'gffread/0.12.7' using 'module load' in Apollo.***")
		time.sleep(2)
		sys.exit()



#Confirm primer sequences
primers_file = args.primers_file
print(primers_file.read())



#run lima
ccs = args.ccs
primers = args.primers
out = args.output

print("***Primer removal and demultiplexing***")
time.sleep(2)

lima = "lima --version"
os.system(lima)

lima = "lima" + " " + ccs + " " + primers + " " + out + " --isoseq --peek-guess"
os.system(lima)

subprocess.call("ls fl*", shell = True)
time.sleep(2)



#run refine
print("***Refining***")
time.sleep(2)

isoseq3 = "isoseq3 --version"
os.system(isoseq3)

#Change the input file name
subprocess.call("mv fl.*.bam lima.bam", shell = True)

#Check the path of input file
input_file2("lima.bam")

#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)

lima_bam = os.path.join(current_path, "lima.bam")
primers = os.path.join(current_path, "primers.fasta")
out = os.path.join(current_path, "flnc.bam")

refine = "isoseq3 refine" + " " + lima_bam + " " + primers + " " + out
os.system(refine)

subprocess.call("ls flnc.*", shell = True)
time.sleep(2)



#Run cluster
while True:
	answer = input("Do you have additional SMRT Cells for proceeding the next analysis?:")
	if answer.lower().startswith("n"):
		print("***Clustering.***")
		time.sleep(2)
		#Check the path of input file
		input_file2("flnc.bam")
		#Current working directory
		current_path = os.path.abspath(os.getcwd())
		print(current_path)
		flnc_bam = os.path.join(current_path, "flnc.bam")
		out = os.path.join(current_path, "clustered.bam")
		cluster = "isoseq3 cluster" + " " + flnc_bam + " " + out + " --verbose --use-qvs"
		os.system(cluster)
		subprocess.call("ls clustered*", shell = True)
		time.sleep(2)
		break
	elif answer.lower().startswith("y"):
		print("***Perform '$ ls flnc.bam flnc.bam flnc.bam ... > flnc.fofn.'***")
		time.sleep(2)
		flnc_bam = ""
		flnc_bam = input("Enter the path of the 'flnc.fofn'.: ")
		input_file2(flnc_bam)
		output = ""
		output = input("copy 'clustered.bam' and paste here: ")
		cluster = "isoseq3 cluster" + " " + flnc_bam + " " + out + " --verbose --use-qvs"
		os.system(cluster)
		subprocess.call("ls clustered*", shell = True)
		time.sleep(2)
		break



#Run pbmm2
print("***Aligning***")
time.sleep(2)

#Add reference file
reference = ""
reference = input("Enter the path of the 'genome reference file'.: ")
input_file2(reference)

#Check the path of input file
input_file2("clustered.hq.bam")
#input_file2("hg38.mmi")

#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)

clustered_bam = os.path.join(current_path, "clustered.hq.bam")
#reference = os.path.join(current_path, "hg38.mmi")
out = os.path.join(current_path, "aligned.sorted.bam")

align = "pbmm2 align" + " " + clustered_bam + " " + reference + " " + out + " --preset ISOSEQ --sort"
os.system(align)

subprocess.call("ls aligned.sorted.*", shell = True)
time.sleep(2)



#Run collapse
print("***Collapsing***")
time.sleep(2)

#Check the path of input file
input_file2("aligned.sorted.bam")

#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)

aligned_bam = os.path.join(current_path, "aligned.sorted.bam")
out = os.path.join(current_path, "collapsed.gff")

collapse = "isoseq3 collapse" + " " + aligned_bam + " " + ccs + " " + out
os.system(collapse)

#Convert gff to gtf
input_file2("collapsed.gff")

current_path = os.path.abspath(os.getcwd())
print(current_path)

collapsed_gff = os.path.join(current_path, "collapsed.gff")
out = os.path.join(current_path, "collapsed.gtf")

convert_gff = "gffread -T" + " " + collapsed_gff + " -o" + " " + out
os.system(convert_gff)

subprocess.call("ls collapsed.*", shell = True)
time.sleep(2)



##Run SQANTI3
exec(open("sqanti3.py").read())	
