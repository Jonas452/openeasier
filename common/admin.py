from django.contrib import admin

from .models import *


admin.site.register(CKANInstance)
admin.site.register(DBColumn)
admin.site.register(DBConfig)
admin.site.register(DBSchema)
admin.site.register(DBTable)
admin.site.register(UserSchema)
