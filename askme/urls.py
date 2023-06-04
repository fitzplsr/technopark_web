from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('questions/', include('app.urls')),
    path('signup', views.signup, name='signup'),
    path('login', views.log_in, name='login'),
    path('logout', views.logout, name='logout'),
    path('profile/edit', views.settings, name='settings'),
    path('ask', views.ask, name='ask'),
    path('vote', views.vote, name='vote'),
    path('correct', views.correct, name='correct')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)