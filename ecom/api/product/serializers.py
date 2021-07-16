from django.db.models import fields
from .models import Product
from rest_framework import serializers

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.ImageField(
            max_length=None, allow_empty_file=False, allow_null=True, required=False)
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'image', 'category')