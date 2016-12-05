from django.shortcuts import render

# Create your views here.
# Generic view from django
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.core import serializers
from django.shortcuts import render, get_object_or_404
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Generic view from django
from django.views import generic

# Datatable view from django-datatable-view package
# from django_datatables_view.base_datatable_view import BaseDatatableView
# from datatableview.views import DatatableView

# Data table from django-table
# from table.views import FeedDataView
# from .tables import VcfTable

from .models import Log, Vcf, Gene

## DB containing data
actual_db = "default"

def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/vcfdb/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Epidemic account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

class IndexView(generic.ListView):

    template_name = 'vcfdb/index.html'
    context_object_name = 'latest_log_list'

    def get_queryset(self):
        """Return the last five modification logged."""
        return Log.objects.order_by('-log_date')[:5]

class SearchView(generic.ListView):

    template_name = 'vcfdb/search.html'
    context_object_name = 'query'

    def get_queryset(self):
        return Vcf.objects.using(actual_db).all[1]

class ResultsView(generic.ListView):

    template_name = 'gene_results.html'
    model = Vcf

    def get(self):
        context = locals()
        mutations = Vcf.objects.filter(gene_ensgene__icontains=gene)
        context['mutations'] = mutations
        context['gene'] = gene
        return render_to_response(self.template_name, context, context_instance=RequestContext(request))

@login_required(login_url="/vcfdb/login")
def search(request):
    if request.method == 'POST': # If the form has been submitted...
        query = request.POST['q']
        #results = Vcf.objects.filter(gene_refgene__icontains=query).values('gene_refgene','gene_ensgene').distinct()
        results = Gene.objects.filter(genename__icontains=query).values('ensgene','genename','description').distinct()
        #json_results = serializers.serialize('json', results)
        #values = results.values()
        context={'query' : query, 'results' : results}
        return render(request, 'search.html', context)

@login_required(login_url="/vcfdb/login")
def display_vcf_table(request, gene_ensgene):
    import re
    if request.method == "GET":
        # Samples pattern matching
        samples_col = []
        s = re.compile('^[dhc]{1}[0-9]+')
        # Get header
        all_fields=[]
        for f in Vcf._meta.get_fields():
            all_fields.append(f.name)
            if s.match(f.name):
                samples_col.append(f.name)
        # Default columnns
        default_col = ['chrom', 'pos', 'rs_id', 'ref', 'alt', 'gene_refgene', 'ac', 'af', 'exonicfunc_refgene', 'exac_nfe']
        gene = gene_ensgene
        mutations = Vcf.objects.using(actual_db).filter(gene_ensgene__icontains=gene)

        context = { 'samples_col' : samples_col, 'default_col' : default_col, 'all_fields' : all_fields, 'gene' : gene, 'mutations' : mutations}
        return render(request, 'gene_results.html', context )



# Dev

def VcfToJson(request):
    query = request.POST['q_json']
    object_list = Vcf.objects.all().filter(gene_refgene__icontains=query) #or any kind of queryset
    json = serializers.serialize('json', object_list)
    return HttpResponse(json, content_type='application/json')

def get_gene_mutations(request, gene_ensgene):
    if request.method == "GET":
        gene = gene_ensgene
        mutations = Vcf.objects.filter(gene_ensgene__icontains=gene).values('chrom','rs_id','ref','alt','af','exonicfunc_refgene','gene_refgene','gene_ensgene','h32').distinct()
        context = { 'gene' : gene , 'mutations' : mutations }
        return render(request, 'gene_results.html', context )

def get_gene_mutations_JSON(request, gene_ensgene):
    if request.method == "GET":
        gene = gene_ensgene
        mutations = Vcf.objects.filter(gene_ensgene__icontains=gene)
        json = serializers.serialize('json', mutations)
        context = { 'gene' : gene , 'json' : json }
        #return HttpResponse(json, content_type='application/json')
        return render(request, 'gene_results.html', context )