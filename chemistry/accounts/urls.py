from django.urls import path

from .views import SignUpView
from . import views


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path('approval-pending/', views.approval_pending, name='approval_pending'),

]