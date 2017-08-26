from django.views.generic import View
from django.shortcuts import render


class ResourceSearchView(View):
    form_class = UserForm
    template_name = 'frontend/resource_search.html'

    def get(self, request):
        return render(request, self.template_name,)

    def post(self, request):
        return render(request, self.template_name,)
