#!/usr/bin/env python
# coding: utf-8

import logging
from datetime import datetime

from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.db.models import Q, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from netstat.models import Session, Record
#from policy.models import Policy

from tas.utils import get_first_day


class IndexView(TemplateView):

    template_name = "index.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TemplateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)

        context['top10_session'] = Record.objects.filter(
                session__in=Session.objects.filter(user=self.request.user,
                    dt_finish=None)
                ).order_by('-traf_in')[:10]

        context['top10_month'] = Record.objects.filter(
                session__in=Session.objects.filter(Q(user=self.request.user),
                    Q(dt_finish__gte=get_first_day()) | Q(dt_finish=None))
                ).values('dst').annotate(traf_in=Sum('traf_in')
                        ).order_by('-traf_in')[:10]

        return context

def login(request, *args, **kwargs):

    from django.contrib.auth.views import login as auth_login_view
    ret = auth_login_view(request, *args, **kwargs)

    if request.method == 'POST' and request.user.is_authenticated():

        ip = request.META['REMOTE_ADDR']

        if Session.objects.filter(src=ip, dt_finish=None).count():
            if Session.objects.filter(user=request.user, src=ip, dt_finish=None).count():
                messages.success(request, 'Интернет уже включен для %s.' % ip)
            else:
                messages.warning(request, 'Интернет для адреса %s был включен другим пользователем, отключаем его.' % ip)
                session = Session.objects.get(src=ip, dt_finish=None)
                session.dt_finish = datetime.now()
                session.save()
        else:
            Session(user=request.user, src=ip).save()
            messages.success(request, 'Интернет включен для адреса %s.' % ip)

    return ret

@login_required
def logout(request, *args, **kwargs):

    ip = request.META['REMOTE_ADDR']

    if Session.objects.filter(src=ip, dt_finish=None).count():
        session = Session.objects.get(user=request.user, src=ip, dt_finish=None)
        session.dt_finish = datetime.now()
        session.save()
        messages.success(request, 'Интернет отключен для адреса %s.' % ip)
    else:
        messages.warning(request, 'Для вашего адреса не включен Интернет!')

    from django.contrib.auth.views import logout_then_login
    return logout_then_login(request, *args, **kwargs)

