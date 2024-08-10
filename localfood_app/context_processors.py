from .models import Category, User


def categories(request):
    return {
        'categories': Category.objects.all()
    }

