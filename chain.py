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
config = open("sample.config", "w")

while True:
	answer = input("Do you still have multiple Iso-Seq jobs to chain together?:")
	if answer.lower().startswith("n"):
		print("***Chaining samples***")
		time.sleep(2)
		break
	elif answer.lower().startswith("y"):
		sample1 = input("Enter the sample name and the path of the collapsed files in this format (SAMPLE=<sample name>;<path>):")
		config.write(sample1 + '\n')
		sample2 = input("Enter the sample name and the path of the collapsed files in this format (SAMPLE=<sample name>;<path>):")
		config.write(sample2 + '\n')
		while True:
			answer = input("Do you have more samples to chain?:")
			if answer.lower().startswith("n"):
				config.write('\n')
				config.write("GROUP_FILENAME=collapsed.group.txt" + '\n')
				config.write("GFF_FILENAME=collapsed.gff" + '\n')
				config.write("COUNT_FILENAME=collapsed.abundance.txt" + '\n')
				config.close()
				subprocess.call("ls *.config", shell = True)
				time.sleep(2)
				break
			elif answer.lower().startswith("y"):
				sample = input("Enter the sample name and the path of the collapsed files in this format (SAMPLE=<sample name>;<path>):")
				config.write(sample + '\n')

#Check the path of input file
input_file2("sample.config")

#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)

sample_config = os.path.join(current_path, "sample.config")

chain = "chain_samples.py" + " " + sample_config + " " + "count_fl"
os.system(chain)

subprocess.call("ls all_samples.*", shell = True)
time.sleep(2)
