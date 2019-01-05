import os
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa



def link_callback(uri, rel):
    # use short variable names
    sUrl = r'/static/'      # Typically /static/
    sRoot = os.path.expanduser('~/PycharmProjects/') + "/QuizExitSurvey/static/"# Typically /home/userX/project_static/
    mUrl = '/static/media/'     # Typically /static/media/
    mRoot = ''     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
        print("111111111111111111111111111")
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
    return path
