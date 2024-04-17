
def get_search_keyword(request):
    if request.method == 'GET':
        return request.GET.get('search', '')
    return ''

    