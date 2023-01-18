from django.shortcuts import render


def index_page(request):
    return render(request, 'index_page.html')

def index_page_test(request):
    tab = "fefef"
    context = {'tab':tab}
    return render(request, 'index_page_test.html' ,context)