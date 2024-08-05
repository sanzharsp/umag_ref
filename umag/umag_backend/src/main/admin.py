from unfold.contrib.import_export.forms import ExportForm, ImportForm
from import_export.admin import ImportExportModelAdmin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin, StackedInline
from django.contrib.auth.models import User
from django.contrib import admin


class SupportConsultationInline(StackedInline):  # или admin.StackedInline
    model = SupportConsultation
    extra = 0
    readonly_fields = ('creation_date',)


class SupportBugInline(StackedInline):  # или admin.StackedInline
    model = SupportBug
    extra = 0
    readonly_fields = ('creation_date',)


class SupportSynchronizationInline(StackedInline):  # или admin.StackedInline
    model = SupportSynchronization
    extra = 0
    readonly_fields = ('creation_date',)


class SupportGetCourseInline(StackedInline):  # или admin.StackedInline
    model = SupportGetCourse
    extra = 0
    readonly_fields = ('creation_date',)


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


class SupportConsultationAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('personal_data', 'creation_date')
    list_filter = ('creation_date',)
    search_fields = ('description_problem',)
    readonly_fields = ('creation_date',)


class SettingsModelAdmin(ModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    def has_add_permission(self, request):
        # Разрешить добавление, только если записей еще нет
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Опционально: запретить удаление
        return False

    def has_change_permission(self, request, obj=None):
        # Опционально: разрешить изменение только если уже есть запись
        return Settings.objects.exists()


class RefreshAccessTokenAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('created_at', 'updated_at',)

    def has_add_permission(self, request):
        # Разрешить добавление, только если записей еще нет
        return not RefreshAccessToken.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Опционально: запретить удаление
        return False

    def has_change_permission(self, request, obj=None):
        # Опционально: разрешить изменение только если уже есть запись
        return RefreshAccessToken.objects.exists()


class WebhookIssueCreatedAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('created_at', 'issue_id', 'project_name', 'status', 'id',)
    list_per_page = 25
    list_max_show_all = 1000


class WebhookIssueUpdatedAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('created_at', 'issue_id', 'project_name', 'status', 'id',)
    list_per_page = 25
    list_max_show_all = 1000


class WebhookIssueDeletedAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('created_at', 'issue_id', 'project_name', 'status', 'id',)
    list_per_page = 25
    list_max_show_all = 1000


class SupportBugAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('bug_name', 'creation_date',)
    list_per_page = 25
    list_max_show_all = 1000
    readonly_fields = ('creation_date',)


class PersonalDatadAdmin(ModelAdmin, ImportExportModelAdmin):
    inlines = [SupportConsultationInline, SupportBugInline, SupportSynchronizationInline, SupportGetCourseInline, ]
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('telegram_id', 'first_name', 'franchise_name', 'phone_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('telegram_id', 'first_name', 'franchise_name', 'phone_number',)
    readonly_fields = ('created_at',)


class SupportGetCourseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('personal_data', 'email', 'study_type', 'creation_date')
    list_filter = ('creation_date',)
    search_fields = ('email',)
    readonly_fields = ('creation_date',)


class SupportSynchronizationAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('personal_data', 'creation_date')
    list_filter = ('creation_date',)
    search_fields = ('all_messages',)
    readonly_fields = ('creation_date',)


class QualityControlAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('content_type', 'content_object', 'object_id', 'rating', 'creation_date')


class ResponseTimeCreateAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    readonly_fields = ('creation_date',)
    list_display = ('leads_id', 'creation_date')


class ResponseTimeDeleteAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    readonly_fields = ('creation_date',)
    list_display = ('leads_id', 'creation_date')


admin.site.register(SupportConsultation, SupportConsultationAdmin)
admin.site.register(SupportSynchronization, SupportSynchronizationAdmin)
admin.site.register(Settings, SettingsModelAdmin)
admin.site.register(RefreshAccessToken, RefreshAccessTokenAdmin)
admin.site.register(WebhookIssueCreated, WebhookIssueCreatedAdmin)
admin.site.register(WebhookIssueUpdated, WebhookIssueUpdatedAdmin)
admin.site.register(AmoCrmWebhookModel)
admin.site.register(WebhookIssueDeleted, WebhookIssueDeletedAdmin)
admin.site.register(PersonalData, PersonalDatadAdmin)
admin.site.register(SupportBug, SupportBugAdmin)
admin.site.register(SupportGetCourse, SupportGetCourseAdmin)
admin.site.register(QualityControl, QualityControlAdmin)

admin.site.register(ResponseTimeCreate, ResponseTimeCreateAdmin)
admin.site.register(ResponseTimeDelete, ResponseTimeDeleteAdmin)

admin.site.register(TestModel)
