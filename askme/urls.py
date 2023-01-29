"""askme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.new_questions, name='index'),
    path('hot/', views.hot_questions, name='hot_questions'),
    path('new/', views.new_questions, name='new_questions'),
    path('tag/<str:tag>/', views.tag_questions, name='tag'),

    path('ask/', views.ask_question, name='ask_question'),
    path('question/<int:question_id>/', views.question_answers, name='question_answers'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.sign_up, name='signup'),
    path('profile/edit', views.edit_profile, name='profile_edit'),

    path('vote/', views.vote, name='vote'),
    path('correct-answer/', views.correct_answer, name='correct_answer'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

