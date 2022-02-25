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


#Check the input files (no parser) 
def input_file2 (path):
	if os.path.isfile(path):
		return
	else:
		print("Doesn't exist. Please check the file location")


#Generate sorted.sam
print("***Aligning minimap2***")
time.sleep(2)
#Unzip clustered.hq.fasta.gz
with gzip.open('clustered.hq.fasta.gz', 'rb') as file_in:
	with open('clustered.hq.fasta', 'wb') as file_out:
		shutil.copyfileobj(file_in, file_out)
	#Check the path of input file
input_file2("clustered.hq.fasta")
subprocess.call("ls clustered.hq.*", shell = True)
time.sleep(2)
#Add reference file
reference2 = ""
reference2 = input("Enter the path of the 'genome reference (.fasta)'.: ")
input_file2(reference2)
#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)
clustered_fasta = os.path.join(current_path, "clustered.hq.fasta")
out = os.path.join(current_path, "clustered.hq.fasta.sam")
#Run minimap2
align2 = "minimap2 -ax splice -t 30 -uf --secondary=no -C5" + " " + reference2 + " " + clustered_fasta + " " + ">" + " " + out
os.system(align2)


#Sort clustered.hq.fasta.sam
sort = "sort -k 3,3 -k 4,4n" + " " + out + ">" + " " + "clustered.hq.fasta.sorted.sam"
os.system(sort)
subprocess.call("ls clustered.hq.*", shell = True)
time.sleep(2)


#Finding fusion genes
print("***Finding fusion genes***")
time.sleep(2)
#Check the path of input file
input_file2("clustered.hq.fasta")
input_file2("clustered.hq.fasta.sorted.sam")
input_file2("clustered.cluster_report.csv")
#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)
#Parameters
fasta = os.path.join(current_path, "clustered.hq.fasta")
sam = os.path.join(current_path, "clustered.hq.fasta.sorted.sam")
out = os.path.join(current_path, "clustered.hq.fasta.sorted.sam.fusion")
report = os.path.join(current_path, "clustered.cluster_report.csv")
#Run fusion_finder.py
fusion = "fusion_finder.py --input " + fasta + " -s " + sam + " -o " + out + " --cluster_report_csv " + report #+ " --dun-merge-5-shorter"
os.system(fusion)
subprocess.call("ls *.fusion.*", shell = True)
time.sleep(2)


#Save chained file in fusion_file folder
#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)
subprocess.call("mkdir fusion_files", shell = True)
subprocess.call("cp clustered.hq.fasta.sorted.sam.fusion.* " + current_path + "/" + "fusion_files", shell = True)
subprocess.call("cp branch_tmp.group.txt " + current_path + "/" + "fusion_files", shell = True)


#Chaining fusion genes
while True:
	answer = input("Do you have multiple fusion jobs to chain together?:")
	if answer.lower().startswith("n"):
		#Change file name
		subprocess.call("mv clustered.hq.fasta.sorted.sam.fusion.gff fusion.gff", shell = True)
		subprocess.call("mv clustered.hq.fasta.sorted.sam.fusion.abundance.txt fusion.abundance.txt", shell = True)
		#Convert gff to gtf
		input_file2("fusion.gff")
		current_path = os.path.abspath(os.getcwd())
		print(current_path)
		fusion_gff = os.path.join(current_path, "fusion.gff")
		out = os.path.join(current_path, "fusion.gtf")
		#Run gffread
		convert_gff = "gffread -T" + " " + fusion_gff + " -o" + " " + out
		os.system(convert_gff)
		subprocess.call("ls fusion.gtf", shell = True)
		time.sleep(2)
		exec(open("sqanti3_fusion.py").read())
	elif answer.lower().startswith("y"):
		exec(open("chain_fusion.py").read())
