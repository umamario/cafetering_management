from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'survey', views.QuestionViewSet)
urlpatterns = router.urls