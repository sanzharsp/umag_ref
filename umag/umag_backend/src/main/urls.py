from django.urls import path
from .views import *

urlpatterns = [

    path('webhook/', TestModelPost.as_view()),
    path('webhook/issue_created', IssueCreatedWebhook.as_view()),
    path('webhook/issue_updated', IssueUpdatedWebhook.as_view()),
    path('webhook/issue_deleted', IssueDeletedWebhook.as_view()),
    path('webhook/amo_crm', AmoCrmWebhook.as_view()),
    path('register', PersonalDataCreateAPIView.as_view()),
    path('personaldata/check/<str:telegram_id>', CheckTelegramIDAPIView.as_view(), name='personaldata-check'),
    path('token/get', AccessTokenApi.as_view()),
    path('personaldata/update/<str:telegram_id>', PersonalDataUpdateAPIView.as_view(), name='personaldata-update'),
    path('consultation/create', SupportConsultationApi.as_view(), name='consultation-create'),
    path('bug/create', SupportBugApi.as_view(), name='bug-create'),
    path('synchronization/create', SupportSynchronizationApi.as_view(), name='synchronization-create'),
    path('get_course/create', SupportGetCourseApi.as_view(), name='get_course-create'),
    path('analytics/', analytics_view, name='analytics'),

    path('unrated-bugs/<str:telegram_id>/', UnratedBugsView.as_view(), name='unrated-bugs'),
    path('unrated-consultation/<str:telegram_id>/', UnratedConsultationView.as_view(), name='unrated-consultation'),
    path('unrated-synchronization/<str:telegram_id>/', UnratedSynchronizationView.as_view(), name='unrated-synchronization'),
    path('quality-control/', QualityControlCreateView.as_view(), name='quality-control-create'),
    path('quality-control-period/consultation', QualityControlConsultationPeriodApi.as_view(), name='quality-control-period-consultation'),
    path('quality-control-period/synchronization', QualityControlSynchronizationPeriodApi.as_view(), name='quality-control-period-synchronization'),

    path('', quality_control_analytics, name='quality_control_analytics'),


    path('analytics_lead/', analytics_lead_time_view, name='analytics_lead'),
]
