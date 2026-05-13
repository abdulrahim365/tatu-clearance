from django.contrib import admin

from .models import Unit, ClearanceRequest, ClearanceStep

# Register your models here.

admin.site.site_header = "Tamale Technical University (TaTu) Administration"
admin.site.site_title = "TaTu Admin"
admin.site.index_title = "Clearance System Administration"


from .models import Unit, ClearanceRequest, ClearanceStep


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)
    search_fields = ('name',)


@admin.register(ClearanceRequest)
class ClearanceRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'applied_date', 'status', 'is_complete')
    list_filter = ('status', 'applied_date')
    search_fields = ('student__username', 'student__student_profile__student_id')
    readonly_fields = ('applied_date', 'completed_date')
    date_hierarchy = 'applied_date'


@admin.register(ClearanceStep)
class ClearanceStepAdmin(admin.ModelAdmin):
    list_display = ('request', 'unit', 'status', 'approver', 'approved_date')
    list_filter = ('status', 'unit')
    search_fields = ('request__student__username', 'unit__name')
    readonly_fields = ('approved_date',)
    raw_id_fields = ('request', 'approver')



    


    



