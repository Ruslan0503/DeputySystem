from django import template

register = template.Library()

@register.filter
def has_role(profile,role_name):
	if profile is None:
		return False
	return profile.has_role(role_name)
