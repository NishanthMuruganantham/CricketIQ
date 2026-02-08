from rest_framework import serializers

class ConversationMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user', 'assistant'])
    text = serializers.CharField()

class ChatRequestSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000, required=True)
    conversation_history = ConversationMessageSerializer(many=True, required=False, default=list)

class ChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    query_executed = serializers.CharField(required=False, allow_null=True)
    chart_data = serializers.DictField(required=False, allow_null=True)
