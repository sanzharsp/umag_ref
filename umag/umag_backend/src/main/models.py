from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class SingletonModel(models.Model):
    # Ваши поля здесь

    def save(self, *args, **kwargs):
        if not self.pk and SingletonModel.objects.exists():
            # Если вы пытаетесь сохранить новый объект, когда уже существует один, выбросите исключение
            raise ValidationError('There can be only one SingletonModel instance')
        return super(SingletonModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True  # Это делает модель абстрактной, чтобы она не создавала отдельную таблицу в базе данных




class Settings(models.Model):
    telegram_filed = models.CharField(verbose_name="Название поля для телеграм", max_length=255)
    username = models.CharField(verbose_name="Название пользователя jira", max_length= 100)
    api_token = models.TextField(verbose_name="Токен аккаунта jira")
    jira_url = models.URLField(verbose_name="Ссылка на базовый путь проекта")
    amo_id = models.TextField(verbose_name="ID интеграций")
    amo_secret_key = models.TextField(verbose_name="Секретный ключь")
    amo_auth_key = models.TextField(verbose_name="Код авторизаций")
    redirect_url = models.URLField(verbose_name="Путь перенаправления")
    subdomain = models.CharField(max_length=120, verbose_name="Субдомен в АМО СРМ")

    def __str__(self):
        return f"{self.telegram_filed}"

    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настойки"




class WebhookIssueCreated(models.Model):
    issue_id = models.CharField( max_length=255, verbose_name="Идентификатор")
    project_name = models.TextField(verbose_name="Название проекта")
    status = models.CharField(max_length=255, verbose_name="Статус", blank=True, null=True)
    description = models.TextField(blank=True, verbose_name="ответ на вебхук")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    def __str__(self):
        return f"{self.id} "

    class Meta:
        verbose_name = "Создание проблемы"
        verbose_name_plural = "Создание проблемы"



class WebhookIssueUpdated(models.Model):
    issue_id = models.CharField( max_length=255, verbose_name="Идентификатор")
    project_name = models.TextField(verbose_name="Название проекта")
    status = models.CharField(max_length=255, verbose_name="Статус", blank=True, null=True)
    description = models.TextField(blank=True, verbose_name="ответ на вебхук")
    timestamp = models.TextField(verbose_name="Дата и время создания", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    def __str__(self):
        return f"{self.id} "

    class Meta:
        verbose_name = "Проблема обновлена"
        verbose_name_plural = "Проблема обновлена"

class WebhookIssueDeleted(models.Model):
    issue_id = models.CharField( max_length=255, verbose_name="Идентификатор")
    project_name = models.TextField(verbose_name="Название проекта")
    status = models.CharField(max_length=255, verbose_name="Статус", blank=True, null=True)

    description = models.TextField(blank=True, verbose_name="ответ на вебхук")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    def __str__(self):
        return f"{self.id} "

    class Meta:
        verbose_name = "Проблема удалена"
        verbose_name_plural = "Проблема удалена"


class AmoCrmWebhookModel(models.Model):
    description = models.TextField(blank=True, verbose_name="ответ на вебхук")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    def __str__(self):
        return f"{self.id} "

    class Meta:
        verbose_name = "Webhook Amo crm"
        verbose_name_plural = "Webhook Amo crm"

class RefreshAccessToken(models.Model):
    access_token = models.TextField(verbose_name="Токен доступа")
    refresh_token = models.TextField(verbose_name="Токен обновления")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = "Токен доступа и обновления"
        verbose_name_plural = "Токен доступа и обновления"

class PersonalData(models.Model):
    telegram_id = models.CharField(verbose_name="id пользователя в телеграмм", unique=True, max_length=255)
    first_name = models.CharField(max_length=100, db_index=True, verbose_name="Имя пользователя")
    franchise_name = models.CharField(max_length=100, verbose_name="Наименование франшизы")
    phone_number = models.CharField(max_length=15, verbose_name="Номер телефона")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления")

    def __str__(self):
        return f"{self.first_name}, {self.franchise_name}"
    class Meta:
        verbose_name = "Персональные данные"
        verbose_name_plural = "Персональные данные"


class SupportConsultation(models.Model):
    personal_data = models.ForeignKey(PersonalData,verbose_name="Клиент", on_delete=models.CASCADE)
    description_problem = models.TextField(verbose_name="Описание проблемы")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    leads_id = models.CharField(max_length=255, verbose_name="Идентификатор сделки", null=True, blank=True)

    def __str__(self):
        return f"Консультация | {self.personal_data}"

    class Meta:
        verbose_name = " объект 'Консультация'"
        verbose_name_plural = "Консультации"

class SupportBug(models.Model):
    personal_data = models.ForeignKey(PersonalData,verbose_name="Клиент", on_delete=models.CASCADE)
    bug_name= models.CharField(max_length=255, blank=True, verbose_name="Название бага", null=True)
    description_and_scenario = models.TextField(verbose_name="Описание и сценарий", blank=True, null=True)
    additional_information = models.TextField(verbose_name="Дополнительная информация", blank=True, null=True)
    app_version = models.TextField(verbose_name="Версия приложения", blank=True, null=True)
    personal_account_access = models.TextField(verbose_name="Доступ от личного кабинета", blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    leads_id = models.CharField(max_length=255, verbose_name="Идентификатор сделки", null=True, blank=True)

    def __str__(self):
        return f"Баг | {self.personal_data}"

    class Meta:
        verbose_name = " объект 'Баг'"
        verbose_name_plural = "Баги"


class SupportSynchronization(models.Model):
    personal_data = models.ForeignKey(PersonalData,verbose_name="Клиент", on_delete=models.CASCADE)
    all_messages = models.TextField(verbose_name="Детали")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    leads_id = models.CharField(max_length=255, verbose_name="Идентификатор сделки", null=True, blank=True)

    def __str__(self):
        return f"Синхронизация | {self.personal_data}"

    class Meta:
        verbose_name = " объект 'Синхранизация'"
        verbose_name_plural = "Синхранизаций"



class SupportGetCourse(models.Model):
    personal_data = models.ForeignKey(PersonalData,verbose_name="Клиент", on_delete=models.CASCADE)
    email = models.CharField(verbose_name="Email", max_length=255)
    study_type = models.CharField(verbose_name="Вид обучения", max_length=60)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    leads_id = models.CharField(max_length=255, verbose_name="Идентификатор сделки", null=True, blank=True)

    def __str__(self):
        return f"Get Course | {self.personal_data}"

    class Meta:
        verbose_name = " объект 'Get Course'"
        verbose_name_plural = "Get Courses"


class TestModel(models.Model):

    test = models.TextField(verbose_name="Данные")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = " объект 'Тест'"
        verbose_name_plural = "Тесты"

class QualityControl(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    rating = models.PositiveIntegerField(verbose_name="Оценка качества")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Оценка: {self.rating}, {self.content_object}"

    class Meta:
        verbose_name = " объект 'Контроль качества'"
        verbose_name_plural = "Контроль качества"



class ResponseTimeCreate(models.Model):
    leads_id = models.CharField(max_length=255, verbose_name="Идентификатор сделки")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")


    def __str__(self):
        return f"{self.leads_id}, {self.creation_date}"

    class Meta:
        verbose_name = " объект 'Созданная сделка AMO CRM'"
        verbose_name_plural = "Созданные сделки AMO CRM"

class ResponseTimeDelete(models.Model):
    leads_id = models.CharField(max_length=255, verbose_name="Идентификатор сделки")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")



    def __str__(self):
        return f"{self.leads_id}, {self.creation_date}"

    @property
    def get_closure_time(self):
        create_obj = ResponseTimeCreate.objects.filter(leads_id=self.leads_id).first()
        if create_obj:
            closure_duration = self.creation_date - create_obj.creation_date
            days = closure_duration.days
            hours, remainder = divmod(closure_duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return days, hours, minutes
        return None
    class Meta:
        verbose_name = " объект 'Удаленная сделка AMO CRM'"
        verbose_name_plural = "Удаленные сделки AMO CRM"