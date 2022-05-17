from rest_framework import serializers

from fitgenius.club.models import OfferedItem, Product, Offer, Budget


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__al__'


class OfferedItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OfferedItem
        fields = '__al__'


class OfferSerializer(serializers.ModelSerializer):
    total_sales = serializers.DecimalField(read_only=True, max_digits=18, decimal_places=2)

    class Meta:
        model = Offer
        fields = '__all__'


class BudgetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Budget
        fields = '__all__'
