# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Resident, Visit

class ResidentAdmin(admin.ModelAdmin):
	model = Resident

class VisitAdmin(admin.ModelAdmin):
	model = Visit


admin.site.register(Resident, ResidentAdmin)
admin.site.register(Visit, VisitAdmin)