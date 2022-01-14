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

#Check the path of input files
def input_file2 (path):
	while True:
		if os.path.isfile(path):
			return
		else:
			path = input("Doesn't exist. Enter the path again: ")

#Open a config file
config = open("fusion_sample.config", "w")

while True:
	answer = raw_input("Do you still have multiple fusion jobs to chain together?:")
	if answer.lower().startswith("n"):
		print("***Chaining fusion samples***")
		time.sleep(2)
		break
	elif answer.lower().startswith("y"):
		sample1 = raw_input("Enter the sample name and the path of the fusion files in this format (SAMPLE=<sample name>;<path>):")
		config.write(sample1 + '\n')
		sample2 = raw_input("Enter the sample name and the path of the fusion files in this format (SAMPLE=<sample name>;<path>):")
		config.write(sample2 + '\n')
		while True:
			answer = raw_input("Do you have more samples to chain?:")
			if answer.lower().startswith("n"):
				config.write('\n')
				config.write("GROUP_FILENAME=aligned.sorted.sam.fusion.group.txt" + '\n')
				config.write("GFF_FILENAME=aligned.sorted.sam.fusion.gff" + '\n')
				config.write("COUNT_FILENAME=aligned.sorted.sam.fusion.abundance.txt" + '\n')
				config.write("FASTQ_FILENAME=aligned.sorted.sam.fusion.rep.fa")
				config.close()
				subprocess.call("ls *.config", shell = True)
				time.sleep(2)
				break
			elif answer.lower().startswith("y"):
				sample = raw_input("Enter the sample name and the path of the fusion files in this format (SAMPLE=<sample name>;<path>):")
				config.write(sample + '\n')

#Check the path of input file
input_file2("fusion_sample.config")

#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)

fusion_sample_config = os.path.join(current_path, "fusion_sample.config")

chain_fusion = "chain_fusion_samples.py" + " " + fusion_sample_config + " " + "count_fl"
os.system(chain_fusion)

subprocess.call("ls all_samples.*", shell = True)
time.sleep(2)
