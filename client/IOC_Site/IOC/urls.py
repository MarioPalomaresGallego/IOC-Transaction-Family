from django.urls import path

from . import views

urlpatterns = [
	path('',views.index, name='index'),
	path('details/',views.details, name='index'),
	path('upload/',views.upload, name='upload'),
	path('block/',views.req_block,name='block'),
	path('download/',views.download,name='download'),
	path('update_status/',views.update_status,name='update'),
]
