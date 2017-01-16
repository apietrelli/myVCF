# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models
import datetime
from django.utils import timezone

class Gene75(models.Model):
    # Classe per il DB dei geni ENSEMBL
    # Creata a mano dal file /home/likewise-open/INGMAD/pietrelli/Data2/Public/ENSEMBL_Gene_v75_homo_sapiens_b37.txt
    ensgene = models.TextField(db_column='Ensgene_ID', blank=False, null=False)
    genename = models.TextField(db_column='Gene_name', blank=True)
    description = models.TextField(db_column='Description', blank=True)

    def __unicode__(self):
        return self.ensgene

class Gene84(models.Model):
    # Classe per il DB dei geni ENSEMBL
    # Creata a mano dal file /home/likewise-open/INGMAD/pietrelli/Data2/Public/ENSEMBL_Gene_v84_homo_sapiens_b38.txt
    ensgene = models.TextField(db_column='Ensgene_ID', blank=False, null=False)
    genename = models.TextField(db_column='Gene_name', blank=True)
    description = models.TextField(db_column='Description', blank=True)

    def __unicode__(self):
        return self.ensgene

class Log(models.Model):
    # Classe per la registrazione delle modifiche effettuate alla vcfdb APP
    log_text = models.TextField()
    log_date = models.DateTimeField('log modified')

    def __unicode__(self):
        return self.log_text

    def was_modified_recently(self):
        return self.log_date >= timezone.now() - datetime.timedelta(days=3)

    def log_date_human(self):
        return self.log_date.strftime('%d %B %Y')

    def is_recent(self):
        is_recent_var = self.log_date >= timezone.now() - datetime.timedelta(days=3)
        return is_recent_var

    was_modified_recently.admin_order_field = 'log_date'
    was_modified_recently.boolean = True
    was_modified_recently.short_description = 'Modified recently?'

class DbInfo(models.Model):
    # Classe per le informazioni sul DB
    project_name = models.TextField()
    sw_annotation = models.TextField()
    gene_annotation = models.TextField()
    assembly_version = models.TextField()
    samples = models.TextField()
    samples_len = models.IntegerField()
    default_col = models.TextField()
    mutation_col = models.TextField()

    def __unicode__(self):
        return self.project_name

    def annotation_type(self):
        return self.gene_annotation

    def annotation_sw(self):
        return self.sw_annotation

    def get_samples(self):
        return self.samples

    def n_samples(self):
        return self.samples_len

    def default_col_list(self):
        return self.default_col

    def get_mutation_col(self):
        return self.mutation_col

