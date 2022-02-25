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


#Change the input file name
subprocess.call("mv fusion.abundance.txt fusion.abundance.tsv", shell = True)
#input_file2("fusion.abundance.tsv")
		

#Parameters
input_gtf = "fusion.gtf"
abundance = "fusion.abundance.tsv"
out_name = "out_fusion_sqanti"


#Add annotation file
annot_gtf = ""
annot_gtf = input("Enter the path of the 'annotation_gtf'.: ")
input_file2(annot_gtf)

#Add reference
ref_fasta = ""
ref_fasta = input("Enter the path of the 'reference_fasta'.: ")
input_file2(ref_fasta)

#Add cage_peak file
cage_peak = ""
cage_peak = input("Enter the path of the 'CAGE_Peak_bed'.: ")
input_file2(cage_peak)

#Add polya_peak file
polya_peak = ""
polya_peak = input("Enter the path of the 'polyA_peak_bed'.: ")
input_file2(polya_peak)

#Add polya_motif file
polya_motif = ""
polya_motif = input("Enter the path of the 'polyA_motif_txt'.: ")
input_file2(polya_motif)

#Add tappAS-annotation file
tappAS = ""
tappAS = input("Enter the path of the 'tappAS-annotation_gff3'.: ")
input_file2(tappAS)

#Add short_coverage file
coverage = ""
coverage = input("Enter the path of the 'intropolis junction_bed'.: ")
input_file2(coverage)

#Output directory
#out_dir = ""
#out_dir = input("Enter the name of the 'output_directory'.: ")

#CPUs
cpus = ""
cpus = input("Enter the number of the cpus to use: ")


#Fusion_Short Reads
while True:
	answer = input("Do you want to provide Short-Read fastq files (fofn)?:")
	if answer.lower().startswith("y"):
		short_reads = ""
		short_reads = input("Enter the path of the 'short_reads.fastq (fofn)'.: ")
		input_file2(short_reads)
		print("***Running SQANTI***")
		sqanti3_qc_fusion_shortRead =  "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + "sqanti3_fusion" + " -fl " + abundance + " --short_reads " + short_reads + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " --is_fusion" + " --report both"
		os.system(sqanti3_qc_fusion_shortRead)
		subprocess.call("mv fusion.gff clustered.hq.fasta.sorted.sam.fusion.gff", shell = True)
		subprocess.call("mv fusion.abundance.tsv clustered.hq.fasta.sorted.sam.fusion.abundance.txt", shell = True)
		print("***Completing the process***")
		time.sleep(2)
		quit()
	elif answer.lower().startswith("n"):
		print("***Running SQANTI***")
		sqanti3_qc_fusion = "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + "sqanti3_fusion" + " -fl " + abundance + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " -c " + coverage + " --is_fusion" + " --report both"
		os.system(sqanti3_qc_fusion)
		subprocess.call("mv fusion.gff clustered.hq.fasta.sorted.sam.fusion.gff", shell = True)
		subprocess.call("mv fusion.abundance.tsv clustered.hq.fasta.sorted.sam.fusion.abundance.txt", shell = True)
		print("***Completing the process***")
		time.sleep(2)
		quit()