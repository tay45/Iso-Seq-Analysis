Iso-Seq Analysis Pipeline

This pipeline consists of the command lines based on the PacBio IsoSeq3 (https://github.com/PacificBiosciences/IsoSeq), SQANTI3 (https://github.com/ConesaLab/SQANTI3) and the tools of the cDNA_Cupcake https://github.com/Magdoll/cDNA_Cupcake) for more conveniently analyzing the Iso-Seq dataset of the PacBio.

It is designed for executing in the Apollo server (apollo-acc.coh.org) of the City of Hope using the interactive job mode (http://apollo.coh.org/user-guide/interactivejobs/). The modules must be loaded in advance to the server.

- module load smrtlink/10.1
- module load cDNA_Cupcake
- module load SQANTI3
- module load gffread/0.12.7

To execute the pipeline, the below files should be in the same running folder.

- Python scripts (isoseq3.py, sqanti3.py, chain.py, fusion.py and chain_fusion.py)
- Raw read file (ccs.bam) including the corresponding index file (ccs.bam.pbi) 

And, please run below command in the shell. 

- python3 isoseq3.py -c ccs.bam -p primer.fasta -o fl.bam -pf primer.fasta

The input must be HiFi reads (ccs.bam; QV>20). If the raw data is the continuous long reads (CLRs) in movieX.subreads.bam, please produce the ccs.bam via the below command to generate the correct input. 

- ccs movieX.subreads.bam movieX.ccs.bam --min-rq 0.9

The 'supporting_files' folder (/net/isi-dcnl/ifs/user_data/Seq/PacBio/thkang/Pipelines/IsoSeq3_Sqanti3/supporting_files) contains the files requiring for the SQANTI3 execution. If you need a more information regarding the files, please refer to the instruction of the SQANTI3 (https://github.com/ConesaLab/SQANTI3/wiki/Running-SQANTI3-Quality-Control).

- Genome reference (.fasta) 
- Annotation (.gtf)
- CAGE Peak (.bed)
- polyA_motif (.txt)

The 'fusion.py' and 'chain_fusion.py' can be used after completing the process of the 'isoseq3.py'. But, these are not supported by Python3. Please replace the Python3 with the Python2 in the same shell before executing the scripts.

- module load Python/2.7.14
- python fusion.py

For executing this pipeline in other platforms, please satisfy the prerequisite through installing below tools.

- IsoSeq3 (https://github.com/PacificBiosciences/IsoSeq)
- SQANTI3 and cDNA_Cupcake (https://github.com/ConesaLab/SQANTI3/wiki/SQANTI3-dependencies-and-installation)
- gffread (https://anaconda.org/bioconda/gffread)  
