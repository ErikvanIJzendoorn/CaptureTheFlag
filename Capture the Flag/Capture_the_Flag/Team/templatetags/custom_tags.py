from django import template

register = template.Library()

@register.simple_tag
def get_complementary(color):
        if color == "":
            return "#000000"
        color = color[1:]
        color = int(color, 16)
        comp_color = 0xFFFFFF ^ color
        comp_color = "#%06X" % comp_color
        return comp_color