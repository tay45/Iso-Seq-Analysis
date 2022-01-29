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
	while True:
		if os.path.isfile(path):
			return
		else:
			path = input("Doesn't exist. Enter the path again: ")

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

#Parameters
input_gtf = "collapsed.gtf"
abundance = "collapsed.abundance.tsv"
out_name = "out_sqanti"

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
out_dir = ""
out_dir = input("Enter the name of the 'output_directory'.: ")

#CPUs
cpus = ""
cpus = input("Enter the number of the cpus to use: ")

#Chaining samples
while True:
	answer = input("Do you have multiple Iso-Seq jobs to chain together?:")
	if answer.lower().startswith("n"):
		#print("***Running SQANTI***")
		time.sleep(2)
		break
	elif answer.lower().startswith("y"):
		#Chaining
		exec(open("chain.py").read())
		#Change the input file name
		subprocess.call("mv all_samples.chained_count.txt all_samples.chained_count.tsv", shell = True)
		#Convert gff to gtf
		input_file2("all_samples.chained.gff")
		current_path = os.path.abspath(os.getcwd())
		print(current_path)
		all_gff = os.path.join(current_path, "all_samples.chained.gff")
		out = os.path.join(current_path, "all_samples.chained.gtf")
		convert_gff = "gffread -T" + " " + all_gff + " -o" + " " + out
		os.system(convert_gff)
		subprocess.call("ls all_samples.chained.gtf", shell = True)
		time.sleep(2)
		#Change chained file names
		#Parameters
		input_gtf = "all_samples.chained.gtf"
		abundance = "all_samples.chained_count.tsv"
		out_name = "all_out_sqanti"
		#Fusion_Short Reads
		while True:
			answer = input("Is this for the fusion transcripts?:")
			if answer.lower().startswith("y"):
				answer = input("Do you want to provide Short-Read fastq files (fofn)?:")
				if answer.lower().startswith("y"):
					short_reads = ""
					short_reads = input("Enter the path of the 'short_reads.fastq (fofn)'.: ")
					input_file2(short_reads)
					print("***Running SQANTI***")
					sqanti3_qc_fusion_shortRead =  "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + out_dir + " -fl " + abundance + " --short_reads " + short_reads + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " --is_fusion" + " --report both"
					os.system(sqanti3_qc_fusion_shortRead)
					#subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)
					print("***Completing the process***")
					time.sleep(2)
					quit()
				elif answer.lower().startswith("n"):
					print("***Running SQANTI***")
					sqanti3_qc_fusion = "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + out_dir + " -fl " + abundance + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " -c " + coverage + " --is_fusion" + " --report both"
					os.system(sqanti3_qc_fusion)
					#subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)
					print("***Completing the process***")
					time.sleep(2)
					quit()
			elif answer.lower().startswith("n"):	
				while True:
					answer = input("Do you want to provide Short-Read fastq files (fofn)?:")
					if answer.lower().startswith("n"):
						print("***Running SQANTI***")
						time.sleep(2)
						#Run SQANTI3
						sqanti3_qc = "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + out_dir + " -fl " + abundance + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " -c " + coverage + " --report both"
						subprocess.run(sqanti3_qc, shell=True)
						print("***Completing the process***")
						time.sleep(2)
						#subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)
						quit()
					elif answer.lower().startswith("y"):
						short_reads = ""
						short_reads = input("Enter the path of the 'short_reads.fastq (fofn)'.: ")
						input_file2(short_reads)
						sqanti3_qc_shortRead =  "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + out_dir + " -fl " + abundance + " --short_reads " + short_reads + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " --report both"
						os.system(sqanti3_qc_shortRead)
						print("***Completing the process***")
						time.sleep(2)
						#subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)
						quit()

#Change the input file name
subprocess.call("mv collapsed.abundance.txt collapsed.abundance.tsv", shell = True)
input_file2("collapsed.abundance.tsv")

#Fusion_Short Reads
while True:
	answer = input("Is this for the fusion transcripts?:")
	if answer.lower().startswith("y"):
		answer = input("Do you want to provide Short-Read fastq files (fofn)?:")
		if answer.lower().startswith("y"):
			short_reads = ""
			short_reads = input("Enter the path of the 'short_reads.fastq (fofn)'.: ")
			input_file2(short_reads)
			print("***Running SQANTI***")
			sqanti3_qc_fusion_shortRead =  "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + out_dir + " -fl " + abundance + " --short_reads " + short_reads + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " --is_fusion" + " --report both"
			os.system(sqanti3_qc_fusion_shortRead)
			subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)
			print("***Completing the process***")
			time.sleep(2)
			quit()
		elif answer.lower().startswith("n"):
			print("***Running SQANTI***")
			sqanti3_qc_fusion = "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + out_dir + " -fl " + abundance + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " -c " + coverage + " --is_fusion" + " --report both"
			os.system(sqanti3_qc_fusion)
			subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)
			print("***Completing the process***")
			time.sleep(2)
			quit()
	elif answer.lower().startswith("n"):	
		break

#Short Reads
while True:
	answer = input("Do you want to provide Short-Read fastq files (fofn)?:")
	if answer.lower().startswith("n"):
		print("***Running SQANTI***")
		time.sleep(2)
		break
	elif answer.lower().startswith("y"):
		#splice_junction = ""
		#splice_junction = input("Enter the path of the 'SJ.out.tab'.: ")
		#input_file2(splice_junction)
		short_reads = ""
		short_reads = input("Enter the path of the 'short_reads.fastq (fofn)'.: ")
		input_file2(short_reads)
		sqanti3_qc_shortRead =  "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + out_dir + " -fl " + abundance + " --short_reads " + short_reads + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " --report both"
		os.system(sqanti3_qc_shortRead)
		print("***Completing the process***")
		time.sleep(2)
		subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)
		quit()

#Run SQANTI3
sqanti3_qc = "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + out_dir + " -fl " + abundance + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " -c " + coverage + " --report both"
subprocess.run(sqanti3_qc, shell=True)
print("***Completing the process***")
time.sleep(2)
subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)
quit()
			
