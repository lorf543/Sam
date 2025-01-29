from django.urls import path
from . import views


urlpatterns_pedidos = [
    path('create-pedidos/',views.create_pedido,name="create_pedido"),
]


urlpatterns = [
    path('my-account',views.my_account,name='my_account'),
    path('handle-buyer/<int:pk>/',views.handle_buyer, name='handle_buyer'),
    path('create-comment/<int:pk>/',views.create_comment,name='create_comment'),
    path('update-comment/<int:pk>/',views.update_comment,name='update_comment'),
    
    path("profile/", views.edit_profile, name="edit_profile"),
    path("signup/", views.custom_signup, name="custom_signup"),
] 



urlpatterns += urlpatterns_pedidos
