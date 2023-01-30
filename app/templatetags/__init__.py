from app.forms import Profile
from django import template

register = template.Library()


@register.simple_tag
def get_vote(user, obj_type, obj_id):
    # print(f'{user}  {obj_id}')
    vote = Profile.objects.get_user_vote(user=user, obj_type=obj_type, obj_id=obj_id)
    if vote is None:
        return 'NONE'
    return vote.mark_type
