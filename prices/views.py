from rest_framework.decorators import api_view
from rest_framework.response import Response

from prices.models import Price
from prices.serializers import PriceSerializer

@api_view(['GET'])
def get_price_history(request):
    print(request.query_params)
    ticket = request.query_params.get("ticket", "btcusdt")
    prices = Price.objects.filter(ticket__iexact=ticket)
    return Response(data=PriceSerializer(prices, many=True).data)

