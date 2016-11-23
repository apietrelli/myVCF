myVCF features
==============

myVCF is designed as a tool for browsing and visualizing mutational data coming from NGS technology, including Whole-Exome and -Genome sequencing as well as target resequencing.

Several features have been implemented to help the end user in the navigation and the exploration of his project. In the next paragraphs you will find the description of principal features available in myVCF.

How to query a project database?
--------------------------------

The search engine in myVCF is very versatile.
Once you are in a project homepage, you can query the database by searching for:

1. Gene name (Official Gene Symbol)
2. Genomic region (1:20000-200100)
3. dbSNP ID (rs324239)
4. Variant (1-456783-456783-A-T)

Gene/Region view
^^^^^^^^^^^^^^^^

Basic gene/region search will generate a **Gene page** composed by:

- **Table** containing the mutation found in the gene/region
- **Mutation plot** showing the distribution of the mutations grouped by their functional consequence.

Here is described a gene search example

Example for **SAMD11** gene query:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Fill the text box with :code:`SAMD11` region you want and click **GO!**

.. figure:: img/myVCF_search_SAMD11.png
   :scale: 50 %
   :alt: search samd11
   :align: center

We searched for :code:`SAMD11` gene. The system will put wildcards (:code:`*`) at the edges of the gene name automatically and search for :code:`*SAMD11*`.

To display the mutation list for :code:`SAMD11 - ENSG00000187634` just click on the **ENSEMBL Gene ID** link and you will be directed to the **SAMD11 gene page**

.. figure:: img/myVCF_results_SAMD11_part1.png
   :scale: 50 %
   :alt: search samd11
   :align: center

You can filter the mutations by using the buttons |filter_buttons|

.. |filter_buttons| image:: img/myVCF_results_filter_buttons.png


- **PASS Filter** - Only PASS mutations will be showed. This filter acts on :code:`FILTER` field in VCF file
- **MAF Threshold** - Only mutations with Allele Frequency (AF) lower than MAF selected will be selected. This filter acts on :code:`AF` field in VCF file.
- **Reset Filters** - Reset all filters. All mutation will be displayed

You can also modify the display element by

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
