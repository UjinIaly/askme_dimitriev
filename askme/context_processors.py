from app.models import Tag, Profile


def tags(arg):
    tags = Tag.objects.get_best_tags()
    return {'tags': tags}


def best_members(arg):
    best_members = Profile.objects.get_best_users()
    return {'members': best_members}
