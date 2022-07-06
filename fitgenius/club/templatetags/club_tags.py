from django import template

register = template.Library()


@register.simple_tag
def percent_direction(percentage):
    if percentage < 0:
        return f'''<span class="text-danger me-2"> {round(percentage, 2)}% <i class="mdi mdi-arrow-down"></i> </span>'''
    elif percentage > 0:
        return f'''<span class="text-success me-2"> {round(percentage, 2)}% <i class="mdi mdi-arrow-up"></i> </span>'''
    else:
        return f'{percentage}%'
