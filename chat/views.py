from django.http import HttpResponse

# Create your views here.


def index(request) -> HttpResponse:
    return HttpResponse(
        b"Hello world! I am Wingman, your personal shopping assistant !"
    )
