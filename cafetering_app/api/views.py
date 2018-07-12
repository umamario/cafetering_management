from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from cafetering_app.api.serializers import QuestionSerializer

from bos.models import Question, Survey


class QuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def retrieve(self, request):
        queryset = Survey.objects.get(id=id).questions.all()
        serializer_class = QuestionSerializer


def api_get_questions(request, survey_id):
    from django.db.models import Sum
    questions = Survey.objects.get(id=survey_id).questions.all()
    acumulated = responses.aggregate(Sum('point_rewarded'))
    return render(request, 'index.html', {'responses': responses,
                                          'user_acumulated': acumulated['point_rewarded__sum']})
