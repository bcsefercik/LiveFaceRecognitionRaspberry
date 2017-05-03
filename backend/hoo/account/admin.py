# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Resident

class ResidentAdmin(admin.ModelAdmin):
	model = Resident


admin.site.register(Resident, ResidentAdmin)