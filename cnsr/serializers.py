from rest_framework import serializers
from cnsr.models import StartAppCnsr, MiddelAppCnsr, EndAppCnsr
from cnsr.utiles import string_to_time


class StartAppCnsrSerializers(serializers.ModelSerializer):
    s = serializers.SerializerMethodField()
    e = serializers.SerializerMethodField()

    def get_s(self, obj):
        return string_to_time(obj.s)

    def get_e(self, obj):
        return string_to_time(obj.e)

    class Meta:
        model = StartAppCnsr
        fields = ("s", "e")


class MiddelAppCnsrSerializers(serializers.ModelSerializer):
    s = serializers.SerializerMethodField()
    e = serializers.SerializerMethodField()

    def get_s(self, obj):
        return string_to_time(obj.s)

    def get_e(self, obj):
        return string_to_time(obj.e)

    class Meta:
        model = MiddelAppCnsr
        fields = ("s", "e")


class EndAppCnsrSerializers(serializers.ModelSerializer):
    s = serializers.SerializerMethodField()
    e = serializers.SerializerMethodField()

    def get_s(self, obj):
        return string_to_time(obj.s)

    def get_e(self, obj):
        return string_to_time(obj.e)

    class Meta:
        model = EndAppCnsr
        fields = ("s", "e")
