from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from .serializers import *
from rest_framework.response import Response
from .models import *
from .send_bot import send_telegram_message, send_telegram_bug
from rest_framework.permissions import AllowAny
import json
from rest_framework.views import APIView
import requests
from django.http import JsonResponse
from .permission import HasAPIKey
from zoneinfo import ZoneInfo
from django.utils import timezone
from .tasks import send_message_consultation_telegram, send_message_synchronization_telegram




import telebot
from dotenv import load_dotenv
import os
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
load_dotenv()
API_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN, parse_mode=None)


def message_result(id: int, status: str, type: str, key: str) -> str:
    STATUS = {
        "Создание заявки": f"Ваш {type} с аббревиатурой *{key}* зарегистрирован ✅",
        "Проверка бага": f"Ваш {type} с аббревиатурой *{key}* на проверке у баг-менеджера 🔍",
        "Backlog": f"Ваш {type} с аббревиатурой *{key}* был добавлен в Беклог в IT-блоке 🗂️📌",
        "Selected for Development": f"Ваш {type} с аббревиатурой *{key}* был взят в спринт у IT-блока 📅🚀",
        "In Progress": f"Ваш {type} с аббревиатурой *{key}* в разработке у IT-блока 👩‍💻👨‍💻",
        "Review": f"Ваш {type} с аббревиатурой *{key}* на проверке у ТехЛида/Старшего разработчика 👨‍💻🔍",
        "Test": f"Ваш {type} с аббревиатурой *{key}* на проверке у команды тестирования 📝✅",
        "Ready to deploy": f"Ваш {type} с аббревиатурой *{key}* скоро будет решен 👨‍💻",
        "Done": f"Ваш {type} с аббревиатурой *{key}* был исправлен ✔️",
        "Ожидает IT-решения": f"Ваш {type} с аббревиатурой *{key}* требует архитектурных решений Продукта, решение займет большего времени 👨‍💻📝",
        "Ожидает продуктового решения": f"Ваш {type} с аббревиатурой *{key}* требует пересмотра бизнес-логики Продукта, решение займет большего времени 📝",
        "Отказано": f"Ваш {type} с аббревиатурой *{key}* не будет взят в работу. Ознакомьтесь с причинами ❌",
    }

    return STATUS.get(status, f"Ваш {type} с ID {id} с ключем {key} обновлен 📝. Статус (*{status}* ))""")




from django.core.exceptions import ObjectDoesNotExist
class TestModelPost(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):

        data = request.data
        print(json.dumps(data, indent=2, ensure_ascii=False))  # Для отладки

        lead_id_delete = data.get('leads[update][0][id]')
        lead_status = data.get('leads[update][0][status_id]')
        print(lead_id_delete)
        if lead_id_delete != None and lead_status == "142" :
            time_create = ResponseTimeCreate.objects.filter(leads_id=lead_id_delete)
            if time_create.exists():
                ResponseTimeDelete.objects.create(leads_id=lead_id_delete)
                synchronization = SupportSynchronization.objects.filter(leads_id = lead_id_delete)
                consultation = SupportConsultation.objects.filter(leads_id = lead_id_delete)
                if synchronization.exists():
                    support_synchronization_ct = ContentType.objects.get_for_model(SupportSynchronization)

                    qualitycontrol = QualityControl.objects.filter(content_type =support_synchronization_ct , object_id = synchronization.first().id)
                    if not qualitycontrol.exists():
                        menu = InlineKeyboardMarkup()
                        menu.row(
                            InlineKeyboardButton(text=f"Оценить качество Синхранизаций",
                                                 callback_data=f"rate_synchronization:{synchronization.first().id}")
                        )
                        bot.send_message(synchronization.first().personal_data.telegram_id, "Оцените качество обслуживания:", reply_markup=menu)
                if consultation.exists():
                    support_consultation_ct = ContentType.objects.get_for_model(SupportConsultation)
                    qualitycontrol = QualityControl.objects.filter(content_type = support_consultation_ct, object_id = consultation.first().id)
                    if not qualitycontrol.exists():
                        menu = InlineKeyboardMarkup()
                        menu.row(
                            InlineKeyboardButton(text=f"Оценить качество Консультаций",
                                                 callback_data=f"rate_consultation:{consultation.first().id}")
                        )
                        bot.send_message(consultation.first().personal_data.telegram_id, "Оцените качество обслуживания:", reply_markup=menu)
                return Response({'detail': 'Lead deleted'}, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        def find_matching_record(personal_data, lead_id):
            time_threshold = timezone.now() - timedelta(seconds=5)  # допустимый интервал времени создания
            # Ищем последние записи в разных моделях
            models = [SupportConsultation, SupportBug, SupportSynchronization, SupportGetCourse]
            for model in models:
                record = model.objects.filter(personal_data=personal_data, creation_date__gte=time_threshold,
                                                  leads_id__isnull=True).order_by('-creation_date').first()
                if record:
                    record.leads_id = lead_id
                    record.save()
                    return True
            return False

        lead_id = data.get('unsorted[add][0][lead_id]')
        client_telegram_id = data.get('unsorted[add][0][source_data][client][id]')
        print(f"Client Telegram ID: {client_telegram_id}, Lead ID: {lead_id}")
        if lead_id!=None or client_telegram_id!=None:
            try:
                personal_data = PersonalData.objects.get(telegram_id=client_telegram_id)
            except ObjectDoesNotExist:
                return Response({'detail': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
            if not ResponseTimeCreate.objects.filter(leads_id=lead_id).exists():
                if find_matching_record(personal_data, lead_id):
                    ResponseTimeCreate.objects.create(leads_id=lead_id)
                    return Response({'detail': 'Lead created'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'detail': 'No matching record found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'detail': 'Lead already exists'}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)
    # def post(self, request, *args, **kwargs):
    #     try:
    #         data = request.data.dict()
    #         print(json.dumps(data, indent=2, ensure_ascii=False))  # Для отладки
    #
    #         if 'leads[update][0][id]' in data:
    #             lead_id = data.get('leads[update][0][id]')
    #             print(lead_id)
    #             if not ResponseTimeCreate.objects.filter(leads_id=lead_id).exists():
    #                 ResponseTimeCreate.objects.create(leads_id=lead_id)
    #                 return Response({'detail': 'Lead created'}, status=status.HTTP_201_CREATED)
    #             return Response({'detail': 'Lead already exists'}, status=status.HTTP_200_OK)
    #
    #         elif 'leads[delete][0][id]' in data:
    #             lead_id = data.get('leads[delete][0][id]')
    #             ResponseTimeDelete.objects.create(leads_id=lead_id)
    #             return Response({'detail': 'Lead deleted'}, status=status.HTTP_201_CREATED)
    #
    #         return Response({'detail': 'Invalid webhook data'}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({'detail': f'Error processing request: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IssueCreatedWebhook(generics.GenericAPIView):
    queryset = WebhookIssueCreated.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = json.dumps(request.data, indent=2, ensure_ascii=False)
        instance = WebhookIssueCreated.objects.create(description=data)
        obj = json.loads(data)
        instance.issue_id = obj['issue']['id']
        instance.project_name = obj['issue']['fields']['project']['name']
        instance.status = obj['issue']['fields']['status']['name']
        instance.save()
        id = obj['issue']['fields'][f'{Settings.objects.first().telegram_filed}']
        # message = f"""Ваш {obj['issue']['fields']['issuetype']['name']} с ID {obj['issue']['id']} с ключем {obj['issue']['key']} зарегистрирован ✅. Статус (**{obj['issue']['fields'][('status')]['name']}** )"""
        message = f"""Ваш {obj['issue']['fields']['issuetype']['name']} с аббревиатурой {obj['issue']['key']} зарегистрирован ✅."""
        try:
            send_telegram_message(id, message)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


# class IssueUpdatedWebhook(generics.GenericAPIView):
#     queryset = WebhookIssueUpdated.objects.all()
#     permission_classes = (AllowAny, )
#
#
#     def post(self, request, *args, **kwargs):
#         data = json.dumps(request.data, indent=2, ensure_ascii=False)
#         instance = WebhookIssueUpdated.objects.create(description=data)
#         #data = WebhookIssueUpdated.objects.get(id=1).description
#         obj = json.loads(data)
#         instance.issue_id = obj['issue']['id']
#         instance.project_name =obj['issue']['fields']['project']['name']
#         instance.status =obj['issue']['fields']['status']['name']
#         instance.save()
#
#         id = obj['issue']['fields'][f'{Settings.objects.first().telegram_filed}']
#         message = f"""Ваш {obj['issue']['fields']['issuetype']['name']} с ID {obj['issue']['id']} с ключем {obj['issue']['key']} обновлен 📝. Статус (*{obj['issue']['fields'][('status')]['name']}* ))"""
#         try:
#             send_telegram_message(id, message)
#             return Response(status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


from datetime import timedelta
import datetime
import pytz


class IssueUpdatedWebhook(generics.GenericAPIView):
    queryset = WebhookIssueUpdated.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = json.dumps(request.data, indent=2, ensure_ascii=False)
        obj = json.loads(data)

        # Проверка на уникальность события
        issue_id = obj['issue']['id']
        project_name = obj['issue']['fields']['project']['name']
        status_name = obj['issue']['fields']['status']['name']

        timestamp_text = str(obj['timestamp'])  # Получаем timestamp как текст

        tz = pytz.timezone('Asia/Almaty')
        timestamp_datetime = datetime.datetime.utcfromtimestamp(int(timestamp_text) / 1000.0)
        timestamp_datetime = timestamp_datetime.replace(tzinfo=pytz.utc).astimezone(tz)

        # Переводим timestamp_datetime обратно в UTC, чтобы сравнить с created_at
        timestamp_utc = timestamp_datetime.astimezone(pytz.utc)

        # Определяем временной интервал для поиска дубликатов в UTC
        start_time = timestamp_utc - datetime.timedelta(seconds=3)
        end_time = timestamp_utc + datetime.timedelta(seconds=3)
        webhookupdate = WebhookIssueUpdated.objects.filter(issue_id=issue_id, status=status_name,
                                                           created_at__range=(start_time, end_time))
        # Проверяем, существует ли уже запись с таким же issue_id и timestamp/status
        if not webhookupdate.exists():
            instance = WebhookIssueUpdated.objects.create(description=data)
            instance.issue_id = issue_id
            instance.project_name = project_name
            instance.status = status_name
            # Если используете timestamp, сохраните его в модели
            instance.timestamp = timestamp_text
            instance.save()

            id = obj['issue']['fields'][f'{Settings.objects.first().telegram_filed}']
            message = message_result(issue_id, status_name, obj['issue']['fields']['issuetype']['name'],
                                     obj['issue']['key'])
            # = f"""Ваш {obj['issue']['fields']['issuetype']['name']} с ID {issue_id} с ключем {obj['issue']['key']} обновлен 📝. Статус (*{status_name}* ))"""
            try:
                if (obj['issue_event_type_name'] == 'issue_generic'):
                    send_telegram_message(id, message)
                    if status_name=='Done' or status_name=='Отказано':
                        send_telegram_bug(id)
                    return Response(status=status.HTTP_200_OK)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            webhookupdate.first().delete()
            # Запись существует, игнорируем дубликат
            return JsonResponse({'message': 'Event already processed'}, status=status.HTTP_200_OK)


class IssueDeletedWebhook(generics.GenericAPIView):
    queryset = WebhookIssueDeleted.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = json.dumps(request.data, indent=2, ensure_ascii=False)
        instance = WebhookIssueDeleted.objects.create(description=data)
        obj = json.loads(data)
        instance.issue_id = obj['issue']['id']
        instance.project_name = obj['issue']['fields']['project']['name']
        instance.status = obj['issue']['fields']['status']['name']
        instance.save()
        id = obj['issue']['fields'][f'{Settings.objects.first().telegram_filed}']
        # message = f"""Ваш {obj['issue']['fields']['issuetype']['name']} с ID {obj['issue']['id']} с ключем {obj['issue']['key']} удалено ❌ со статусом (**{obj['issue']['fields'][('status')]['name']}** )"""
        message = f"""Ваш {obj['issue']['fields']['issuetype']['name']} с аббревиатурой {obj['issue']['key']} удален ❌."""
        try:
            send_telegram_message(id, message)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


class AmoCrmWebhook(generics.GenericAPIView):
    queryset = AmoCrmWebhookModel.objects.all()
    serializer_class = AmoCrmWebhookModelSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        pass
        # telegram = requests.post('https://pay.ziz.kz/api/webhook/amo_crm', json = request.data)
        # telegram = requests.post('https://umag.ziz.kz/api/webhook/amo_crm', json = request.data)
        # telegram = requests.post('https://pay.ziz.kz/api/bot', json = request.data)
        # requests.post('https://amojo.amocrm.ru/~external/hooks/telegram?t=6397638357:AAEF4kljx7MgkA56vx5jTbB-lAjWkLVLVk4', json = request.data)
        # data = json.dumps(request.data, indent=2, ensure_ascii=False)
        AmoCrmWebhookModel.objects.create(description=request.data)
        return Response(status=status.HTTP_200_OK)


class AccessTokenApi(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = KeySerializer

    def post(self, request, *args, **kwargs):
        serializer = KeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if serializer.data['key'] == Settings.objects.first().amo_secret_key:
                return Response({'access_token': RefreshAccessToken.objects.first().access_token},
                                status=status.HTTP_200_OK)
            return Response({"detail": "Ваш ключь не актуален или не верен"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PersonalDataCreateAPIView(generics.CreateAPIView):
    permission_classes = [HasAPIKey,]
    queryset = PersonalData.objects.all()
    serializer_class = PersonalDataSerializer
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckTelegramIDAPIView(APIView):
    permission_classes = [HasAPIKey,]
    def get_queryset(self):
        return PersonalData.objects.all()
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ],
        responses={200: PersonalDataSerializer(many=False)}
    )
    def get(self, request, telegram_id):
        try:
            personal_data = PersonalData.objects.get(telegram_id=telegram_id)
            serializer = PersonalDataSerializer(personal_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PersonalData.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


class PersonalDataUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [HasAPIKey, ]
    queryset = PersonalData.objects.all()
    serializer_class = PersonalDataSerializer
    lookup_field = 'telegram_id'
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class SupportConsultationApi(generics.GenericAPIView):
    permission_classes = [HasAPIKey,]
    serializer_class = SupportConsultationSaveSerializer
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SupportBugApi(generics.GenericAPIView):
    permission_classes = [HasAPIKey,]
    serializer_class = SupportBugSaveSerializer
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SupportSynchronizationApi(generics.GenericAPIView):
    permission_classes = [HasAPIKey,]
    serializer_class = SupportSynchronizationSaveSerializer
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupportGetCourseApi(generics.GenericAPIView):
    permission_classes = [HasAPIKey,]
    serializer_class = SupportGetCourseSaveSerializer
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from django.shortcuts import render
from django.core.serializers import serialize



def analytics_view(request):
    personal_data = PersonalData.objects.all()
    support_consultations = SupportConsultation.objects.all()
    support_bugs = SupportBug.objects.all()
    support_synchronizations = SupportSynchronization.objects.all()
    support_get_courses = SupportGetCourse.objects.all()

    context = {
        'personal_data': serialize('json', personal_data),
        'support_consultations': serialize('json', support_consultations),
        'support_bugs': serialize('json', support_bugs),
        'support_synchronizations': serialize('json', support_synchronizations),
        'support_get_courses': serialize('json', support_get_courses)
    }

    return render(request, 'analytics.html', context)


def get_consultation_data(leads_id):
    consultation_data = []
    verbose_names = {}

    if SupportConsultation.objects.filter(leads_id=leads_id).exists():
        consultation_data = list(SupportConsultation.objects.filter(leads_id=leads_id).values())
        verbose_names = get_field_verbose_names(SupportConsultation)
        for data in consultation_data:
            data['type'] = 'SupportConsultation'
            data['verbose_name'] = 'Консультация'
            data['verbose_names'] = verbose_names
    elif SupportBug.objects.filter(leads_id=leads_id).exists():
        consultation_data = list(SupportBug.objects.filter(leads_id=leads_id).values())
        verbose_names = get_field_verbose_names(SupportBug)
        for data in consultation_data:
            data['type'] = 'SupportBug'
            data['verbose_name'] = 'Баг'
            data['verbose_names'] = verbose_names
    elif SupportSynchronization.objects.filter(leads_id=leads_id).exists():
        consultation_data = list(SupportSynchronization.objects.filter(leads_id=leads_id).values())
        verbose_names = get_field_verbose_names(SupportSynchronization)
        for data in consultation_data:
            data['type'] = 'SupportSynchronization'
            data['verbose_name'] = 'Синхронизация'
            data['verbose_names'] = verbose_names
    elif SupportGetCourse.objects.filter(leads_id=leads_id).exists():
        consultation_data = list(SupportGetCourse.objects.filter(leads_id=leads_id).values())
        verbose_names = get_field_verbose_names(SupportGetCourse)
        for data in consultation_data:
            data['type'] = 'SupportGetCourse'
            data['verbose_name'] = 'Получение курса'
            data['verbose_names'] = verbose_names
    return consultation_data


def get_field_verbose_names(model):
    return {field.name: field.verbose_name for field in model._meta.fields}


def analytics_lead_time_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    model_filter = request.GET.get('model_filter')

    deals = ResponseTimeDelete.objects.all()
    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        deals = deals.filter(creation_date__range=(start_date, end_date))

    if model_filter:
        if model_filter == 'SupportConsultation':
            deals = deals.filter(leads_id__in=SupportConsultation.objects.values_list('leads_id', flat=True))
        elif model_filter == 'SupportBug':
            deals = deals.filter(leads_id__in=SupportBug.objects.values_list('leads_id', flat=True))
        elif model_filter == 'SupportSynchronization':
            deals = deals.filter(leads_id__in=SupportSynchronization.objects.values_list('leads_id', flat=True))
        elif model_filter == 'SupportGetCourse':
            deals = deals.filter(leads_id__in=SupportGetCourse.objects.values_list('leads_id', flat=True))

    paginator = Paginator(deals, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    closure_times = []
    daily_closure_data = {}
    total_hours_sum = 0
    deal_count = 0

    for deal in page_obj:
        closure_time = deal.get_closure_time
        if closure_time:
            days, hours, minutes = closure_time
            total_hours = days * 24 + hours + minutes / 60
            total_hours_sum += total_hours
            deal_count += 1
            consultation_data = get_consultation_data(deal.leads_id)
            closure_times.append({
                'leads_id': deal.leads_id,
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'creation_date': deal.creation_date.strftime('%Y-%m-%d'),
                'total_hours': total_hours,
                'consultation_data': consultation_data
            })

            creation_date = deal.creation_date.strftime('%Y-%m-%d')
            if creation_date not in daily_closure_data:
                daily_closure_data[creation_date] = 0
            daily_closure_data[creation_date] += total_hours

    daily_closure_data = dict(sorted(daily_closure_data.items()))

    closure_times_serialized = json.dumps(closure_times, default=str)
    daily_closure_data_serialized = json.dumps(daily_closure_data, default=str)

    average_time = total_hours_sum / deal_count if deal_count > 0 else 0

    context = {
        'page_obj': page_obj,
        'closure_times': closure_times,
        'daily_closure_data': daily_closure_data_serialized,
        'average_time': round(average_time, 2),
        'closure_times_json': closure_times_serialized,
        'model_filter': model_filter,
    }

    return render(request, 'analytics_lead_time_view.html', context)


from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from .models import PersonalData, SupportBug, QualityControl



class UnratedBugsView(ListAPIView):
    serializer_class = SupportBugSaveSerializer
    permission_classes = [HasAPIKey, ]
    def get_queryset(self):
        telegram_id = self.kwargs['telegram_id']
        personal_data = get_object_or_404(PersonalData, telegram_id=telegram_id)
        rated_bugs_ids = QualityControl.objects.filter(content_type__model='supportbug').values_list('object_id', flat=True)
        unrated_bugs = SupportBug.objects.filter(personal_data=personal_data).exclude(id__in=rated_bugs_ids)
        return unrated_bugs
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UnratedConsultationView(ListAPIView):
    serializer_class = SupportConsultationSaveSerializer
    permission_classes = [HasAPIKey, ]
    def get_queryset(self):
        telegram_id = self.kwargs['telegram_id']
        personal_data = get_object_or_404(PersonalData, telegram_id=telegram_id)
        rated_consultation_ids = QualityControl.objects.filter(content_type__model='supportconsultation').values_list('object_id', flat=True)
        unrated_bugs = SupportConsultation.objects.filter(personal_data=personal_data).exclude(id__in=rated_consultation_ids)
        return unrated_bugs
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UnratedSynchronizationView(ListAPIView):
    serializer_class = SupportSynchronizationSaveSerializer
    permission_classes = [HasAPIKey, ]
    def get_queryset(self):
        telegram_id = self.kwargs['telegram_id']
        personal_data = get_object_or_404(PersonalData, telegram_id=telegram_id)
        rated_synchronization_ids = QualityControl.objects.filter(content_type__model='supportsynchronization').values_list('object_id', flat=True)
        unrated_bugs = SupportSynchronization.objects.filter(personal_data=personal_data).exclude(id__in=rated_synchronization_ids)
        return unrated_bugs
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QualityControlCreateView(generics.GenericAPIView):
    queryset = QualityControl.objects.all()
    serializer_class = QualityControlCreateSerializer
    permission_classes = [HasAPIKey, ]

    def post(self, request, *args, **kwargs):
        # Получаем content_type по переданному model_name
        model_name = request.data.get('model_name')
        if not model_name:
            return Response({"error": "model_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type = ContentType.objects.get(model=model_name)
        except ContentType.DoesNotExist:
            return Response({"error": "Invalid model_name"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['content_type'] = content_type.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()




from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from datetime import datetime as analistyc_datetime
import openpyxl
from django.http import HttpResponse
def export_to_excel(reviews):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Отзывы'

    # Заголовки столбцов
    headers = ['ID', 'Тип контента', 'Оценка', 'Дата создания', 'Имя пользователя', 'Наименование франшизы']
    sheet.append(headers)

    # Данные
    for review in reviews:
        # Получаем данные о связанном объекте
        related_object = review.content_object

        personal_data = related_object.personal_data
        first_name = personal_data.first_name
        franchise_name = personal_data.franchise_name



        row = [
            review.id,
            review.content_type.model,
            review.rating,
            review.creation_date.strftime('%Y-%m-%d'),
            first_name,
            franchise_name
        ]
        sheet.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=quality_control_reviews.xlsx'
    workbook.save(response)
    return response

def quality_control_analytics(request):
    # Средняя оценка
    avg_rating = QualityControl.objects.aggregate(Avg('rating'))['rating__avg']

    # Данные для графика
    ratings = QualityControl.objects.values('rating').annotate(count=Count('rating')).order_by('rating')

    # Средняя оценка и количество отзывов по каждому типу контента
    content_types = QualityControl.objects.values('content_type', 'content_type__model').annotate(
        avg_rating=Avg('rating'),
        count_reviews=Count('id')
    ).order_by('content_type')

    # Получение verbose_name для типов контента
    for content_type in content_types:
        model = ContentType.objects.get(id=content_type['content_type']).model_class()
        content_type['verbose_name'] = model._meta.verbose_name

    # Фильтрация по типу контента, времени и поисковому запросу
    content_type_filter = request.GET.get('content_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    all_reviews = QualityControl.objects.all()

    if content_type_filter:
        all_reviews = all_reviews.filter(content_type__model=content_type_filter)

    if start_date:
        start_date = analistyc_datetime.strptime(start_date, '%Y-%m-%d')
        all_reviews = all_reviews.filter(creation_date__gte=start_date)

    if end_date:
        end_date = analistyc_datetime.strptime(end_date, '%Y-%m-%d')
        all_reviews = all_reviews.filter(creation_date__lte=end_date)

    # Проверка на экспорт в Excel
    if request.GET.get('export') == 'excel':
        return export_to_excel(all_reviews)

    # Пагинация
    paginator = Paginator(all_reviews, 10)  # Показываем 10 отзывов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'avg_rating': avg_rating,
        'ratings': list(ratings),
        'content_types': content_types,
        'page_obj': page_obj,
        'content_type_filter': content_type_filter,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'quality_control_analytics.html', context)





class QualityControlConsultationPeriodApi(generics.GenericAPIView):
    serializer_class = SupportConsultationSerializer
    permission_classes = [HasAPIKey, ]

    def get_queryset(self):
        return SupportConsultation.objects.none()
    @swagger_auto_schema(
        operation_description="",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'telegram_id': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram ID пользователя'),
                'support_consultation_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID консультации')
            },
            required=['telegram_id', 'support_consultation_id']
        ),
        responses={
            200: openapi.Response(description='Успешный ответ', examples={
                'application/json': {'support_consultation_id': 1}
            }),
            409: openapi.Response(description='Оценка уже существует'),
        }
    )
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        support_consultation_id = request.data.get('support_consultation_id')
        now = timezone.now()
        result_time = now + timedelta(days=2)
        result_time_aware = result_time.astimezone(ZoneInfo("Asia/Qyzylorda"))
        #send_message_consultation_telegram.apply_async((support_consultation_id, telegram_id), eta=result_time_aware)
        return Response({"support_consultation_id": support_consultation_id}, status=status.HTTP_200_OK)



class QualityControlSynchronizationPeriodApi(generics.GenericAPIView):
    serializer_class = SupportConsultationSerializer
    permission_classes = [HasAPIKey, ]

    def get_queryset(self):
        return SupportConsultation.objects.none()
    @swagger_auto_schema(
        operation_description="",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'telegram_id': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram ID пользователя'),
                'support_synchronization_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID Синхранизаций')
            },
            required=['telegram_id', 'support_synchronization_id']
        ),
        responses={
            200: openapi.Response(description='Успешный ответ', examples={
                'application/json': {'support_synchronization_id': 1}
            }),
            409: openapi.Response(description='Оценка уже существует'),
        }
    )
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        support_synchronization_id = request.data.get('support_synchronization_id')
        now = timezone.now()
        result_time = now + timedelta(days=2)
        result_time_aware = result_time.astimezone(ZoneInfo("Asia/Qyzylorda"))
        #send_message_synchronization_telegram.apply_async((support_synchronization_id, telegram_id), eta=result_time_aware)
        return Response({"support_synchronization_id": support_synchronization_id}, status=status.HTTP_200_OK)



class WebhookAmoCrm():
    pass