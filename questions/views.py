from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from cgi import parse_qsl, escape

class AboutView(TemplateView):
    template_name = "about.html"

@csrf_exempt
def getpost(request):
    result = ['<h1>Django</h1>']
    result.append('Post:')
    result.append('<form method="post">')
    result.append('<input type="text" name = "test">')
    result.append('<input type="submit" value="Send">')
    result.append('</form>')

    if request.method == 'POST':
        result.append('<h1>Post data:</h1>')
        result.append(request.POST.get('test'))

    if request.method == 'GET':
        if request.GET:
            result.append('<h1>Get data:</h1>')
            for key, value in request.GET.items():
                keyvalue=key+" = "+value
                result.append(keyvalue)

    return HttpResponse('<br>'.join(result))
