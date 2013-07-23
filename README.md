![Genie Avatar](https://raw.github.com/robinandeer/Genie/develop/assets/genie_logo.png)

## Genie: A Genomics Database Downloader
Genie simplifies connecting to and downloading various genomics resources from
around the web.

Currently supported FTP servers include:
* Ensembl
* NCBI
* GATK
* UCSC

To integrate the package into your existing pipe line you should take a look at
the CLI.

## More details
The idea is not to provide a completely generalized solution since the different
servers provide very different folder structures. Instead it will be incouraged
to write your very own ftp hooks to expand functionality.

## Documentation

### CLI

Usage: `genie.py [-f] [-s server] [-q query] [-d destination] [-n file_name]`

| Option                | Explanation                                 |
| --------------------- | ------------------------------------------- |
| `-s`, `--server`      | The name of the server; NCBI, Ensembl etc.  |
| `-q`, `--query`       | The keyword for the file file to download.  |
| `-d`, `--destination` | The destination folder to store downloaded file in. |
| `-n`, `--file_name`   | What to name the downloaded file.           |
| `-f`, `--force`       | Enable overwrite mode.                      |

Example:
```bash
  python genie.py -s Ensembl -q gtf -d ~/Desktop -n Homo_sapiens.gtf.gz
```

**User information**
For anonymous FTP access, the servers will often accept your email adress as
either username or password. This is a *required* option.

```bash
	python update_databases.py -email "ptanderson@magnolia.org"
```

**Ensembl**
The only supported file from Ensembl is the reference genome sequence in FASTA
format. Chromosome IDs are prepended with "chr".

**NCBI (CCDS)**
The only supported file from the NCBI servers is the fantastic and
[CCDS](http://www.ncbi.nlm.nih.gov/CCDS/CcdsBrowse.cgi) (Consensus CDS project)
that aims to provide a "core set of human and mouse protein coding regions that
are consistently annotated and of high quality." They have their own release
numbering system based on the NCBI release ID following the format
"Hs[NCBI release].[version]". However, the actual file is named according to
the Ensembl genome assembly that the database is based on: e.g. "GRCh37.69".
The default is to fetch the latest release of the database.

**UCSC**
The second source for getting the reference human genome sequence in FASTA
format. The main difference seems to be in the mitochondrial DNA sequence and
the fact that, compared to Ensemble, UCSC doesn't prepend "chr" to the
chromosome IDs. The assembly option is not as detailed as for Ensembl and of the
format "hg[assembly number]".

**GATK**
GATK provides a number of valuable files that they recommend be used as input
for running the GATK software.

* 1000G_phase1.indels.{}.vcf => 1000g_indels
* Mills_and_1000G_gold_standard.indels.{}.vcf => mills
* dbsnp_137.{}.vcf => dbsnp
* hapmap_3.3.{}.vcf => hapmap
* 1000G_omni2.5.{}.vcf => 1000g
* dbsnp_137.{}.excluding_sites_after_129.vcf => dnsnp_ex

The files have made up short codes that allow for simple input in a bash script.
There are a couple of other options as well such like the GATK version and which
assembly "GRCh37/hg19" to use. The default is either the latest and the "hg19"
genome assembly. Really the only options for assembly is "hg18-19" and
"GRCh36-37" (no versions).

**Force**
It can sometimes be handy to force overwriting existing files when scripts
behave irrationally. By providing the option "-f" the script will not worry
about what files are already in your reference directory and simply overwrite
any files you specify for download. At this point it's not possible to gain
more fine grain control of which files should be forced to download.

**Future updates**
* Because of the sequential nature of the script, updating multiple databases at
once will take unnesesarily long. Although not a priority at this point,
multithreading is an interesting improvement in a future release.

* The Ensembl folder structre has evolved over the years and the script is only
compatible with the current folder structure.