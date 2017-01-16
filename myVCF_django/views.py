__author__ = 'pietrelli'

## Main views for myVCF site

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.apps import apps
import json
import re
import os
from subprocess import check_output
import vcf

import sqlite3
from vcfdb.base_models import DbInfo

app_label = "vcfdb"
## DB containing mutations
project_db = "projects"

def main_page(request):
    db_list = DbInfo.objects.values("project_name",
                                    "gene_annotation",
                                    "sw_annotation",
                                    "assembly_version",
                                    "samples",
                                    "samples_len")
    context = {'db_list': db_list}
    return render(request, 'base_site.html', context)


def upload_project(request):
    context = {}
    return render(request, 'upload.html', context)


def check_project_name(request):
    project_name = request.POST['project_name']
    # __iexact is case-insensitive
    res = DbInfo.objects.filter(project_name__iexact=project_name).exists()
    if res:
        context = json.dumps({'valid': False})
    else:
        context = json.dumps({'valid': True})
    return HttpResponse(context)


#
# delete_db:
#
def delete_db(request):
    # AJAX request
    project_name = request.POST['project_name']
    # get the model
    model = apps.get_model(app_label=app_label,
                           model_name=project_name)

    # Delete data
    model.objects.using(project_db).all().delete()

    # Delete table
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    database = os.path.join(base_dir, "data/db/projects_DB.sqlite3")
    conn = sqlite3.connect(database)
    c = conn.cursor()
    table_name = model._meta.db_table
    sql = "DROP TABLE %s;" % (table_name)
    c.execute(sql)

    # Restore projects_DB.sqlite3 size
    sql = "VACUUM;"
    c.execute(sql)
    conn.close()

    # Delete the link in home page
    db = DbInfo.objects.get(project_name=project_name)
    db.delete()

    msg_validate = "Project deleted"

    context = json.dumps({'project_name': project_name,
                          'msg_validate': msg_validate})
    return HttpResponse(context)

#
# select_vcf: Comment
#
def select_vcf(request):
    # path = request.POST['static_path']
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vcf_dir = os.path.join(base_dir, "data/VCFs")
    files = os.listdir(vcf_dir)
    context = json.dumps({'vcf_dir': vcf_dir,
                          'files': files})
    return HttpResponse(context)


#
# preprocessing_vcf: Comment
#
def preprocessing_vcf(request):
    ## Path doesn't works because it not reads relative path on static
    ## path = request.POST['static_path']
    ##
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vcf_dir = os.path.join(base_dir, "data/VCFs")
    vcf_name = request.POST['vcf_name']

    vcf_file = os.path.join(vcf_dir, vcf_name)

    def validate_vcf(vcf_file):
        import vcf
        valid = False
        annotation = None
        annovar_field = "Gene_ensGene"
        annovar_exonic_field = "ExonicFunc_ensGene"
        annovar_genesymbol_field = "Gene_refGene"
        vep_field = "CSQ"

        # Check if is a VCF file
        try:
            vcf_handler = vcf.Reader(open(vcf_file, 'r'))
        except:
            msg = "Does not seem a VCF file..."
            return valid, msg, annotation

        # Check if contains INFO fields
        if vcf_handler.infos.keys() == []:
            msg = "This VCF does not contain INFO fields..."
            return valid, msg, annotation

        # Check if contains at least 1 sample
        elif len(vcf_handler.samples) == 0:
            msg = "This VCF does not contain ANY sample genotype..."
            return valid, msg, annotation

        # Check if the VCF has been annotatod with supported software:
        # Annovar = Gene_ensGene field
        # Annovar exonic annotation = ExonicFunc_ensGene
        # VEP = CSQ field
        elif ( (annovar_field or annovar_exonic_field or annovar_genesymbol_field) not in vcf_handler.infos.keys()) and (vep_field not in vcf_handler.infos.keys()):
            msg = "This VCF is not annotated with Annovar or VEP software<br>" \
                  "Please follow the manual to make a VCF suitable for myVCF!!"
            return valid, msg, annotation

        else:
            if annovar_field in vcf_handler.infos.keys():
                annotation="annovar"
            if vep_field in vcf_handler.infos.keys():
                annotation="vep"

        valid = True
        msg = "OK!"
        return valid, msg, annotation


    valid, msg_validate, annotation = validate_vcf(vcf_file)

    context = json.dumps({'annotation' : annotation,
                          'msg_validate': msg_validate,
                          'valid': valid})
    return HttpResponse(context)


#
# submit_vcf: Parse VCF file and store into projects DB
#

def submit_vcf(request):
    import sqlite3

    def generateTableFromVCF_VEP(vcf_handler, database, project_name):

        def readCSQ_header(CSQ_info):
            if "desc" in CSQ_info._fields:
                # print CSQ_info.desc
                CSQ_fields = CSQ_info.desc.split("Format: ")[1].split("|")
                return CSQ_fields
            else:
                return """CSQ format is not well-defined!\nFIELD INFORMATION MISSING"""

        table_name = ""
        table_type = ""

        Drop_query = "DROP TABLE IF EXISTS " + project_name + ";"
        DefaultStatement = "CREATE TABLE " + project_name + "(ID INT PRIMARY KEY NOT NULL, CHROM TEXT NOT NULL, POS INT NOT NULL, RS_ID TEXT, REF TEXT NOT NULL, ALT TEXT, QUAL REAL, FILTER TEXT, "
        CSQ_Statement = ""
        CSQ_Statement_Flag = 0
        INFO_Statement = ""
        TableIndex = []

        # print vcf_handler.infos.keys()
        for id in vcf_handler.infos.keys():
            if vcf_handler.infos[id][2] == "String":
                table_type = "TEXT"
            elif vcf_handler.infos[id][2] == "Float":
                table_type = "REAL"
            elif vcf_handler.infos[id][2] == "Integer":
                table_type = "INTEGER"
            else:
                table_type = "TEXT"
            # print vcf_handler.infos[id][0]

            if vcf_handler.infos[id][0][0].isdigit():
                table_name = '"u' + vcf_handler.infos[id][0] + '"'
            elif vcf_handler.infos[id][0].startswith("GERP"):
                table_name = '"GERP_RS"'
            elif vcf_handler.infos[id][0].startswith("CSQ"):
                # print "CSQ point"
                CSQ_Statement_Flag = 1
                CSQ_fields = readCSQ_header(vcf_handler.infos[id])
                for field in CSQ_fields:
                    # print field
                    if field in TableIndex:
                        # print TableIndex
                        print "Jump " + table_name + " because was found DUPLICATED!"
                    else:
                        CSQ_Statement += '"' + field + '" ' + "TEXT" + ", "

            else:
                table_name = vcf_handler.infos[id][0]

            if CSQ_Statement_Flag:
                # print CSQ_Statement
                INFO_Statement = CSQ_Statement
                CSQ_Statement_Flag = 0
            else:
                INFO_Statement = '"' + table_name + '" ' + table_type + ", "

            # INFO_Statement += table_name + " " + table_type + ", "
            TableIndex.append(table_name)
            DefaultStatement = DefaultStatement + INFO_Statement

        # Samples columns
        SampleStatement = ""
        for sample in range(len(vcf_handler.samples)):
            SampleStatement += '"' + vcf_handler.samples[sample] + '"' + " TEXT, "
            TableIndex.append(vcf_handler.samples[sample])
        query = DefaultStatement + SampleStatement[:-2] + ");"

        # Debug
        # print query
        # print TableIndex
        # end debug

        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(Drop_query)
        c.execute(query)
        conn.commit()
        c.close()

        return 0

    def generateTableFromVCF_annovar(vcf_handler, database, project_name):
        import vcf
        import collections
        import sqlite3

        table_name = ""
        table_type = ""

        Drop_query = "DROP TABLE IF EXISTS " + project_name + ";"
        DefaultStatement = "CREATE TABLE " + project_name + "(ID INT PRIMARY KEY NOT NULL, CHROM TEXT NOT NULL, POS INT NOT NULL, RS_ID TEXT, REF TEXT NOT NULL, ALT TEXT, QUAL REAL, FILTER TEXT, "
        TableIndex = []

        for id in vcf_handler.infos.keys():
            if vcf_handler.infos[id][2] == "String":
                table_type = "TEXT"
            elif vcf_handler.infos[id][2] == "Float":
                table_type = "REAL"
            elif vcf_handler.infos[id][2] == "Integer":
                table_type = "INTEGER"
            else:
                table_type = "TEXT"
            # print vcf_handler.infos[id][0]
            if vcf_handler.infos[id][0][0].isdigit():
                table_name = '"u' + vcf_handler.infos[id][0] + '"'
            elif vcf_handler.infos[id][0].startswith("GERP"):
                table_name = '"GERP_RS"'
            else:
                table_name = '"' + vcf_handler.infos[id][0] + '"'
            DefaultStatement = DefaultStatement + table_name + " " + table_type + ", "
            TableIndex.append(table_name)
        # Samples columns
        SampleStatement = ""
        for sample in range(len(vcf_handler.samples)):
            SampleStatement += '"' + vcf_handler.samples[sample] + '"' + " TEXT, "
            TableIndex.append(vcf_handler.samples[sample])
        query = DefaultStatement + SampleStatement[:-2] + ");"

        # Create DB in sqlite3

        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(Drop_query)
        #return(query)
        c.execute(query)
        conn.commit()
        c.close()

        return 0

    def populateTablesSQLite3(vcf_handler, database, annotation, project_name):
        import string
        import time
        import sqlite3

        conn = sqlite3.connect(database)
        c = conn.cursor()

        autoincremental_id = 1

        query = ""
        start_time = time.time()

        for record in vcf_handler:
            DefaultStatement = ""
            coordinates = []
            info = []
            gt = []

            ### Base information generation (CHR, POS, ALT ...) and ID
            coordinates = [autoincremental_id, record.CHROM, str(record.POS), str(record.ID), record.REF,
                           str(record.ALT[0]), str(record.QUAL)]
            # print base
            # coordinates=",".join(baseStr)

            ### INFO generation
            null = string.maketrans('', '')
            for i in vcf_handler.infos.keys():
                try:
                    res = string.translate(str(record.INFO[i]), null, "[']")
                except KeyError:
                    res = "None"
                # print i,res
                if annotation == "annovar":
                    info.append(res)
                else:
                    CSQ = ""
                    if i == "CSQ":
                        CSQ = res.split("|")
                        info.append(CSQ)
                    else:
                        info.append(res)
            ### Genotype generation
            for i in range(len(record.samples)):
                gt.append(str(record.samples[i].gt_type))

            autoincremental_id += 1
            DefaultStatement = coordinates + info + gt
            query = "INSERT OR IGNORE INTO " + project_name + " VALUES(" + string.translate(str(DefaultStatement), null, "[]") + ");"
            # if autoincremental_id % 1000 == 0:
            # print "Written " + str(autoincremental_id) + " lines.."
            c.execute(query)
        conn.commit()
        conn.close()
        loading_time = (time.time() - start_time)
        return loading_time

    def populateTablesSQLite3_executemany(vcf_handler, database, annotation, project_name):
        import string
        import time
        import sqlite3
        from numpy import mean

        autoincremental_id = 1
        query = ""
        data=[]
        params=""
        start_time = time.time()

        record_time = []

        for record in vcf_handler:
            # grep the start reading record
            start_record=time.time()

            DefaultStatement = ""
            coordinates = []
            info = []
            gt = []
            null = string.maketrans('', '')

            ### Base information generation (CHR, POS, ALT ...) and ID
            ## Get FILTER status
            ## [] = PASS
            if record.FILTER==[]:
                filter_string = "PASS"
            else:
                filter_string = string.translate(str(record.FILTER), null, "[']")
            coordinates = [autoincremental_id, record.CHROM, str(record.POS), str(record.ID), record.REF,
                           str(record.ALT[0]), str(record.QUAL), filter_string]
            # print base
            # coordinates=",".join(baseStr)

            ### INFO generation
            for i in vcf_handler.infos.keys():
                try:
                    res = string.translate(str(record.INFO[i]), null, "[']")
                except KeyError:
                    res = "None"
                # print i,res
                if annotation == "annovar":
                    info.append(res)
                else:
                    CSQ = ""
                    if i == "CSQ":
                        CSQ = res.split("|")
                        for CSQ_field in CSQ:
                            info.append(CSQ_field)
                    else:
                        info.append(res)

            ### Genotype generation
            for i in range(len(record.samples)):
                gt.append(str(record.samples[i].gt_type))

            autoincremental_id += 1
            DefaultStatement = coordinates + info + gt
            data.append(tuple(DefaultStatement))
            end_record=time.time()
            record_time.append(end_record-start_record)

        # Vcf storing time
        vcf_store_time = (time.time() - start_time)
        record_store_time=mean(record_time)

        params = l=len(data[0])
        params = ("?," * l)[:-1]
        query = "INSERT OR IGNORE INTO " + project_name + " VALUES(" + params + ");"

        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute("PRAGMA synchronous = OFF")
        c.execute("PRAGMA journal_mode = OFF")
        c.executemany(query, data)
        conn.commit()
        conn.close()
        loading_time = (time.time() - start_time)
        return loading_time, vcf_store_time, record_store_time, autoincremental_id

    # Main

    # Reading the input
    sw_annotation = request.POST['sw_annotation']
    annotation_version = request.POST['annotation_version']
    vcf_name = request.POST['vcf_name']
    project_name = request.POST['project_name']
    assembly_version = request.POST['assembly_version']

    # Preprocessing
    ## Get the absolute path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models = os.path.join(base_dir, app_label, "models.py")
    vcf_dir = os.path.join(base_dir, "data/VCFs")
    filename = os.path.join(vcf_dir, vcf_name)
    database = os.path.join(base_dir, "data/db/projects_DB.sqlite3")
    dbinfo = os.path.join(base_dir, "data/db/myVCF_DB.sqlite3")
    manage_script = os.path.join(base_dir, "manage.py")
    # Read the VCF
    vcf_handler = vcf.Reader(open(filename, 'r'))

    # Get the sample list (IT'S A PYTHON LIST)
    samples = vcf_handler.samples
    # get samples number
    samples_len = len(vcf_handler.samples)

    # Create DB and populate it
    ### SQLITE version
    ### Generate the sqlite3 file and the "columns" from VCF header
    ### IMPORTANT IN MANUAL WIKI TO DEFINE MANDATORY FIELDS!!!!
    ### Annovar = exonicfunc_ensgene, gene_ensgene, func_ensgene, gene_refgene
    ### VEP = consequence
    if sw_annotation == "annovar":
        generateTableFromVCF_annovar(vcf_handler, database, project_name)
        default_col = ['chrom', 'pos', 'rs_id', 'ref', 'alt', 'gene_refgene', 'ac', 'af', 'exonicfunc_ensgene']
        mutation_col = 'exonicfunc_ensgene'
    else:
        generateTableFromVCF_VEP(vcf_handler, database, project_name)
        default_col = ['chrom', 'pos', 'rs_id', 'ref', 'alt', 'symbol', 'ac', 'af', 'consequence']
        mutation_col = 'consequence'
    #########
    ## Single execution for every set of values
    #loading_time = populateTablesSQLite3(vcf_handler, database, sw_annotation, project_name)

    ## Multiple execution
    loading_time, vcf_store_time, record_store_time, n_record = populateTablesSQLite3_executemany(vcf_handler, database, sw_annotation, project_name)
    n_record_rate = n_record/vcf_store_time
    # Add DB in myVCF_DB--> dbinfo

    db = DbInfo.objects.create(project_name = project_name,
                               gene_annotation = annotation_version,
                               sw_annotation = sw_annotation,
                               samples = samples,
                               samples_len = samples_len,
                               default_col = default_col,
                               mutation_col = mutation_col,
                               assembly_version = assembly_version
                               )
    db.save()

    # Output the context

    sanity_check = "OK"
    context = {'sanity_check': sanity_check,
               'vcf_name': vcf_name,
               'annotation_version': annotation_version,
               'assembly_version' : assembly_version,
               'sw_annotation': sw_annotation,
               'project_name': project_name,
               'loading_time': loading_time,
               'vcf_store_time': vcf_store_time,
               'record_store_time': record_store_time,
               'n_record_rate': n_record_rate,
               'n_record': n_record
               }

    # Modify model.py
    command = ["python",
               manage_script,
               "inspectdb",
               "--database",
               project_db]
    m = check_output(command)
    m = re.sub('managed = False\n', "", m)
    fm = open(models, "w")
    fm.write(m)
    fm.close()

    return render(request, 'vcf_submitted.html', context)
