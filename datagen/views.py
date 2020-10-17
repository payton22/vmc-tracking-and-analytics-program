from django.shortcuts import render
from django.http import HttpResponse
from .forms import DateForm
from .scanner_generation import gen_scan_file
# Create your views here.

def index(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            gen_scan_file('scanner_data.csv',form.cleaned_data['date'])
            content = open('scanner_data.csv').read()
            response = HttpResponse(content)
            response['Content-Type'] = 'text/plain'
            response['Content-Disposition'] = 'attachment; filename=scanner_data.csv'
            return response
    else:
        form = DateForm()

    return render(request,'datagen/index.html', {'form': form})
