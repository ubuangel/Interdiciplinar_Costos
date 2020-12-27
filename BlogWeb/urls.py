"""BlogWeb URL Configuration

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
    
    rama2 yo aqui XD
"""
from django.contrib import admin
from django.urls import path,include


from django.conf.urls.i18n import i18n_patterns
from main.viewset import fee_progViewSet,productViewSet,batchViewSet,salesViewSet, statisticsViewset,salesCustom
from main.views import change_batch_status,edit_company_capital
from rest_framework import routers


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('appblog/',include('appblog.urls')),
]




router=routers.DefaultRouter()
router.register(r'fee_progVS',fee_progViewSet)
router.register(r'productVS',productViewSet)
router.register(r'batchVS',batchViewSet)
router.register(r'salesVS',salesViewSet)
router.register(r'statisticsVS',statisticsViewset)

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/salescustom/<str:order_id>/',salesCustom.as_view()),
    path('api/changeBatchStatus/',change_batch_status),
    path('api/editCompanyCapital/',edit_company_capital),
    path('api/',include(router.urls)),
]

urlpatterns += i18n_patterns(
    path('',include('main.urls')),
    path('app/',include('main.urls')))
