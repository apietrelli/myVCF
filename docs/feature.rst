myVCF features
==============

myVCF is designed as a tool for browsing and visualizing mutational data coming from NGS technology, including Whole-Exome and -Genome sequencing as well as target resequencing.

Several features have been implemented to help the end user in the navigation and the exploration of his project. In the next paragraphs you will find the description of principal features available in myVCF.

How to query a project database?
--------------------------------

The search engine in myVCF is very versatile.
Once you are in a project homepage, you can query the database by searching for:

1. Gene name (Official Gene Symbol)
2. Genomic region
3. dbSNP ID
4. Variant

Gene view
^^^^^^^^^

Basic search. Fill the text box with the gene name you want to search and click **GO!**

.. figure:: img/myVCF_search_SAMD11.png
   :scale: 50 %
   :alt: search samd11
   :align: center

In the example image, we searched for :code:`SAMD11` gene. The system will put wildcards (:code:`*`) at the edges of the gene name automatically and search for :code:`*SAMD11*`.

Every gene that match the query search will be displayed in a table containing:

1. ENSEMBL Gene ID
2. Gene Symbol
3. Description of the gene function
4. Number of mutation in that gene found

To display the mutation list for :code:`SAMD11 - ENSG00000187634` just click on the **ENSEMBL Gene ID** link and you will be directed to the **SAMD11 gene page**

.. figure:: img/myVCF_results_SAMD11_part1.png
   :scale: 50 %
   :alt: search samd11
   :align: center

Variant view
^^^^^^^^^^^^

Variant view directly connected with principal population frequency database

.. Note:: Internet connection is needed to retrieve the frequency information

VCF metrics summary
-------------------

Click on ...
Cache will speed-up the process once is loaded for the first time.

- metric 1
- metric 2
- metric N

Change default columns view
---------------------------
