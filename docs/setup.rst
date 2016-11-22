.. _setup_label:

Setup the application
=====================

Now you are ready to load all your VCFs and start to analyze your data with myVCF

myVCF manage **annotated VCF** files that contain some mandatory fields in order to load and visualize them correctely.

To verify if your :code:`.vcf` file is compatible with myVCF, please read the following section

VCF fields and requirements
---------------------------

myVCF can read VCF files coming from **Annovar** of **VEP** annotation systems. Those softwares are the most common tool used for VCF annotation after the SNP call step.

.. Note::
  If you are not sure if your VCF file respect the mandatory field and requirements, try to load it by following the :ref:`Load new data section <load_vcf>`

Let's define which are the mandatory fields that a VCF must contains for myVCF tool

- Since myVCF is a tool fro browse and visualize mutations genotyped with NGS technology, the VCF file **must** contain at least 1 genotyped sample
See example below:

.. code-block:: shell

  ##contig=<ID=17,length=81195210,assembly=b37>
  ##contig=<ID=18,length=78077248,assembly=b37>
  ##contig=<ID=19,length=59128983,assembly=b37>
  ##contig=<ID=20,length=63025520,assembly=b37>
  ##contig=<ID=21,length=48129895,assembly=b37>
  ##contig=<ID=22,length=51304566,assembly=b37>
  ##contig=<ID=X,length=155270560,assembly=b37>
  ##contig=<ID=Y,length=59373566,assembly=b37>
  ##contig=<ID=MT,length=16569,assembly=b37>
  ##INFO=<ID=Func_ensGene,Number=.,Type=String,Description="Func_ensGene annotation provided by ANNOVAR">
  ##INFO=<ID=Gene_ensGene,Number=.,Type=String,Description="Gene_ensGene annotation provided by ANNOVAR">
  ##INFO=<ID=GeneDetail_ensGene,Number=.,Type=String,Description="GeneDetail_ensGene annotation provided by ANNOVAR">
  ##INFO=<ID=ExonicFunc_ensGene,Number=.,Type=String,Description="ExonicFunc_ensGene annotation provided by ANNOVAR">
  #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	Sample1
  1	762273	rs3115849	G	A	123.7	LowQual	AC=2;AF=1;AN=2;Func_ensGene=ncRNA_exonic;Gene_ensGene=ENSG00000225880;GeneDetail_ensGene=.;ExonicFunc_ensGene=.	GT:AD:DP:GQ:PL	1/1:0,63:63:99:1550,188,0

This is a VCF part in which we have 1 genotyped sample (Sample1) for one mutation.

- For **Annovar** annotated VCFs, the mandatory field within the file would be:

  1. Gene_ensGene
  2. ExonicFunc_ensGene

- For **VEP** annotated VCFs, the mandatory field within the file would be:

  1. CSQ

  This field is added by default during VEP annotation

.. Note::
  To verify the necessary fields for the annotation part, you should see in the HEADER part of the VCF those lines:

  .. code-block:: shell

    # Annovar fields
    ##INFO=<ID=Gene_ensGene,Number=.,Type=String,Description="Gene_ensGene annotation provided by ANNOVAR">
    ##INFO=<ID=ExonicFunc_ensGene,Number=.,Type=String,Description="ExonicFunc_ensGene annotation provided by ANNOVAR">

    # VEP: CSQ field
    ##INFO=<ID=CSQ,Number=.,Type=String,Description="Consequence annotations from Ensembl VEP. Format: Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|VARIANT_CLASS|SYMBOL_SOURCE|HGNC_ID|CANONICAL>

  or copy the VCF in :code:`myVCF/data/VCFs/` directory and try to load the VCF through the :ref:`Upload page <load_vcf>`

How to annotate your VCF
------------------------

If you don't have the genomic/transcript annotation for your VCF file, or the VCF is not suitable for myVCF please consider to annotate it using the following instructions.

-----------------------------------
How to install the annotation tools
-----------------------------------

Annovar
^^^^^^^

The installation of Annovar is very well-described on `ANNOVAR Manual pages <http://annovar.openbioinformatics.org/en/latest/user-guide/download/>`_

Since is a :code:`perl` script, the software can be run on diverse operating systems including Unix and Windows.

VEP
^^^

The installation of VEP is described on `VEP main page <http://www.ensembl.org/info/docs/tools/vep/index.html>`_

Please follow the instructions below to install the software based on your operating system.

**Unix (Ubuntu/Debian system)/MAC**

For UNIX/MAC users, there is available this `tutorial <http://www.ensembl.org/info/docs/tools/vep/script/vep_tutorial.html>`_ that describe the download and the installation step ina a very easy way.

**Windows**

Please follow this `instuctions <http://www.ensembl.org/info/docs/tools/vep/script/vep_download.html#windows>`_ to install and configure VEP for windows system.

.. Note:: The easiest way is the **Cygwin** installation procedure.

------------------------------
Launch the code for annotation
------------------------------

Here it is reported the *minimum code* to run for a correct annotation compatible with myVCF. The tutorial contains both the *Annovar* and *VEP* annotation procedure.

For **Windows users** please launch the commands using **Cygwin** downloaded in previous section or **CMD shell** (:ref:`find CMD <cmd_label>`)

Annovar
^^^^^^^

1. Download the ENSEMBL transcript reference database required for myVCF compatibility

.. code-block:: shell

  # Download the ensembl DB (example: hg19)
  # buildver = hg19/hg38 depending on what reference assembly you used during the read mapping
  table_annovar.pl -downdb -webfrom annovar -buildver hg19 ensGene

  ## Optional but useful annotation
  # dbSNP147
  table_annovar.pl -downdb -webfrom annovar -buildver hg19 avsnp147
  # dbnsfp30a - non-synonimous variants annotation compendium (it takes lot for download)
  #http://annovar.openbioinformatics.org/en/latest/user-guide/filter/#ljb42-dbnsfp-non-synonymous-variants-annotation
  table_annovar.pl -downdb -webfrom annovar -buildver hg19 dbnsfp30a

2. Launch the annotation process. The command line is based on  `Annovar tutorial <http://annovar.openbioinformatics.org/en/latest/user-guide/startup/#table_annovarpl>`_.

.. code-block:: shell

  # Launch the annotation
  table_annovar.pl example/ex2.vcf humandb/ -buildver hg19 -out myanno -remove -protocol ensGene,avsnp142,dbnsfp30a -operation g,f,f -nastring . -vcfinput

.. Note:: To download additional databases to enrich the annotation for your mutations, please see `this link <http://annovar.openbioinformatics.org/en/latest/user-guide/download/#additional-databases>`_ and modify the *Lunch the application* command line by adding the name of the database in :code:`-protocol` and an :code:`f` in :code:`-operation` for every database

VEP
^^^

Simplier than Annovar, once downloaded the tool and the human assembly containing the annotations, launch this command to annotate your vcf

.. code-block:: shell

  perl variant_effect_predictor.pl -i example.vcf --cache --force_overwrite --vcf -o example_VEP.vcf

At the end of the process you will have file named :code:`example_VEP.vcf` with all the information suitable for myVCF

.. _load_vcf:

Load new data
-------------

1. Copy/move the VCF files you want to load into the system in :code:`/path/to/myVCF/data/VCFs`
2. Launch the application (See how to :ref:`launch the app <launch_app>`) and load http://127.0.0.1:8000/ in your browser
3. Click on the **Upload new project** link in the myVCF homepage
4. Give a name to the project and select the VCF to load

.. figure:: img/myVCF_upload_page.png
   :scale: 50 %
   :alt: Upload page picture
   :align: center

   New project upload page example. :code:`mini_VEP.vcf` is the mutation file to upload into :code:`test` project using :code:`ENSEMBL75` as transcript reference.

.. Note:: If you don't find your VCF in the dropdown menu, please verify that you have copied the file into :code:`myVCF/data/VCFs` directory and restart the application

5. Click on submit button for saving the project

.. figure:: img/myVCF_saving.png
   :scale: 50 %
   :alt: Saving VCF..
   :align: center

   The storing process of very large VCF files (above 50 MB) will takes long time.

.. warning:: Don't panic if the saving process takes very long time. Do **NOT refresh** the page until the **Upload completed** page will be showed.
