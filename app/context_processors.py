from app.models import ProjectCache

def popular_tags(request):
    tags = ProjectCache.get_popular_tags()

    return {'popular_tags': tags}

# def best_users(request):
#     users = ProjectCache.get_best_users()
#
#     return {'best_users': users}