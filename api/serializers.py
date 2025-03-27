from rest_framework import serializers
from .models import PDFHistory


class PDFHistory(serialiers.ModelSerializer):
    class Meta:
        model = PDFHistory
        fields = '__all__'









