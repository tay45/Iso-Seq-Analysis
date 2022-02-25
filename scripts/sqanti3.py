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
#out_dir = ""
#out_dir = input("Enter the name of the 'output_directory'.: ")

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
		while True:
			answer = input("Do you want to provide Short-Read fastq files (fofn)?:")
			if answer.lower().startswith("n"):
				print("***Running SQANTI***")
				time.sleep(2)
				#Run SQANTI3
				sqanti3_qc = "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + "sqanti3_chain" + " -fl " + abundance + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " -c " + coverage + " --report both"
				subprocess.run(sqanti3_qc, shell=True)
				#Save chained file in chained_file folder
				#Current working directory
				current_path = os.path.abspath(os.getcwd())
				print(current_path)
				subprocess.call("mkdir chained_files", shell = True)
				subprocess.call("cp all_samples.* " + current_path + "/" + "chained_files", shell = True)
				
				#Run gtfToGenePred
				print("***Run gtfToGenePred***")
				time.sleep(2)
				input_file2("all_samples.chained.gtf")
				gtfToGenePred = "gtfToGenePred" + " " + "all_samples.chained.gtf" + " " + "all_samples.chained.genePred"
				os.system(gtfToGenePred)
				
				#Run genePredToBed
				print("***Run genePredToBed***")
				time.sleep(2)
				input_file2("all_samples.chained.genePred")
				genePredToBed = "genePredToBed" + " " + "all_samples.chained.genePred" + " " + "all_samples.chained.bed12"
				os.system(genePredToBed)
				
				#Run genePredToBed
				print("***Run color_bed12_post_sqanti.py***")
				time.sleep(2)
				#Current working directory
				current_path = os.path.abspath(os.getcwd())
				print(current_path)
				input_file2(current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_classification.txt")
				color_bed12 = "color_bed12_post_sqanti.py" + " " + current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_classification.txt" + " " + "all_samples.chained.bed12" + " " + "all_samples.chained.colored"
				os.system(color_bed12)
				subprocess.call("ls all_samples.*", shell = True)
				time.sleep(2)
				
				#Run IsoAnnot
				print("***Run IsoAnnot***")
				time.sleep(2)
				#Current working directory
				current_path = os.path.abspath(os.getcwd())
				print(current_path)
				#Check file locations
				input_file2(current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_corrected.gtf")
				input_file2(current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_classification.txt")
				input_file2(current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_junctions.txt")
				correct = current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_corrected.gtf"
				classification = current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_classification.txt"
				junctions = current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_junctions.txt"
				#Run IsoAnnot.py
				isoannot = color_bed12 = "python3 IsoAnnotLite_v2.7.0_SQ3.py" + " " + correct + " " + classification + " " + junctions + " " + "-gff3" + " " + tappAS + " " + "-novel -o" + " " + "isoannot" + " " + "-stdout" + " " + "isoannot.summaryResults"
				os.system(isoannot)
				subprocess.call("ls isoannot.*", shell = True)
				time.sleep(2)
				
				#Ask fusion analysis
				while True:
					answer = input("Do you want to analyze the fusion genes?:")
					if answer.lower().startswith("n"):
						print("***Completing the process***")
						time.sleep(2)
						quit()
					elif answer.lower().startswith("y"):	
						exec(open("fusion.py").read())
			elif answer.lower().startswith("y"):
				short_reads = ""
				short_reads = input("Enter the path of the 'short_reads.fastq (fofn)'.: ")
				input_file2(short_reads)
				sqanti3_qc_shortRead =  "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + "sqanti3_chain" + " -fl " + abundance + " --short_reads " + short_reads + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " --report both"
				os.system(sqanti3_qc_shortRead)
				#Save chained file in chained_file folder
				#Current working directory
				current_path = os.path.abspath(os.getcwd())
				print(current_path)
				subprocess.call("mkdir chained_files", shell = True)
				subprocess.call("cp all_samples.* " + current_path + "/" + "chained_files", shell = True)
				
				#Run gtfToGenePred
				print("***Run gtfToGenePred***")
				time.sleep(2)
				input_file2("all_samples.chained.gtf")
				gtfToGenePred = "gtfToGenePred" + " " + "all_samples.chained.gtf" + " " + "all_samples.chained.genePred"
				os.system(gtfToGenePred)

				#Run genePredToBed
				print("***Run genePredToBed***")
				time.sleep(2)
				input_file2("all_samples.chained.genePred")
				genePredToBed = "genePredToBed" + " " + "all_samples.chained.genePred" + " " + "all_samples.chained.bed12"
				os.system(genePredToBed)

				#Run genePredToBed
				print("***Run color_bed12_post_sqanti.py***")
				time.sleep(2)
				#Current working directory
				current_path = os.path.abspath(os.getcwd())
				print(current_path)
				input_file2(current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_classification.txt")
				color_bed12 = "color_bed12_post_sqanti.py" + " " + current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_classification.txt" + " " + "all_samples.chained.bed12" + " " + "all_samples.chained.colored"
				os.system(color_bed12)
				subprocess.call("ls all_samples.*", shell = True)
				time.sleep(2)
				
				#Run IsoAnnot
				print("***Run IsoAnnot***")
				time.sleep(2)
				#Current working directory
				current_path = os.path.abspath(os.getcwd())
				print(current_path)
				#Check file locations
				input_file2(current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_corrected.gtf")
				input_file2(current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_classification.txt")
				input_file2(current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_junctions.txt")
				correct = current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_corrected.gtf"
				classification = current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_classification.txt"
				junctions = current_path + "/" + "sqanti3_chain" + "/" + "all_out_sqanti_junctions.txt"
				#Run IsoAnnot.py
				isoannot = color_bed12 = "python3 IsoAnnotLite_v2.7.0_SQ3.py" + " " + correct + " " + classification + " " + junctions + " " + "-gff3" + " " + tappAS + " " + "-novel -o" + " " + "isoannot" + " " + "-stdout" + " " + "isoannot.summaryResults"
				os.system(isoannot)
				subprocess.call("ls isoannot.*", shell = True)
				time.sleep(2)
				
				while True:
					answer = input("Do you want to analyze the fusion genes?:")
					if answer.lower().startswith("n"):
						print("***Completing the process***")
						time.sleep(2)
						quit()
					elif answer.lower().startswith("y"):	
						exec(open("fusion.py").read())


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


#Change the input file name
subprocess.call("mv collapsed.abundance.txt collapsed.abundance.tsv", shell = True)
input_file2("collapsed.abundance.tsv")


#Short Reads
while True:
	answer = input("Do you want to provide Short-Read fastq files (fofn)?:")
	if answer.lower().startswith("n"):
		print("***Running SQANTI***")
		time.sleep(2)
		break
	elif answer.lower().startswith("y"):
		short_reads = ""
		short_reads = input("Enter the path of the 'short_reads.fastq (fofn)'.: ")
		input_file2(short_reads)
		sqanti3_qc_shortRead =  "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + "sqanti3" + " -fl " + abundance + " --short_reads " + short_reads + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " --report both"
		os.system(sqanti3_qc_shortRead)
		subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)
		
		#Run gtfToGenePred
		print("***Run gtfToGenePred***")
		time.sleep(2)
		input_file2("collapsed.gtf")
		gtfToGenePred = "gtfToGenePred" + " " + "collapsed.gtf" + " " + "collapsed.genePred"
		os.system(gtfToGenePred)

		#Run genePredToBed
		print("***Run genePredToBed***")
		time.sleep(2)
		input_file2("collapsed.genePred")
		genePredToBed = "genePredToBed" + " " + "collapsed.genePred" + " " + "collapsed.bed12"
		os.system(genePredToBed)

		#Run genePredToBed
		print("***Run color_bed12_post_sqanti.py***")
		time.sleep(2)
		#Current working directory
		current_path = os.path.abspath(os.getcwd())
		print(current_path)
		input_file2(current_path + "/" + "sqanti3" + "/" + "out_sqanti_classification.txt")
		color_bed12 = "color_bed12_post_sqanti.py" + " " + current_path + "/" + "sqanti3" + "/" + "out_sqanti_classification.txt" + " " + "collapsed.bed12" + " " + "collapsed.colored"
		os.system(color_bed12)
		subprocess.call("ls collapsed.*", shell = True)
		time.sleep(2)
		
		#Run IsoAnnot
		print("***Run IsoAnnot***")
		time.sleep(2)
		#Current working directory
		current_path = os.path.abspath(os.getcwd())
		print(current_path)
		#Check file locations
		input_file2(current_path + "/" + "sqanti3" + "/" + "out_sqanti_corrected.gtf")
		input_file2(current_path + "/" + "sqanti3" + "/" + "out_sqanti_classification.txt")
		input_file2(current_path + "/" + "sqanti3" + "/" + "out_sqanti_junctions.txt")
		correct = current_path + "/" + "sqanti3" + "/" + "out_sqanti_corrected.gtf"
		classification = current_path + "/" + "sqanti3" + "/" + "out_sqanti_classification.txt"
		junctions = current_path + "/" + "sqanti3" + "/" + "out_sqanti_junctions.txt"
		#Run IsoAnnot.py
		isoannot = color_bed12 = "python3 IsoAnnotLite_v2.7.0_SQ3.py" + " " + correct + " " + classification + " " + junctions + " " + "-gff3" + " " + tappAS + " " + "-novel -o" + " " + "isoannot" + " " + "-stdout" + " " + "isoannot.summaryResults"
		os.system(isoannot)
		subprocess.call("ls isoannot.*", shell = True)
		time.sleep(2)
		
		while True:
			answer = input("Do you want to analyze the fusion genes?:")
			if answer.lower().startswith("n"):
				print("***Completing the process***")
				time.sleep(2)
				quit()
			elif answer.lower().startswith("y"):	
				exec(open("fusion.py").read())


#Run SQANTI3
sqanti3_qc = "sqanti3_qc.py " + input_gtf + " " + annot_gtf + " " + ref_fasta + " --cage_peak " + cage_peak + " --polyA_peak " + polya_peak + " --polyA_motif_list " + polya_motif + " -o " + out_name + " -d " + "sqanti3" + " -fl " + abundance + " --cpus " + str(cpus) + " -n 10" + " --genename" + " --isoAnnotLite" + " --gff3 " + tappAS + " -c " + coverage + " --report both"
subprocess.run(sqanti3_qc, shell=True)
subprocess.call("mv collapsed.abundance.tsv collapsed.abundance.txt", shell = True)

#Run gtfToGenePred
print("***Run gtfToGenePred***")
time.sleep(2)
input_file2("collapsed.gtf")
gtfToGenePred = "gtfToGenePred" + " " + "collapsed.gtf" + " " + "collapsed.genePred"
os.system(gtfToGenePred)

#Run genePredToBed
print("***Run genePredToBed***")
time.sleep(2)
input_file2("collapsed.genePred")
genePredToBed = "genePredToBed" + " " + "collapsed.genePred" + " " + "collapsed.bed12"
os.system(genePredToBed)

#Run genePredToBed
print("***Run color_bed12_post_sqanti.py***")
time.sleep(2)
#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)
input_file2(current_path + "/" + "sqanti3" + "/" + "out_sqanti_classification.txt")
color_bed12 = "color_bed12_post_sqanti.py" + " " + current_path + "/" + "sqanti3" + "/" + "out_sqanti_classification.txt" + " " + "collapsed.bed12" + " " + "collapsed.colored"
os.system(color_bed12)
subprocess.call("ls collapsed.*", shell = True)
time.sleep(2)

#Run IsoAnnot
print("***Run IsoAnnot***")
time.sleep(2)
#Current working directory
current_path = os.path.abspath(os.getcwd())
print(current_path)
#Check file locations
input_file2(current_path + "/" + "sqanti3" + "/" + "out_sqanti_corrected.gtf")
input_file2(current_path + "/" + "sqanti3" + "/" + "out_sqanti_classification.txt")
input_file2(current_path + "/" + "sqanti3" + "/" + "out_sqanti_junctions.txt")
correct = current_path + "/" + "sqanti3" + "/" + "out_sqanti_corrected.gtf"
classification = current_path + "/" + "sqanti3" + "/" + "out_sqanti_classification.txt"
junctions = current_path + "/" + "sqanti3" + "/" + "out_sqanti_junctions.txt"
#Run IsoAnnot.py
isoannot = color_bed12 = "python3 IsoAnnotLite_v2.7.0_SQ3.py" + " " + correct + " " + classification + " " + junctions + " " + "-gff3" + " " + tappAS + " " + "-novel -o" + " " + "isoannot" + " " + "-stdout" + " " + "isoannot.summaryResults"
os.system(isoannot)
subprocess.call("ls isoannot.*", shell = True)
time.sleep(2)

while True:
	answer = input("Do you want to analyze the fusion genes?:")
	if answer.lower().startswith("n"):
		print("***Completing the process***")
		time.sleep(2)
		quit()
	elif answer.lower().startswith("y"):	
		exec(open("fusion.py").read())
			