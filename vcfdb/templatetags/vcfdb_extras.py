__author__ = 'pietrelli'

from django import template
from django.conf import settings
import re

register = template.Library()
numeric_test = re.compile("^\d+$")

#@register.filter
def get_range( value ):
  """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
  """
  return range( value )

@register.filter
def getattr (obj, args):
    """ Try to get an attribute from an object.

    Example: {% if block|getattr:"editable,True" %}

    Beware that the default is always a string, if you want this
    to return False, pass an empty second argument:
    {% if block|getattr:"editable," %}
    """
    args = args.split(',')
    if len(args) == 1:
        (attribute, default) = [args[0], '']
    else:
        (attribute, default) = args
    try:
        return obj.__getattribute__(attribute)
    except AttributeError:
         return  obj.__dict__.get(attribute, default)
    except:
        return default

@register.filter
def get_sample_list (obj, args):
    """ Try to get an attribute from an object.

    Example: {% if block|getattr:"editable,True" %}

    Beware that the default is always a string, if you want this
    to return False, pass an empty second argument:
    {% if block|getattr:"editable," %}
    """
    args = args.split(',')
    default=''
    if len(args) == 1:
        group = [args[0]]
    try:
        return obj.sample_list(group)
    except:
        return default

@register.filter
def get_mutation_genotype_by_group(obj, group):
    # Obj single VCF obj
    samples = obj.sample_list(group)
    genotype=0
    l=[]
    freq = 0
    for sample in samples:
        try:
            genotype += (int(getattr(obj, sample)))
        except ValueError:
            genotype += 0
        #l.append((int(getattr(obj, sample))))
    freq = round(genotype/float(len(samples)),2)
    return genotype

@register.filter
def get_mutation_by_type(obj, args):
    # Obj list of VCF obj
    args = args.split(',')
    type = args[0]
    group = args[1]
    mutations=0
    for mutation in obj:
        # RefGene
        if mutation.exonicfunc_refgene.startswith(type):
            mutations += mutation.get_mutation_genotype_by_group(group)
        # ENSGENE
        #if mutation.exonicfunc_ensgene.startswith(type):
        #    mutations += mutation.get_mutation_genotype_by_group(group)


    return mutations


