from django.urls import path
from . import views
urlpatterns = [
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    
    path('pdf/text-to-pdf/', views.text_to_pdf, name='text_to_pdf'),
    path('pdf/merge/', views.merge_pdfs, name='merge_pdfs'),
    path('pdf/to-word/', views.pdf_to_word, name='pdf_to_word'),
    path('pdf/highlight/', views.highlight_pdf, name='highlight_pdf'),
    
    path('history/', views.get_history, name='get_history'),
]