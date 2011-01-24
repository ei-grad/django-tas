from socket import gethostbyaddr

from django.conf import settings

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='resolv_ip')
@stringfilter
def resolv_ip(ip):
    if settings.RESOLV_IP == True:
        try:
            return gethostbyaddr(ip)[0]
        except:
            pass
    return ip

