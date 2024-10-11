# Iso-Seq Analysis Pipeline

This pipeline is designed for processing PacBio Iso-Seq data, including both conventional and Kinnex full-length bulk Iso-Seq analyses. It integrates PacBio IsoSeq3 v4.1.2 (part of SMRT Link tools v13.1), SQANTI3 v5.2.2 (SQANTI3 GitHub), and cDNA_Cupcake v28.0.0 (cDNA_Cupcake GitHub) to provide an end-to-end solution for Iso-Seq data analysis. This pipeline aims to simplify Iso-Seq analysis for users with little to no prior experience, requiring just two command lines and a configuration file. The configuration file includes helpful comments to guide users in selecting the appropriate analysis steps.

## Environment Setup
The pipeline is designed to run on the Apollo server (apollo-acc.coh.org) at City of Hope (Duarte, CA) in both batch and interactive job modes. For detailed information on the server, visit HPRCC.

Before running the analysis, ensure the following modules are loaded:

module load smrtlink/13.1

module load samtools

module load cDNA_Cupcake

module load SQANTI3/5.2.2

## Running the Pipeline

### 1. Preparing the Files
Download the following files to your working directory:

isoseq3.py

sqanti3.py

chain_fusion.py

config.yaml

Edit the config.yaml file to specify the required and optional arguments based on your analysis needs.

### 2. Executing the Iso-Seq3 Pipeline
Run the following command to execute the Iso-Seq3 pipeline:

python isoseq3.py \
-c raw.hifi.bam \
-fa fragment_adapters.fasta \
-bc cDNA_primers.fasta \
-ref ref.fasta \
-gtf annot.gtf \
-j <number of threads>

The input must be HiFi reads (ccs.bam, QV > 20).
For continuous long reads (CLR) (movieX.subreads.bam), generate ccs.bam using the following command:

ccs movieX.subreads.bam movieX.ccs.bam --min-rq 0.9

If you omit the -fa argument, the pipeline will skip the skera_split step, which is intended for fragmenting Kinnex concatenated reads. This is applicable for conventional bulk Iso-Seq analysis.

### 3. Executing the SQANTI3 Pipeline
To run the SQANTI3 pipeline with machine learning (ML) filtering and rescue:

python sqanti3.py

#### Note: This pipeline only includes the ML-based filter and rescue functionality. For rule-based filtering and rescue, refer to the official SQANTI3 documentation:

'https://github.com/ConesaLab/SQANTI3/wiki/Running-SQANTI3-filter'

'https://github.com/ConesaLab/SQANTI3/wiki/Running-SQANTI3-rescue'

### Supporting Files
The supporting_files directory (located at /nfs-irwrsrchnas01/labs/Seq/PacBio/thkang/Pipelines/IsoSeq3_Sqanti3/supporting_files) contains essential files for SQANTI3 execution. For more details, refer to the SQANTI3 Wiki.

#### Supporting Files:

Genome Reference: GRCh38.p12.genome.fa, hg38.fa

Annotation: gencode.v30.chr_patch_hapl_scaff.annotation.gtf, gencode.v30.annotation.gtf

CAGE Peak: hg38.cage_peak_phase1and2combined_coord.bed

PolyA Peak: atlas.clusters.2.0.GRCh38.96.bed

PolyA Motif: mouse_and_human.polyA_motif.txt

tappAS Annotation: Homo_sapiens_GRCh38_Ensembl_86.gff3, Homo_sapiens_GRCh38_RefSeq_78.gff3

Intropolis Junction BED: intropolis.v1.hg19_with_liftover_to_hg38.tsv.min_count_10.modified

## Installation for Other Platforms
To run this pipeline on platforms other than Apollo, install the following tools:

IsoSeq3 (https://github.com/PacificBiosciences/IsoSeq)

cDNA_Cupcake (https://github.com/Magdoll/cDNA_Cupcake)

SQANTI3 (https://github.com/ConesaLab/SQANTI3)
