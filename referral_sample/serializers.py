from rest_framework import serializers


class DeviceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'get_name', 'hostname', 'last_ping', 'trust_score', 'comment', 'device_id', 'owner',
                  'trust_score_color', 'trust_score_percent']
