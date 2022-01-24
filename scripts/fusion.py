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

#Change Python version
while True:
	answer = raw_input("Have you switched the Python version to 2.7.14?:")
	if answer.lower().startswith("y"):
		print("***Running the fusion script.***")
		time.sleep(2)
		break
	elif answer.lower().startswith("n"):
		print("***Please load 'Python/2.7.14' using 'module load' in Apollo.***")
		time.sleep(2)
		sys.exit()

#Check the path of input files
def input_file2 (path):
	while True:
		if os.path.isfile(path):
			return
		else:
			path = input("Doesn't exist. Enter the path again: ")	

#Converting bam to sam
print("***Converting bam to sam***")
time.sleep(2)

#Check the path of input file
input_file2("aligned.sorted.bam")

#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)

aligned_sorted_bam = os.path.join(current_path, "aligned.sorted.bam")
out = os.path.join(current_path, "aligned.sorted.sam")

bamtosam = "samtools view -h -o" + " " + out + " " + aligned_sorted_bam
os.system(bamtosam)

subprocess.call("ls aligned.sorted.*", shell = True)
time.sleep(2)

#Finding fusion genes
print("***Finding fusion genes***")
time.sleep(2)

#Check the path of input file
input_file2("clustered.hq.fasta.gz")
input_file2("aligned.sorted.sam")
input_file2("clustered.cluster_report.csv")

with gzip.open('clustered.hq.fasta.gz', 'rb') as file_in:
	with open('clustered.hq.fasta', 'wb') as file_out:
		shutil.copyfileobj(file_in, file_out)
	
subprocess.call("ls clustered.hq.*", shell = True)
time.sleep(2)

#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)

fasta = os.path.join(current_path, "clustered.hq.fasta")
sam = os.path.join(current_path, "aligned.sorted.sam")
out = os.path.join(current_path, "aligned.sorted.sam.fusion")
report = os.path.join(current_path, "clustered.cluster_report.csv")

fusion = "fusion_finder.py --input " + fasta + " -s " + sam + " -o " + out + " --cluster_report_csv " + report
os.system(fusion)

subprocess.call("ls *.fusion.*", shell = True)
time.sleep(2)

#Chaining fusion genes
while True:
	answer = raw_input("Do you have multiple fusion jobs to chain together?:")
	if answer.lower().startswith("n"):
		break
	elif answer.lower().startswith("y"):
		subprocess.call("mkdir chain_fusion", shell = True)
		current_path = os.path.abspath(os.getcwd())
		print(current_path)
		execfile("chain_fusion.py")		
		quit()
		
subprocess.call("mkdir fusion", shell = True)
subprocess.call("cp aligned.sorted.sam.fusion.* " + current_path + "/" + "fusion", shell = True)
subprocess.call("cp branch_tmp.group.txt " + current_path + "/" + "fusion", shell = True)
subprocess.call("cp sqanti3.py " + current_path + "/" + "fusion", shell = True)
os.chdir(current_path + "/" + "fusion")
subprocess.call("mv aligned.sorted.sam.fusion.gff collapsed.gff", shell = True)
subprocess.call("mv aligned.sorted.sam.fusion.abundance.txt collapsed.abundance.txt", shell = True)
quit()
