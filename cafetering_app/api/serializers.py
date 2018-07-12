from rest_framework import serializers
from bos.models import Question


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_choice', 'point_reward')
