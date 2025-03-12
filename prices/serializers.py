from rest_framework.serializers import ModelSerializer

from prices.models import Price

class PriceSerializer(ModelSerializer):
    class Meta:
        model = Price
        fields = "__all__"
