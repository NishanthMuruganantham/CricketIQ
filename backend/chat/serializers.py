"""Serializers for chat API - validates incoming and outgoing data."""
from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    """Validates incoming chat requests."""
    question = serializers.CharField(max_length=2000, required=True)


class ChartDataSerializer(serializers.Serializer):
    """Serializes chart data in the response."""
    type = serializers.CharField(allow_null=True)
    labels = serializers.ListField(child=serializers.CharField(), required=False)
    values = serializers.ListField(child=serializers.FloatField(), required=False)
    title = serializers.CharField(required=False)
    x_axis = serializers.CharField(required=False)
    y_axis = serializers.CharField(required=False)


class ChatResponseSerializer(serializers.Serializer):
    """Validates outgoing chat responses."""
    answer = serializers.CharField()
    chart_data = ChartDataSerializer(allow_null=True)
    query_executed = serializers.CharField(allow_null=True)
