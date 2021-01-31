"""TAP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

# Links the overall django application to different apps that the team develops
urlpatterns = [
    path('datagen/', include('datagen.urls')),
    path('admin/', admin.site.urls),
    path('parse/', include('parsing.urls')),
    path('', include('pages.urls')),
    path('plotly/', include(('visualizations.urls', 'visualizations'), namespace='visualizations')),
    path('sql/', include('sql.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
