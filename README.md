#Genie
=====

Genomics database updater

__Currently supports the following Homo sapiens databases__:
* Ensembl reference genomic sequence ("Homo_sapiens.GRCh37.70_chr.fasta")
* UCSC reference genomic sequence ("Homo_sapiens.hg19_nochr.fasta")
* Several GATK provided files
** 1000G_phase1.indels.{}.vcf
** Mills_and_1000G_gold_standard.indels.{}.vcf
** dbsnp_137.{}.vcf
** hapmap_3.3.{}.vcf
** 1000G_omni2.5.{}.vcf
** dbsnp_137.{}.excluding_sites_after_129.vcf
* The CCDS curated and non-redundant database from NCBI ("CCDS.{}_nochr.txt")

The main script is callabe from the terminal and the user requests which files to be checked and potentially updated/download.
