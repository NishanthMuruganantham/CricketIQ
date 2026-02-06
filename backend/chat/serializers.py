from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000, required=True)

class ChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    query_executed = serializers.CharField(required=False, allow_null=True)
    chart_data = serializers.DictField(required=False, allow_null=True)
