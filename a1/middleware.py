# yourapp/middleware.py
from django.http import HttpResponseNotFound, Http404
from django.urls import reverse, NoReverseMatch

class HandleErrorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except (Http404, AttributeError, TypeError) as e:
            try:
                home_url = reverse('home')
            except NoReverseMatch:
                home_url = '/'  # fallback if 'home' URL is not defined

            error_html = f"""
                <h3>Xatolik yuz berdi</h3>
                <p>{str(e)}</p>
                <a href="{home_url}">Bosh sahifa</a>
            """
            return HttpResponseNotFound(error_html)

        except Exception as e:
            print(f"[Middleware Error] Unexpected: {e}")
            return HttpResponseNotFound("Noma'lum tizim xatosi.")

