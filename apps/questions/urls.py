#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from views import *


urlpatterns = patterns('',

    url(r'answer/(?P<question_id>[^/]+)/$', question_answer,
                                            name='question_answer'),
    
    )