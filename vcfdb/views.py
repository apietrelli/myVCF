from django.shortcuts import render, render_to_response

# Create your views here.
# Generic view from django
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.apps import apps
import ast
import json
import re
from collections import Counter
from collections import OrderedDict
import numpy as np
import requests

# Generic view from django
from django.views import generic

# Datatable view from django-datatable-view package
# from django_datatables_view.base_datatable_view import BaseDatatableView
# from datatableview.views import DatatableView

# Data table from django-table
# from table.views import FeedDataView
# from .tables import VcfTable

# Import models
# Vcf model
app_label = "vcfdb"
from vcfdb.models import *
from vcfdb.base_models import Log, Gene84, Gene75, DbInfo

## DB containing common data
actual_db = "default"
## DB containing mutations
project_db = "projects"


def error404(request):
    context = {'test': "OK"}
    return render(request, '404.html', context)


def error500(request):
    context = {'test': "OK"}
    return render(request, '500.html', context)


def not_found(request, project_name, q):
    context = {'q': q,
               'project_name': project_name}
    return render(request, 'not_found.html', context)


def project_homepage(request, project_name):
    # Get the information of DB selected
    dbinfo = DbInfo.objects.filter(project_name=project_name).first()
    sw_annotation = dbinfo.sw_annotation
    gene_annotation = dbinfo.gene_annotation
    context = {'project_name': project_name,
               'sw_annotation': sw_annotation,
               'gene_annotation': gene_annotation}
    return render(request, 'index.html', context)


def search(request, project_name):
    def is_region(query):
        res = len(re.findall(r"[:-]", query))
        if res == 2:
            return 1
        else:
            return 0

    def split_region(region):
        # Get the numbers from string
        r = re.findall(r"\d+", region)
        # test for element length (CHR:start-end)
        if len(r) == 3:
            return "%s-%s-%s" % (r[0], r[1], r[2])
        else:
            return 0

    def is_dbsnp(query):
        # Check correct rs number
        pattern = re.compile('^rs[1-9]+', re.IGNORECASE)
        if pattern.match(query):
            return 1
        else:
            return 0

    def is_variant(query):
        # Check correct rs number
        pattern = re.compile('^[0-9XY]{1,2}-[0-9]+-[0-9]+-[A,T,G,C]+-[A,T,G,C]+', re.IGNORECASE)
        if pattern.match(query):
            return 1
        else:
            return 0

    def get_dbsnp_record(query, model_project):
        results = model_project.objects.using(project_db).filter(rs_id=query)
        return results

    if request.method == 'GET':  # If the form has been submitted...
        query = request.GET['q']
        dbinfo = DbInfo.objects.filter(project_name=project_name).first()
        gene_annotation = dbinfo.gene_annotation
        sw_annotation = dbinfo.sw_annotation

        # Get the project model
        model_project = apps.get_model(app_label=app_label,
                                       model_name=project_name)

        # Define the query: Region or Gene?
        if is_region(query):
            region_query = split_region(query)
            return HttpResponseRedirect('/vcfdb/%s/region/%s' % (project_name, region_query))

        elif is_dbsnp(query):
            results = get_dbsnp_record(query, model_project)
            if sw_annotation == "vep":
                gene_symbol_col = "symbol"
                ensgene_id_col = "gene"
            else:
                gene_symbol_col = "gene_refgene"
                ensgene_id_col = "gene_ensgene"
            context = {'query': query,
                       'results': results,
                       'ensgene_id_col': ensgene_id_col,
                       'gene_symbol_col': gene_symbol_col,
                       'project_name': project_name}
            return render(request, 'search_variant.html', context)
        elif is_variant(query):
            # Remove whitespaces
            query = query.replace(" ", "")
            return HttpResponseRedirect('/vcfdb/%s/variant/%s' % (project_name, query))
        else:
            # Get the ENSEMBL model
            model_name_ensembl = "Gene" + gene_annotation
            model_ensembl = apps.get_model(app_label=app_label,
                                           model_name=model_name_ensembl)

            results = model_ensembl.objects.filter(genename__icontains=query).values('ensgene', 'genename',
                                                                                     'description').distinct()

            # Get mutation count for each ENSGENE
            # Build a new dictionary which contains EnsembleGeneID, description, Genename and mutation count
            # final_results is the merged dictionary
            final_results = []
            for res in results:
                ensgene_id = res['ensgene']
                if sw_annotation == "annovar":
                    count = model_project.objects.using(project_db).filter(gene_ensgene__iexact=ensgene_id).count()
                else:
                    count = model_project.objects.using(project_db).filter(gene__iexact=ensgene_id).count()
                res['mut_count'] = count
                final_results.append(res)

            # json_results = serializers.serialize('json', results)
            # values = results.values()
            context = {'query': query,
                       'results': final_results,
                       'project_name': project_name}
            return render(request, 'search.html', context)


def display_gene_results(request, gene_ensgene, project_name):
    type = "gene"

    def get_mutations(model, sw_annotation, mutation_col, ensgene, project_db):
        # return the mutations and default_col of a particular gene based on the sw_annotation
        mutations_category = []
        if sw_annotation == "annovar":
            # contains the ensg
            #mutations = model.objects.using(project_db).filter(gene_ensgene__icontains=ensgene)
            # exact match
            mutations = model.objects.using(project_db).filter(gene_ensgene__iexact=ensgene)
            for m in mutations:
                mutations_category.append(getattr(m, mutation_col).encode())
        else:
            # contains the ensg
            mutations = model.objects.using(project_db).filter(gene__icontains=ensgene)
            # exact match
            mutations = model.objects.using(project_db).filter(gene__iexact=ensgene)
            for m in mutations:
                mutations_category.append(str(getattr(m, mutation_col).encode()))
        mutations_category = Counter(mutations_category)
        return mutations, mutations_category

    # get the info of the project
    dbinfo = DbInfo.objects.filter(project_name=project_name).first()
    sw_annotation = dbinfo.sw_annotation
    gene_annotation = dbinfo.gene_annotation
    samples = ast.literal_eval(dbinfo.samples)
    default_col = ast.literal_eval(dbinfo.default_col)
    mutation_col = dbinfo.mutation_col

    # Get gene symbol from ensembl table
    model_name_ensembl = "Gene" + gene_annotation
    model_ensembl = apps.get_model(app_label=app_label,
                                   model_name=model_name_ensembl)
    gene_symbol = model_ensembl.objects.filter(ensgene__iexact=gene_ensgene).values('genename').distinct()[0]

    # Eliminate all special character in samples for clumn visibility
    # django converts CAPITAL in small letter
    # 1. from "-" to "-"
    samples = [sample.replace('-', '_') for sample in samples]

    n_samples = dbinfo.n_samples()
    model = apps.get_model(app_label=app_label,
                           model_name=project_name)

    if request.method == "GET":
        # Samples pattern matching
        samples_col = samples
        # return HttpResponse(samples_col)
        # Get header
        all_fields = []
        for f in model._meta.get_fields():
            all_fields.append(f.name)

        # Get the mutation data
        mutations, mutations_category = get_mutations(model, sw_annotation, mutation_col, gene_ensgene, project_db)

        ## Get data for plot
        # Get mutation categories
        category = [key.encode('ascii', 'ignore') for key in mutations_category.keys()]
        values = mutations_category.values()

        context = {'samples_col': samples_col,
                   'default_col': default_col,
                   'all_fields': all_fields,
                   'query': gene_ensgene,
                   'gene_symbol': gene_symbol,
                   'mutations': mutations,
                   'category': category,
                   'values': values,
                   'type': type,
                   'project_name': project_name}
        return render(request, 'gene_results.html', context)


def display_region_results(request, region, project_name):
    check = "OK"
    type = "region"

    # return HttpResponse(check)

    def check_region_format(region):
        response = True
        msg = "OK"
        if len(region.split("-")) < 3:
            response = False
            msg = "Error in formatting region! CHR:start-end format is the only allowed"
        return (response, msg)

    def get_mutations(model, sw_annotation, mutation_col, region, project_db):
        # Split region in CHR, START, END
        r = region.split("-")
        chr = r[0]
        start = r[1]
        end = r[2]

        # return the mutations and default_col of a region
        mutations_category = []
        mutations = model.objects.using(project_db).filter(chrom=chr).filter(pos__range=[start, end])

        # Extract region category for chart plot
        for m in mutations:
            mutations_category.append(getattr(m, mutation_col).encode())

        mutations_category = Counter(mutations_category)
        return mutations, mutations_category

    # get the info of the project
    dbinfo = DbInfo.objects.filter(project_name=project_name).first()
    sw_annotation = dbinfo.sw_annotation
    gene_annotation = dbinfo.gene_annotation
    samples = ast.literal_eval(dbinfo.samples)
    default_col = ast.literal_eval(dbinfo.default_col)
    mutation_col = dbinfo.mutation_col

    # Eliminate all special character in samples for clumn visibility
    # django converts CAPITAL in small letter
    # 1. from "-" to "-"
    samples = [sample.replace('-', '_') for sample in samples]

    n_samples = dbinfo.n_samples()
    model = apps.get_model(app_label=app_label,
                           model_name=project_name)

    if request.method == "GET":
        # Samples pattern matching
        samples_col = samples
        # return HttpResponse(samples_col)
        # Get header
        all_fields = []
        for f in model._meta.get_fields():
            all_fields.append(f.name)

        # Get the mutation data
        mutations, mutations_category = get_mutations(model, sw_annotation, mutation_col, region, project_db)

        ## Get data for plot
        # Get mutation categories
        category = [key.encode('ascii', 'ignore') for key in mutations_category.keys()]
        values = mutations_category.values()

        context = {'samples_col': samples_col,
                   'default_col': default_col,
                   'all_fields': all_fields,
                   'query': region,
                   'gene_symbol': region,
                   'mutations': mutations,
                   'category': category,
                   'values': values,
                   'type': type,
                   'project_name': project_name}

        return render(request, 'gene_results.html', context)


def display_variant_results(request, variant, project_name):
    def format_variant(variant):
        v = {}
        split_v = variant.split("-")
        v['chrom'] = split_v[0]
        v['pos'] = split_v[1]
        v['ref'] = split_v[3]
        v['alt'] = split_v[4]
        return v

    def get_mutations(model, variant, project_db, mutation_col):
        # return the mutation of a particular location
        try:
            mutations = model.objects.using(project_db).filter(chrom=variant['chrom'],
                                                               pos=variant['pos'],
                                                               ref=variant['ref'],
                                                               alt=variant['alt']).get()
        except:
            mutations = 0
        return mutations

    def get_zigosity(samples, mutations):
        l = []
        for sample in samples:
            s = sample.lower()
            l.append(getattr(mutations, s))
        d = Counter(l)
        return d

    if request.method == 'GET':  # If the form has been submitted...
        # get the info of the project
        dbinfo = DbInfo.objects.filter(project_name=project_name).first()
        sw_annotation = dbinfo.sw_annotation
        gene_annotation = dbinfo.gene_annotation
        samples = ast.literal_eval(dbinfo.samples)
        default_col = ast.literal_eval(dbinfo.default_col)
        mutation_col = dbinfo.mutation_col
        n_samples = dbinfo.n_samples()

        # Get the gene field depending on annotation
        if sw_annotation == "annovar":
            gene_field = "gene_ensgene"
        else:
            gene_field = "gene"

        v = format_variant(variant)

        model = apps.get_model(app_label=app_label,
                               model_name=project_name)

        model_name_ensembl = "Gene" + gene_annotation
        model_ensembl = apps.get_model(app_label=app_label,
                                       model_name=model_name_ensembl)

        mutations = get_mutations(model, v, project_db, mutation_col)
        csq = getattr(mutations, mutation_col)
        ensgene_id = getattr(mutations, gene_field)
        # To fix
        # Example: in annovar annotation, 1:865628 G / A SAMD11
        gene = model_ensembl.objects.filter(ensgene=ensgene_id).values("genename", "description").distinct()
        # To fix: Multiple ENSGID in gene
        #return HttpResponse(gene)


        if mutations == 0:
            context = {'q': variant,
                       'project_name': project_name}
            template = 'not_found.html'

        else:
            low_ac = 0
            covered_samples = mutations.an/2
            if mutations.an <= ((n_samples*2)*80/100):
                low_ac = 1

            zigosity_index = ["0", "1", "2"]
            zigosity_list = get_zigosity(samples, mutations)

            context = {'mutations': mutations,
                       'low_ac': low_ac,
                       'n_samples': n_samples,
                       'covered_samples': covered_samples,
                       'csq': csq,
                       'ensgene_id': ensgene_id,
                       'gene': gene,
                       'zigosity_index': zigosity_index,
                       'zigosity_list': zigosity_list,
                       'project_name': project_name,
                       'variant': variant}
            template = 'variant_results.html'

        # return HttpResponse(mutations)
        return render(request, template, context)


def get_exac_data(request, variant, project_name):
    # reformat position from:
    # CHR-POS-POS-REF-ALT
    # in
    # CHR-POS-REF-ALT
    s = "-"
    v_split = variant.split(s)

    v = s.join([v_split[0], v_split[1], v_split[3], v_split[4]])
    url = "http://exac.hms.harvard.edu/rest/variant/variant/" + v
    r = requests.get(url)
    if r.ok:
        response = r.ok
        exac_data = r.json()
        populations = exac_data["pop_ans"].keys()

        res_data = []
        tmp = {}
        for pop in populations:
            tmp = {}
            tmp["population"] = pop
            tmp["pop_acs"] = exac_data["pop_acs"][pop]
            tmp["pop_ans"] = exac_data["pop_ans"][pop]
            tmp["pop_homs"] = exac_data["pop_homs"][pop]
            tmp["pop_af"] = float("{0:.6f}".format(exac_data["pop_acs"][pop] / float(exac_data["pop_ans"][pop])))
            res_data.append(tmp)

    else:
        response = False
        res_data = {}

    context = json.dumps({'response': response,
                          'data': res_data,
                          'url': url})
    return HttpResponse(context)


def get_esp_data(request, variant, project_name):
    # reformat position from:
    # CHR-POS-POS-REF-ALT
    # in
    # CHR:g.PosRef>ALT
    s = "-"
    v_split = variant.split(s)

    v = v_split[0] + ':g.' + v_split[1] + v_split[3] + '>' + v_split[4]

    # ESP hg19
    url = "http://grch37.rest.ensembl.org/vep/human/hgvs/" + v + "?content-type=application/json"

    r = requests.get(url)
    if r.ok:
        response = r.ok
        data = r.json()
        res_data = []
        val = 0
        # EA
        tmp = {}
        try:
            tmp["population"] = "EA - European American"
            tmp["pop_af"] = data[0]['colocated_variants'][0]['ea_maf']
        except:
            tmp = {}
            val = 1

        res_data.append(tmp)

        # AA
        tmp = {}
        tmp["population"] = "AA - African American"
        try:
            tmp["population"] = "AA - African American"
            tmp["pop_af"] = data[0]['colocated_variants'][0]['aa_maf']
        except:
            tmp={}
            val = 1

        res_data.append(tmp)

        if val == 1:
            return HttpResponse("")
    else:
        response = False
        res_data = []

    context = json.dumps({'response': response,
                          'data': res_data,
                          'url': url})
    return HttpResponse(context)


def get_1000g_data(request, variant, project_name):
    # reformat position from:
    # CHR-POS-POS-REF-ALT
    # in
    # CHR:g.PosRef>ALT
    s = "-"
    v_split = variant.split(s)

    v = v_split[0] + ':g.' + v_split[1] + v_split[3] + '>' + v_split[4]

    # 1000G hg19
    url = "http://grch37.rest.ensembl.org/vep/human/hgvs/" + v + "?content-type=application/json"

    r = requests.get(url)

    if r.ok:
        response = r.ok
        data = r.json()
        res_data = []
        val = 0
        pop_dict = {"eur_maf": "European",
                    "afr_maf": "African",
                    "sas_maf": "South Asian",
                    "eas_maf": "East Asian",
                    "amr_maf": "American (Ad Mixed)"}

        # Tmp results
        for pop in pop_dict.keys():
            tmp = {}
            pop_value = pop_dict[pop]
            tmp["population"] = pop_value
            try:
                tmp["pop_af"] = data[0]['colocated_variants'][0][pop]
            except:
                tmp["pop_af"] = None
                val = 1
            res_data.append(tmp)

        if val == 1:
            return HttpResponse("")
    else:
        response = False
        res_data = []

    context = json.dumps({'response': response,
                          'data': res_data,
                          'url': url})
    return HttpResponse(context)


#
# settings: Get the COL_LIST FROM the DB
#
def settings(request, project_name):
    msg_validate = "OK"
    context = {'project_name': project_name,
               'msg_validate': msg_validate}
    return render(request, 'settings.html', context)


#
# get_col_list: Get the COL_LIST FROM the DB
#
def get_col_list(request, project_name):
    dbinfo = DbInfo.objects.filter(project_name=project_name).first()
    sw_annotation = dbinfo.sw_annotation

    # Transform string into PYTHON LIST (ast.literal_eval)
    samples = ast.literal_eval(dbinfo.samples)
    default_cols = ast.literal_eval(dbinfo.default_col)
    mutation_col = dbinfo.mutation_col

    # Eliminate all special character in samples for clumn visibility
    # django converts CAPITAL in small letter
    # - from "-" to "-"
    samples = [sample.replace('-', '_').lower() for sample in samples]

    model = apps.get_model(app_label=app_label,
                           model_name=project_name)
    # Get all fields
    all_cols = []
    # Not visible cols
    other_cols = []
    for f in model._meta.get_fields():
        all_cols.append(f.name)
        if f.name not in default_cols and f.name not in samples:
            other_cols.append(f.name)
    # Remove ID (autoincrement from DB)
    all_cols.remove('id')
    other_cols.remove('id')
    sanity_check = "OK"
    context = json.dumps({'project_name': project_name,
                          'default_cols': default_cols,
                          'all_cols': all_cols,
                          'other_cols': other_cols,
                          'mutation_col': mutation_col,
                          'sanity_check': sanity_check})
    return HttpResponse(context)


#
# save_preferences (AJAX): Modify the COL Visualization according to the user choice
#
def save_preferences(request, project_name):
    # Get the user-defined cols
    cols = request.POST.getlist("cols")
    mutation_col = request.POST["mutation_col"]

    # Join the single cols and convert the string into list
    s = ','
    new_col = s.join(cols).split(',')

    ## Update the default_col field
    dbinfo = DbInfo.objects.filter(project_name=project_name).first()
    dbinfo.default_col = new_col
    ## Update mutation_col field
    dbinfo.mutation_col = mutation_col

    # Save preferences
    dbinfo.save()

    msg_validate = "OK"
    context = json.dumps({'project_name': project_name,
                          'msg_validate': msg_validate,
                          'new_col': new_col,
                          'mutation_col': mutation_col})
    return HttpResponse(context)


def summary_statistics(request, project_name):
    msg_validate = "OK"

    # Get the project model
    model_project = apps.get_model(app_label=app_label,
                                   model_name=project_name)

    ## Get DB INFO
    dbinfo = DbInfo.objects.filter(project_name=project_name).first()
    samples = ast.literal_eval(dbinfo.samples)
    samples = [sample.replace('-', '_').lower() for sample in samples]

    # Annotation sw
    sw_annotation = dbinfo.sw_annotation

    # Number of samples
    n_samples = dbinfo.n_samples()

    # Get the number of mutation found
    n_mutations = model_project.objects.using(project_db).count()

    context = {'project_name': project_name,
               'n_samples': n_samples,
               'sw_annotation': sw_annotation,
               'n_mutations': n_mutations,
               'msg_validate': msg_validate}
    return render(request, 'summary_statistics.html', context)

#
# get_qual_vcf: Get the quality distribution of VCF quality field
#
def get_qual_vcf(request, project_name, cache):
    # Cache key
    cache_key = project_name + "/get_qual_vcf"

    if cache.has_key(cache_key) == False:
        # Get the project model
        model_project = apps.get_model(app_label=app_label,
                                       model_name=project_name)

        # Quality field
        qual_field = "qual"
        quals = model_project.objects.using(project_db).values_list(qual_field, flat=True)

        qual_median = np.median(quals)
        qual_mean = np.mean(quals)

        quals = np.log10(quals)

        # Get bin and values
        qual_data, qual_bins = np.histogram(quals, bins="auto")
        qual_bins = np.power(qual_bins, 10)

        # Generate qual_data array
        data=[]
        for i in range(0,len(qual_data)-1):
            tmp=[]
            tmp.append(qual_bins[i])
            tmp.append(qual_data[i])
            data.append(tmp)

        cache[cache_key] = json.dumps({'qual_data': data,
                                       'qual_mean': qual_mean,
                                       'cache': cache})

    context = cache[cache_key]
    return HttpResponse(context)


#
# get_mean_variations: Get mean number of variations for each sample
#
def get_mean_variations(request, project_name, cache):
    # Cache key
    cache_key = project_name + "/get_mean_variations"

    def is_outlier(value, p25, p75):
        """Check if value is an outlier
        """
        lower = p25 - 1.5 * (p75 - p25)
        upper = p75 + 1.5 * (p75 - p25)
        return value <= lower or value >= upper

    if cache.has_key(cache_key) == False:
        # Get the project model
        model_project = apps.get_model(app_label=app_label,
                                       model_name=project_name)
        # Get dbinfo
        dbinfo = DbInfo.objects.filter(project_name=project_name).first()
        samples = ast.literal_eval(dbinfo.samples)
        samples = [sample.replace('-', '_').lower() for sample in samples]

        var_samples = []
        for sample in samples:
            value = 0
            search_type = "gt"
            filter_string = sample + "__" + search_type
            value = model_project.objects.using(project_db).filter(**{filter_string: 0}).count()
            # value = res.count()
            var_samples.append(value)

        # Since highchart DRAW only values without calculate anything:
        # I will calculate all the stats in this function
        x = project_name
        mut_q1 = np.percentile(var_samples, 25)
        mut_q3 = np.percentile(var_samples, 75)

        # Add data to the boxplot and outlier_data array
        boxplot_values = []
        outlier_data = []
        for val in var_samples:
            if is_outlier(val, mut_q1, mut_q3):
                outlier = [0, val]
                outlier_data.append(outlier)
            else:
                boxplot_values.append(val)

        # Calculate statistics
        mut_min = min(boxplot_values)
        mut_max = max(boxplot_values)
        mut_median = np.median(var_samples)

        # Generate boxplot_data array
        boxplot_data = []
        boxplot_data.extend([x,
                             mut_min,
                             mut_q1,
                             mut_median,
                             mut_q3,
                             mut_max])

        cache[cache_key] = json.dumps({'boxplot_data': boxplot_data,
                                       'outlier_data': outlier_data,
                                       'cache': cache})

    context = cache[cache_key]
    return HttpResponse(context)


#
# get_chr_variations: Get the number of variations stratified by biotype
#
def get_chr_variations(request, project_name, cache):
    # Cache key
    cache_key = project_name + "/get_chr_variations"

    if cache.has_key(cache_key) == False:
        # Get the project model
        model_project = apps.get_model(app_label=app_label,
                                       model_name=project_name)

        ## Get DB INFO
        dbinfo = DbInfo.objects.filter(project_name=project_name).first()
        # Chromosome column
        chr_col = "chrom"
        # Consequence column
        mutation_col = dbinfo.get_mutation_col()

        # Get chrom list
        chromosomes = model_project.objects.using(project_db).values_list(chr_col, flat=True).distinct()
        # Get function list
        functions = model_project.objects.using(project_db).values_list(mutation_col, flat=True).distinct()
        # Get the summary count of the mutation by chr
        chr_summary = Counter(model_project.objects.using(project_db).values_list(chr_col, mutation_col))

        ## Format data for Highcharts --> BAR CHART
        # Categories = Chromosomes
        # Get the data
        tmp_plot_data = {}
        visible_data = {}
        for func in functions:
            for chr in chromosomes:
                data = chr_summary[chr, func]
                if tmp_plot_data.has_key(func):
                    tmp_plot_data[func].append(data)
                else:
                    tmp_plot_data[func] = [data]

        number_of_categories = 15
        keys = OrderedDict(sorted(tmp_plot_data.items(), key=lambda t: -sum(t[1]))).keys()[:number_of_categories]
        plot_data = {}
        for k in keys:
            plot_data[k] = tmp_plot_data[k]

        cache[cache_key] = json.dumps({'chromosomes': list(chromosomes),
                                       'plot_data': plot_data,
                                       'cache': cache})
    context = cache[cache_key]
    return HttpResponse(context)


#
# get_biotype_variations: Get the number of variations stratified by biotype
#
def get_biotype_variations(request, project_name, cache):
    # Cache key
    cache_key = project_name + "/get_biotype_variations"

    if cache.has_key(cache_key) == False:
        # Get the project model
        model_project = apps.get_model(app_label=app_label,
                                       model_name=project_name)

        ## Get DB INFO
        dbinfo = DbInfo.objects.filter(project_name=project_name).first()

        # Get sw annotation
        sw_annotation = dbinfo.sw_annotation

        # Biotype column
        biotype_col = ""
        if sw_annotation == "vep":
            biotype_col = "biotype"
        else:
            biotype_col = "func_ensgene"

        # Get the summary count of the mutation by type
        biotype_summary = Counter(model_project.objects.using(project_db).values_list(biotype_col, flat=True))
        mutation_type_summary_sorted = OrderedDict(sorted(biotype_summary.items(), key=lambda t: -t[1]))

        # Format data for Highcharts --> PIE CHART
        plot_data = []
        for type in mutation_type_summary_sorted.keys():
            data = [str(type), mutation_type_summary_sorted[type]]
            plot_data.append(data)

        cache[cache_key] = json.dumps({'plot_data': plot_data,
                                       'cache': cache})
    context = cache[cache_key]
    return HttpResponse(context)


#
# get_exonictype_variations: Get the number of variations stratified by exonic function
#
def get_exonictype_variations(request, project_name, cache):
    # Cache key
    cache_key = project_name + "/get_exonictype_variations"

    if cache.has_key(cache_key) == False:
        # Get the project model
        model_project = apps.get_model(app_label=app_label,
                                       model_name=project_name)

        ## Get DB INFO
        dbinfo = DbInfo.objects.filter(project_name=project_name).first()

        # Consequence column
        mutation_col = dbinfo.get_mutation_col()

        # Get the summary count of the mutation by type
        mutation_type_summary = Counter(model_project.objects.using(project_db).values_list(mutation_col, flat=True))
        mutation_type_summary_sorted = OrderedDict(sorted(mutation_type_summary.items(), key=lambda t: -t[1]))

        # Format data for Highcharts --> PIE CHART
        plot_data = []
        for type in mutation_type_summary_sorted.keys():
            data = [str(type), mutation_type_summary_sorted[type]]
            plot_data.append(data)

        cache[cache_key] = json.dumps({'plot_data': plot_data,
                                       'cache': cache})
    context = cache[cache_key]
    return HttpResponse(context)


#
# get_exonictype_variations: Get the mutations of the top mutated genes
#
def get_top_genes(request, project_name, cache):
    # N genes to display
    n_genes = 20
    n_categories = 5
    # Cache key
    cache_key = project_name + "/get_top_genes"

    if cache.has_key(cache_key) == False:
        # Get the project model
        model_project = apps.get_model(app_label=app_label,
                                       model_name=project_name)
        ## Get DB INFO
        dbinfo = DbInfo.objects.filter(project_name=project_name).first()

        # Get sw annotation
        sw_annotation = dbinfo.sw_annotation

        # Consequence column
        mutation_col = dbinfo.get_mutation_col()

        # Get ENSGENE ID based on annotation sw
        if sw_annotation == "vep":
            gene_col = "gene"
        else:
            gene_col = "gene_ensgene"

        ## Get data
        # Get the gene list
        res_genes = Counter(model_project.objects.using(project_db).all().values_list(gene_col, flat=True))
        # Get the first n_genes
        # Categories = top_genes
        top_genes = OrderedDict(sorted(res_genes.items(), key=lambda t: -t[1])).keys()[:n_genes]

        # Get function list
        search_type = "in"
        filter_string = gene_col + "__" + search_type
        res_functions = Counter(
            model_project.objects.using(project_db).filter(**{filter_string: top_genes}).values_list(mutation_col,
                                                                                                     flat=True))
        # Get the first n_categories
        functions = OrderedDict(sorted(res_functions.items(), key=lambda t: -t[1])).keys()[:n_categories]

        # Get the plot data
        plot_data = {}
        for func in functions:
            for gene in top_genes:
                data = model_project.objects.using(project_db).filter(**{gene_col: gene}).filter(
                    **{mutation_col: func}).count()
                if plot_data.has_key(func):
                    plot_data[func].append(data)
                else:
                    plot_data[func] = [data]

        cache[cache_key] = json.dumps({'top_genes': list(top_genes),
                                       'plot_data': plot_data,
                                       'cache': cache})
    context = cache[cache_key]
    return HttpResponse(context)
