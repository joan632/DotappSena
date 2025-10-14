from django.contrib import messages
from django.shortcuts import render, redirect


class SaveLastTemplateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(response, 'template_name') and response.template_name:
            request._last_template = response.template_name
        return response


class AmigableExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        messages.error(request, "En este momento no podemos procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.")

        # 1. ¿Vista de token único?
        if getattr(request, '_vista_de_token_unico', False):
            return redirect('login')

        # 2. ¿Tenemos template guardado en memoria?
        template = getattr(request, '_last_template', None)
        if template:
            return render(request, template, {})

        # 3. Fallback: login
        return redirect('login')