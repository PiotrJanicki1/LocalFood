from .models import Category


def categories(request):
    """
    Returns a dictionary containing all categories.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary with all categories available in the database under the key 'categories'.
    """
    return {
        'categories': Category.objects.all()
    }

