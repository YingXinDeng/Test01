from rest_framework import serializers

from msm.models import AccountLogin


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta():
        model = AccountLogin
        fields = '__all__'