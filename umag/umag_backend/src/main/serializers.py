from rest_framework import serializers
from .models import *


class AmoCrmWebhookModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmoCrmWebhookModel
        fields = '__all__'


class SupportConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportConsultation
        fields = '__all__'


class KeySerializer(serializers.Serializer):
    key = serializers.CharField(
        label="Token",
        required=True,
    )

    class Meta:
        fields = ('key',)


class PersonalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalData
        fields = ['telegram_id', 'first_name', 'franchise_name', 'phone_number']

    def create(self, validated_data):
        try:
            return PersonalData.objects.create(**validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error creating PersonalData: {str(e)}")


class SupportConsultationSaveSerializer(serializers.ModelSerializer):
    telegram_id = serializers.CharField(write_only=True)
    creation_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)

    class Meta:
        model = SupportConsultation
        fields = ['id', 'telegram_id', 'description_problem', 'creation_date']

    def create(self, validated_data):
        telegram_id = validated_data.pop('telegram_id')

        try:
            personal_data = PersonalData.objects.get(telegram_id=telegram_id)
        except PersonalData.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким telegram_id не найден")

        validated_data['personal_data'] = personal_data

        return super().create(validated_data)


class SupportBugSaveSerializer(serializers.ModelSerializer):
    telegram_id = serializers.CharField(write_only=True)
    creation_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)

    class Meta:
        model = SupportBug
        fields = ['id', 'telegram_id', 'bug_name', 'description_and_scenario', 'additional_information', 'app_version',
                  'personal_account_access', 'creation_date']

    def create(self, validated_data):
        telegram_id = validated_data.pop('telegram_id')

        try:
            personal_data = PersonalData.objects.get(telegram_id=telegram_id)
        except PersonalData.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким telegram_id не найден")

        validated_data['personal_data'] = personal_data

        return super().create(validated_data)


class SupportSynchronizationSaveSerializer(serializers.ModelSerializer):
    telegram_id = serializers.CharField(write_only=True)
    creation_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)

    class Meta:
        model = SupportSynchronization
        fields = ['id', 'telegram_id', 'all_messages', 'creation_date']

    def create(self, validated_data):
        telegram_id = validated_data.pop('telegram_id')

        try:
            personal_data = PersonalData.objects.get(telegram_id=telegram_id)
        except PersonalData.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким telegram_id не найден")

        validated_data['personal_data'] = personal_data

        return super().create(validated_data)


class SupportGetCourseSaveSerializer(serializers.ModelSerializer):
    telegram_id = serializers.CharField(write_only=True)

    class Meta:
        model = SupportGetCourse
        fields = ['telegram_id', 'email', 'study_type']

    def create(self, validated_data):
        telegram_id = validated_data.pop('telegram_id')

        try:
            personal_data = PersonalData.objects.get(telegram_id=telegram_id)
        except PersonalData.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким telegram_id не найден")

        validated_data['personal_data'] = personal_data

        return super().create(validated_data)


class QualityControlCreateSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(write_only=True)

    class Meta:
        model = QualityControl
        fields = ['model_name', 'object_id', 'rating']

    def validate(self, attrs):
        model_name = attrs.get('model_name')
        try:
            content_type = ContentType.objects.get(model=model_name)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Invalid model_name")
        attrs['content_type'] = content_type
        return attrs

    def create(self, validated_data):
        validated_data.pop('model_name')
        return super().create(validated_data)
