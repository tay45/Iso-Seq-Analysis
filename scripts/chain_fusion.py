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


#Open a config file
config = open("fusion_sample.config", "w")


while True:
	answer = input("Do you still have multiple fusion jobs to chain together?:")
	if answer.lower().startswith("n"):
		print("***Chaining fusion samples***")
		time.sleep(2)
		break
	elif answer.lower().startswith("y"):
		sample1 = input("Enter the sample name and the path of the fusion files in this format (SAMPLE=<sample name>;<path>):")
		config.write(sample1 + '\n')
		sample2 = input("Enter the sample name and the path of the fusion files in this format (SAMPLE=<sample name>;<path>):")
		config.write(sample2 + '\n')
		while True:
			answer = input("Do you have more samples to chain?:")
			if answer.lower().startswith("n"):
				config.write('\n')
				config.write("GROUP_FILENAME=clustered.hq.fasta.sorted.sam.fusion.group.txt" + '\n')
				config.write("GFF_FILENAME=clustered.hq.fasta.sorted.sam.fusion.gff" + '\n')
				config.write("COUNT_FILENAME=clustered.hq.fasta.sorted.sam.fusion.abundance.txt" + '\n')
				config.close()
				subprocess.call("ls *.config", shell = True)
				time.sleep(2)
				break
			elif answer.lower().startswith("y"):
				sample = input("Enter the sample name and the path of the fusion files in this format (SAMPLE=<sample name>;<path>):")
				config.write(sample + '\n')


#Check the path of input file
input_file2("fusion_sample.config")


#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)
fusion_sample_config = os.path.join(current_path, "fusion_sample.config")
#Run chain_fusion_samples.py
chain_fusion = "chain_fusion_samples.py" + " " + fusion_sample_config + " " + "count_fl"
os.system(chain_fusion)
subprocess.call("ls all_samples.*", shell = True)
time.sleep(2)

#Save chained file in fusion_file folder
#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)
subprocess.call("mkdir fusion_chain_files", shell = True)
subprocess.call("cp all_samples.* " + current_path + "/" + "fusion_chain_files", shell = True)
#Change file name
subprocess.call("mv all_samples.chained.gff fusion.gff", shell = True)
subprocess.call("mv all_samples.chained_count.txt fusion.abundance.txt", shell = True)
#Convert gff to gtf
input_file2("fusion.gff")
current_path = os.path.abspath(os.getcwd())
print(current_path)
fusion_gff = os.path.join(current_path, "fusion.gff")
out = os.path.join(current_path, "fusion.gtf")
convert_gff = "gffread -T" + " " + fusion_gff + " -o" + " " + out
os.system(convert_gff)
subprocess.call("ls fusion.gtf", shell = True)
time.sleep(2)
exec(open("sqanti3_fusion.py").read())
