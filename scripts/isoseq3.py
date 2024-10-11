import argparse
import subprocess
import sys
import logging
import os
import resource
import glob

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(message)s',
                    handlers=[
                        logging.FileHandler("isoseq_pipeline.log"),
                        logging.StreamHandler(sys.stdout)
                    ])

# Run a command with logging for stdout and stderr
def run_command(command, description):
    logging.info(f"*** {description} ***")
    logging.info(f"Running command: {command}")
    
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        for stdout_line in iter(process.stdout.readline, ''):
            logging.info(stdout_line.strip())
        for stderr_line in iter(process.stderr.readline, ''):
            logging.error(stderr_line.strip())

        process.stdout.close()
        process.stderr.close()
        returncode = process.wait()

        if returncode != 0:
            logging.error(f"Command failed with exit code {returncode}")
            raise subprocess.CalledProcessError(returncode, command)
        logging.info(f"Finished {description} successfully")

    except subprocess.CalledProcessError as e:
        logging.error(f"Command {command} failed: {e}")
        sys.exit(1)

# Set explicit resource limits
def set_resource_limits():
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
        logging.info(f"Memory resource limit set to: {soft}")
    except ValueError as e:
        logging.error(f"Error setting resource limits: {e}")

# Function to rename BAM and PBI files, ignoring 'isoseq.unbarcoded.bam'
def rename_bam_and_pbi_files():
    logging.info("Looking for isoseq.*.bam file to rename, excluding 'isoseq.unbarcoded.bam'")

    # Use glob to find the BAM file matching the pattern
    bam_files = glob.glob("isoseq.*.bam")

    # Filter out 'isoseq.unbarcoded.bam'
    bam_files = [f for f in bam_files if 'isoseq.unbarcoded.bam' not in f]

    if not bam_files:
        logging.error("No BAM file found to rename, or only 'isoseq.unbarcoded.bam' was found.")
        sys.exit(1)

    # Assuming you want to rename the first valid match
    original_bam = bam_files[0]
    original_pbi = f"{original_bam}.pbi"  # Corresponding PBI file

    # Log file sizes before renaming
    logging.info(f"Original BAM file size: {os.path.getsize(original_bam)} bytes")

    # Rename the BAM file
    new_bam_name = "isoseq.lima.bam"
    try:
        logging.info(f"Renaming {original_bam} to {new_bam_name}")
        os.rename(original_bam, new_bam_name)
        logging.info(f"Successfully renamed {original_bam} to {new_bam_name}")
        
        # Rename the PBI file if it exists
        if os.path.exists(original_pbi):
            new_pbi_name = f"{new_bam_name}.pbi"
            logging.info(f"Renaming {original_pbi} to {new_pbi_name}")
            os.rename(original_pbi, new_pbi_name)
            logging.info(f"Successfully renamed {original_pbi} to {new_pbi_name}")
        else:
            logging.warning(f"No corresponding PBI file found for {original_bam}")
        
        # Log the size of the new BAM file
        logging.info(f"New BAM file size: {os.path.getsize(new_bam_name)} bytes")
        
        # Verify the original file was removed
        if os.path.exists(original_bam):
            logging.error(f"Original BAM file {original_bam} still exists. Removing manually.")
            os.remove(original_bam)
            logging.info(f"Successfully removed original BAM file {original_bam}")
        if os.path.exists(original_pbi):
            logging.error(f"Original PBI file {original_pbi} still exists. Removing manually.")
            os.remove(original_pbi)
            logging.info(f"Successfully removed original PBI file {original_pbi}")

    except OSError as e:
        logging.error(f"Error renaming BAM or PBI files: {e}")
        sys.exit(1)

# Define the function for skera split
def skera_split(consensusreadset, fragment_adapters, num_threads):
    logging.info("Starting skera split")
    
    output_bam = "segmented.consensusreadset.bam"  # Fixed output file name
    logging.info(f"Output BAM file will be: {output_bam}")
    
    skera_command = f"skera split --log-level INFO --log-file skera.log --alarms alarms.json -j {num_threads} \"{consensusreadset}\" \"{fragment_adapters}\" \"{output_bam}\""
    
    # Execute the skera split command
    run_command(skera_command, f"Running skera split with output to {output_bam}")
    
    return output_bam

# Function to run lima command
def lima(segmented_bam, cdna_primers, output_bam, num_threads):
    logging.info("Starting lima")
    
    lima_command = f"lima -j {num_threads} --log-level INFO --log-file lima-isoseq.log --isoseq --peek-guess --ignore-biosamples --overwrite-biosample-names --alarms alarms.json --dump-removed \"{segmented_bam}\" \"{cdna_primers}\" \"{output_bam}\""
    
    run_command(lima_command, f"Running lima with output to {output_bam}")
    
    return output_bam

# Function to run isoseq refine command
def isoseq_refine(isoseq_bam, cdna_barcodes, refined_bam, filter_summary, report_csv, num_threads):
    logging.info("Starting isoseq refine")
    
    refine_command = f"isoseq refine --log-level INFO -j {num_threads} --alarms alarms.json --require-polya \"{isoseq_bam}\" \"{cdna_barcodes}\" \"{refined_bam}\" \"{filter_summary}\" \"{report_csv}\""
    
    run_command(refine_command, f"Running isoseq refine with output to {refined_bam}")
    
    return refined_bam

# Function to run isoseq cluster2 command
def isoseq_cluster2(refined_bam, cluster2_bam, num_threads):
    logging.info("Starting isoseq cluster2")
    
    cluster2_command = f"isoseq cluster2 --alarms alarms.json --log-level INFO --log-file isoseq_cluster2.log -j {num_threads} \"{refined_bam}\" \"{cluster2_bam}\""
    
    run_command(cluster2_command, f"Running isoseq cluster2 with output to {cluster2_bam}")
    
    return cluster2_bam

# Function to run bam2fasta command
def bam2fasta(clustered_bam):
    logging.info("Starting bam2fasta")
    
    bam2fasta_command = f"bam2fasta --num-threads 7 --alarms alarms.json --allow-exceptions-passthrough --with-biosample-prefix -u --output isoseq.lima.refine.cluster2 {clustered_bam}"
    
    run_command(bam2fasta_command, f"Running bam2fasta with output to isoseq.lima.refine.cluster2")
    
    return "isoseq.lima.refine.cluster2"

# Function to run pbmm2 align command
def pbmm2_align(reference_fasta, clustered_bam):
    logging.info("Starting pbmm2 align")
    
    pbmm2_command = f"pbmm2 align {reference_fasta} {clustered_bam} isoseq.lima.refine.cluster2.mapped.bam --sort --min-gap-comp-id-perc 95.0 --min-length 50 --sample \"\" --report-json mapping_stats.report.json --preset ISOSEQ -j 7 --log-level DEBUG --log-file pbmm2.log --alarms alarms.json"
    
    run_command(pbmm2_command, f"Running pbmm2 align with reference {reference_fasta} and output to isoseq.lima.refine.cluster2.mapped.bam")
    
    return "isoseq.lima.refine.cluster2.mapped.bam"

# Function to run isoseq collapse command
def isoseq_collapse(mapped_bam):
    logging.info("Starting isoseq collapse")
    
    collapse_command = f"isoseq collapse --log-level INFO --alarms alarms.json -j 7 --do-not-collapse-extra-5exons --min-aln-coverage 0.99 --min-aln-identity 0.95 --max-fuzzy-junction 5 {mapped_bam} isoseq.lima.refine.cluster2.mapped.collapse_isoforms.gff"
    
    run_command(collapse_command, f"Running isoseq collapse with output to isoseq.lima.refine.cluster2.mapped.collapse_isoforms.gff")
    
    return "isoseq.lima.refine.cluster2.mapped.collapse_isoforms.gff"

# Function to run pigeon prepare command
def pigeon_prepare(collapse_gff, annotation_gtf, reference_fasta):
    logging.info("Starting pigeon prepare")
    
    pigeon_command = f"pigeon prepare --log-level INFO --log-file pigeon_prepare.log {collapse_gff} {annotation_gtf} {reference_fasta}"
    
    run_command(pigeon_command, f"Running pigeon prepare with output for collapse_gff: {collapse_gff}")
    
    return

# Function to run pigeon classify command
def pigeon_classify(collapse_gff, annotation_gtf, reference_fasta):
    logging.info("Starting pigeon classify")
    
    # Add the '.sorted' suffix to the GTF file
    annotation_gtf_sorted = annotation_gtf.replace('.gtf', '.sorted.gtf')
    
    # Fix the GFF file name to the sorted version
    collapse_gff_sorted = "isoseq.lima.refine.cluster2.mapped.collapse_isoforms.sorted.gff"
    
    classify_command = f"pigeon classify --log-level INFO --log-file pigeon-classify.log -j 7 --out-dir . --out-prefix isoseq_classify --flnc isoseq.lima.refine.cluster2.mapped.collapse_isoforms.flnc_count.txt {collapse_gff_sorted} {annotation_gtf_sorted} {reference_fasta}"
    
    run_command(classify_command, f"Running pigeon classify with collapse_gff: {collapse_gff_sorted} and sorted GTF: {annotation_gtf_sorted}")
    
    return

# Function to run pigeon filter command
def pigeon_filter():
    logging.info("Starting pigeon filter")
    
    # The fixed input files for pigeon filter
    isoforms_gff = "isoseq.lima.refine.cluster2.mapped.collapse_isoforms.sorted.gff"
    classification_txt = "isoseq_classify_classification.txt"
    
    # Command for pigeon filter
    filter_command = f"pigeon filter --log-level INFO --log-file pigeon-filter.log --isoforms {isoforms_gff} {classification_txt}"
    
    # Execute the pigeon filter command
    run_command(filter_command, f"Running pigeon filter with isoforms GFF: {isoforms_gff} and classification: {classification_txt}")
    
    return

# Function to run pigeon report command
def pigeon_report():
    logging.info("Starting pigeon report")
    
    # The fixed input files for pigeon report
    filtered_classification_txt = "isoseq_classify_classification.filtered_lite_classification.txt"
    saturation_txt = "isoseq_saturation.txt"
    
    # Command for pigeon report
    report_command = f"pigeon report --log-level INFO --log-file pigeon-report.log {filtered_classification_txt} {saturation_txt}"
    
    # Execute the pigeon report command
    run_command(report_command, f"Running pigeon report with filtered classification: {filtered_classification_txt} and saturation report: {saturation_txt}")
    
    return

# Main function for argument parsing and execution
def main():
    parser = argparse.ArgumentParser(description="Run skera split, lima, isoseq refine, pbmm2 align, pigeon prepare, and pigeon classify")

    # Define the command-line arguments for skera split, lima, isoseq refine, pbmm2 align, pigeon prepare, and pigeon classify
    parser.add_argument("-c", "--consensusreadset", required=True, help="Path to the consensus read set BAM file")
    parser.add_argument("-fa", "--fragment_adapters", required=False, help="Path to the fragment adapters FASTA file (optional; skera split will be skipped if not provided)")
    parser.add_argument("-bc", "--cdna_primers", required=True, help="Path to the cDNA primers FASTA file for lima and isoseq refine")
    parser.add_argument("-ref", "--reference_fasta", required=True, help="Path to the reference FASTA file for pbmm2 alignment")
    parser.add_argument("-gtf", "--annotation_gtf", required=True, help="Path to the annotation GTF file for pigeon prepare and pigeon classify")
    parser.add_argument("-j", "--num_threads", required=False, default=7, type=int, help="Number of threads to use (default is 7)")

    # Parse arguments
    args = parser.parse_args()

    # Set resource limits
    set_resource_limits()

    # Check if fragment adapters were provided
    if args.fragment_adapters:
        # Step 1: Run skera split if fragment adapters are provided
        segmented_bam = skera_split(args.consensusreadset, args.fragment_adapters, args.num_threads)
    else:
        # If no fragment adapters, skip skera split and use the consensus read set BAM file
        segmented_bam = args.consensusreadset

    # Step 2: Run lima and generate the output BAM file
    isoseq_bam = lima(segmented_bam, args.cdna_primers, "isoseq.bam", args.num_threads)

    # Step 3: Rename the BAM and PBI files to isoseq.lima.bam and isoseq.lima.bam.pbi, excluding 'isoseq.unbarcoded.bam'
    rename_bam_and_pbi_files()

    # Step 4: Run isoseq refine
    refined_bam = isoseq_refine("isoseq.lima.bam", args.cdna_primers, "isoseq.lima.refine.bam", "lima.refine.filter_summary.json", "lima.refine.report.csv", args.num_threads)

    # Step 5: Run isoseq cluster2
    cluster2_bam = isoseq_cluster2("isoseq.lima.refine.bam", "isoseq.lima.refine.cluster2.bam", args.num_threads)

    # Step 6: Run bam2fasta
    bam2fasta(cluster2_bam)

    # Step 7: Run pbmm2 align with reference FASTA
    mapped_bam = pbmm2_align(args.reference_fasta, cluster2_bam)

    # Step 8: Run isoseq collapse
    collapse_gff = isoseq_collapse(mapped_bam)

    # Step 9: Run pigeon prepare with annotation GTF
    pigeon_prepare(collapse_gff, args.annotation_gtf, args.reference_fasta)

    # Step 10: Run pigeon classify with sorted GTF
    pigeon_classify(collapse_gff, args.annotation_gtf, args.reference_fasta)

    # Step 11: Run pigeon filter
    pigeon_filter()

    # Step 12: Run pigeon report
    pigeon_report()

    logging.info(f"Pipeline completed successfully with outputs: segmented BAM: {segmented_bam}, renamed IsoSeq BAM: {isoseq_bam}, refined BAM: {refined_bam}, clustered BAM: {cluster2_bam}, mapped BAM: {mapped_bam}, collapse GFF: {collapse_gff}")

if __name__ == "__main__":
    main()
