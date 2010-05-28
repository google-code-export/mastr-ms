from madas.repository.models import *
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.webhelpers import url
from django.core import urlresolvers

class OrganAdmin(admin.ModelAdmin):
    list_display = ('name', 'detail')
    search_fields = ['name']

class BiologicalSourceAdmin(admin.ModelAdmin):
    list_display = ('type',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_on', 'experiments_link')
    search_fields = ['title']

    def experiments_link(self, obj):
        change_url = urlresolvers.reverse('admin:repository_experiment_changelist')
        return '<a href="%s?project__id__exact=%s">Experiments</a>' % (change_url, obj.id)
    experiments_link.short_description = 'Experiments'
    experiments_link.allow_tags = True


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'comment', 'status', 'created_on', 'formal_quote', 'job_number', 'project', 'instrument_method', 'samples_link']
    search_fields = ['title', 'job_number']

    def samples_link(self, obj):
        change_url = urlresolvers.reverse('admin:repository_sample_changelist')
        return '<a href="%s?experiment__id__exact=%s">Samples</a>' % (change_url, obj.id)
    samples_link.short_description = 'Samples'
    samples_link.allow_tags = True


class ExperimentStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ['name']

class AnimalInfoAdmin(admin.ModelAdmin):
    list_display = ('sex', 'age', 'parental_line')

class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('name','description')

class SampleAdmin(admin.ModelAdmin):
    list_display = ['label', 'experiment', 'comment', 'weight', 'sample_class', 'logs_link']
    search_fields = ['label', 'experiment__title', 'sample_class__organ__name']
    actions = ['create_run']

    def create_run(self, request, queryset):

        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)

        im, created = InstrumentMethod.objects.get_or_create(title="Default Method", creator=request.user)
        r = Run(method=im, creator=request.user, title="New Run")
        r.save() # need id before we can add many-to-many

        for sample_id in selected:
            s = Sample.objects.get(id=sample_id)
            rs = RunSample(run=r, sample=s)
            rs.save()

        change_url = urlresolvers.reverse('admin:repository_run_change', args=(r.id,))
        return HttpResponseRedirect(change_url)

    create_run.short_description = "Create Run from samples."

    def logs_link(self, obj):
        change_url = urlresolvers.reverse('admin:repository_samplelog_changelist')
        return '<a href="%s?sample__id__exact=%s">Logs</a>' % (change_url, obj.id)
    logs_link.short_description = 'Logs'
    logs_link.allow_tags = True    


class SampleTimelineAdmin(admin.ModelAdmin):
    list_display = ('id', 'timeline')
    
class InstrumentMethodAdmin(admin.ModelAdmin):
    list_display = ['title', 'method_path', 'method_name', 'version', 'creator', 'created_on', 'randomisation', 'blank_at_start',
                    'blank_at_end', 'blank_position', 'obsolete', 'obsolescence_date', 'run_link']

    def run_link(self, obj):
        change_url = urlresolvers.reverse('admin:repository_run_changelist')
        return '<a href="%s?method__id__exact=%s">Runs</a>' % (change_url, obj.id)
    run_link.short_description = 'Runs'
    run_link.allow_tags = True


class StandardOperationProcedureAdmin(admin.ModelAdmin):
    list_display = ('responsible', 'label', 'area_where_valid', 'comment', 'organisation', 'version', 'defined_by', 'replaces_document', 'content', 'attached_pdf')

class OrganismTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    
class UserExperimentAdmin(admin.ModelAdmin):
    list_display = ('user', 'experiment', 'type')   

class UserInvolvementTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')   

class PlantInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'development_stage')
    
class SampleClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'experiment', 'biological_source', 'treatments', 'timeline', 'organ', 'enabled']
    search_fields = ['experiment__title']

class SampleLogAdmin(admin.ModelAdmin):
    list_display = ['type', 'description', 'user', 'sample']
    search_fields = ['description']

class RunAdmin(admin.ModelAdmin):
    list_display = ['title', 'method', 'creator', 'created_on']
    search_fields = ['title', 'method__title', 'creator__username', 'creator__first_name', 'creator__last_name']
    raw_id_fields = ['samples']
    

admin.site.register(OrganismType, OrganismTypeAdmin)
admin.site.register(UserInvolvementType, UserInvolvementTypeAdmin)
admin.site.register(Organ, OrganAdmin)
admin.site.register(BiologicalSource, BiologicalSourceAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(InstrumentMethod, InstrumentMethodAdmin)
admin.site.register(ExperimentStatus, ExperimentStatusAdmin)
admin.site.register(AnimalInfo, AnimalInfoAdmin)
admin.site.register(Treatment, TreatmentAdmin)
admin.site.register(Sample,SampleAdmin)
admin.site.register(SampleTimeline,SampleTimelineAdmin)
admin.site.register(StandardOperationProcedure,StandardOperationProcedureAdmin)
admin.site.register(UserExperiment,UserExperimentAdmin)
admin.site.register(PlantInfo, PlantInfoAdmin)
admin.site.register(SampleClass, SampleClassAdmin)
admin.site.register(SampleLog, SampleLogAdmin)
admin.site.register(Run, RunAdmin)
