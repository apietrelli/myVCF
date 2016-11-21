.. _setup_label:

Setup the application
=====================

Now you are ready to load all your VCFs and start to analyze your data with myVCF

myVCF manage **annotated VCF** files that contain some mandatory fields in order to load and visualize them correctely.

To verify if your :code:`.vcf` file is compatible with myVCF, please read the following section

VCF fields and requirements
---------------------------

Basically myVCF read VCF files coming from **Annovar** of **VEP** systems. Those softwares are the most common tool used for VCF annotation after the SNP call step.

.. Note::
  If you are not sure if your VCF file respect the mandatory field and requirements, try to load it by following the :ref:`Load new data section <load_vcf>`

Let's definde which are the mandatory fields for myVCF tool

- The VCF file **must** contain at least 1 sample genotyped (IMG EXAMPLE)

- For **Annovar** annotated VCF the mandatory field within the file would be:

  1. EnsGene
  2. ExonicFunc_ensGene

- For **VEP** annotated VCF the mandatory field within the file would be:

  1. Gene

.. Note::
  To verify the fields necessary for the nnotation part, you should see in the HEADER part of the VCF those lines:
  (Example images)

How to annotate your VCF
------------------------

If you don't have the genomic/transcript annotation for your VCF file, or the VCF is not suitable for myVCF please consider to annotate it using the following instructions.

Annovar
^^^^^^^

VEP
^^^

**Windows**

Please follow this `instuctions <http://www.ensembl.org/info/docs/tools/vep/script/vep_download.html#windows>`_ to install and configure VEP for windows system.

.. Note:: The easiest way is the **Cygwin** installation procedure.

.. _load_vcf:

Load new data
-------------

Notes
-----
