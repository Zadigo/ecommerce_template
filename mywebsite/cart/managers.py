import datetime
import re

from django import http
from django.contrib import messages
from django.core import exceptions
from django.db.models import (Avg, Case, Count, F, Q, QuerySet, Sum, When,
                              fields)
from django.db.models import Value, BooleanField, DecimalField
from django.db.models.functions import TruncMonth

from cart import utilities



class CartManager(QuerySet):
    def my_cart(self, cart_id):
        """
        Returns all the products of a customer's cart
        """
        return self.filter(cart_id__exact=cart_id)

    def cart_products(self, cart_id):
        cart = self.my_cart(cart_id)
        logic = (
            Q(product__discounted_price__gt=0) &
            Q(product__discounted=True)
        )
        # Gets the true price of the product
        condition = When(logic, then='product__discounted_price')
        annotated_cart = cart.annotate(true_price=Case(condition, default='product__price_pre_tax'))
        
        calculate_total = F('true_price') * F('quantity')
        condition = When(true_price__gt=0, then=calculate_total)
        return annotated_cart.annotate(total=Case(condition, output_field=DecimalField()))

    def cart_total(self, cart_id, as_value=False, queryset=None):
        cart = queryset or self.cart_products(cart_id)
        total = cart.aggregate(cart_total=Sum(F('true_price') * F('quantity'), output_field=DecimalField()))
        
        if as_value:
            total = total['cart_total']
            if total is None:
                return 0
            return float(str(total))
        return total

    def cart_total_discount_entire_order(self, cart_id):
        """
        This calculates the total price of a cart based
        on whether the cart has coupon and that it is
        applicable on the entire order
        """
        queryset = self.cart_products(cart_id)

        total_discounted_with_coupon = F('true_price') / (F('coupon__value') * (1 - F('coupon__value') / 100))
        total_minus_coupon = F('true_price') - F('coupon__value')

        coupon_is_for_entire_order = Q(coupon__isnull=False) & Q(coupon__on_entire_order=True)
        coupon_on_entire_order_percentage = coupon_is_for_entire_order & Q(coupon__value_type='percentage')
        coupon_on_entire_order_value = coupon_is_for_entire_order & Q(coupon__value_type='fixed amount')

        first_case = When(coupon_on_entire_order_percentage, then=total_discounted_with_coupon)
        second_case = When(coupon_on_entire_order_value, then=total_minus_coupon)

        case = Case(first_case, second_case, default='true_price', output_field=fields.DecimalField())

        return queryset.annotate(reduced_price=case)

    def discount_on_specific_collection(self):
        """
        Calculates the specific discounted price of a product
        based on whether the coupon applies to the collection
        in which in the product is a part of
        """
        # product_is_part_of_collection = None
        # coupon_on_collection_percentage = Q(coupon__isnull=False) & Q(coupon__collection=True) & Q(value_type='percentage')
        # coupon_on_collection_value = Q(coupon__isnull=False) & Q(coupon__collection=True) & Q(value_type='fixed amount')

        # third_case = When(coupon_on_collection_percentage, then=total_discounted_with_coupon)
        # fourth_case = When(coupon_on_collection_value, then=total_minus_coupon)

        pass

    def number_of_products(self, cart_id, as_value=False):
        """Number of products in a cart"""
        total = self.my_cart(cart_id).aggregate(Sum('quantity'))
        if as_value:
            return total['quantity__sum']
        return total

    def add_to_cart(self, request, current_product, enforce_color=False):
        cart_id = request.session.get('cart_id')
        quantity = request.POST.get('quantity')
        color = request.POST.get('color')
        size = request.POST.get('size')

        base_message = {
            'request': request,
            'extra_tags': 'alert-danger'
        }

        if not current_product.active:
            base_message['message'] = "Une erreur s'est produite - ADD-NA"
            messages.error(**base_message)
            return False

        if color is None:
            base_message['message'] = "Une erreur s'est produite - ADD-CO"
            messages.error(**base_message)
            return False

        if size is None:
            size = ''

        if quantity is None:
            quantity = 1

        new_item_details = {
            'cart_id': cart_id,
            'price_pre_tax': current_product.get_price(),
            'size': size,
            'color': color,
            'quantity': int(quantity),
            'anonymous': request.user.is_authenticated,
            'product': current_product
        }

        if not cart_id:
            cart_id = utilities.create_cart_id()
            new_item_details['cart_id'] = cart_id
            try:
                new_item = self.create(**new_item_details)
            except:
                base_message['message'] = "Une erreur s'est produite - ADD-CR"
                messages.error(**base_message)
                return False
            else:
                request.session['cart_id'] = cart_id
                return new_item
        
        if cart_id:
            characteristics = (
                Q(color=color) &
                Q(size=size)
            )

            other = (
                Q(product__id=current_product.id) & 
                Q(cart_id__iexact=cart_id)
            )

            logic = characteristics & other
            items = self.filter(logic)
            if items.exists():
                item = items.get()
                item.price_pre_tax = current_product.get_price()
                item.product = current_product
                item.color = color
                item.size = size
                item.quantity = F('quantity') + int(quantity)
                item.anonymous = request.user.is_authenticated
                item.save()
                return item
            else:
                new_item = self.create(**new_item_details)
                return new_item
            

    def over_thirtee_days(self):
        current_date = datetime.datetime.now().date()
        queryset = self.filter(
            created_on__range=[
                current_date - datetime.timedelta(days=31), current_date
            ]
        )
        return queryset


##############
#
# DASHBOARD
#
##############

class BaseStatistics(QuerySet):
    def total_count(self):
        return self.all().count()

class CartsStatisticsManager(BaseStatistics):
    def carts_with_orders(self, return_querysets=False):
        carts = []
        for cart in self.all():
            if cart.customerorder_set.all():
                carts.append(cart)

        if return_querysets:
            return carts

        if carts:
            return len(carts)
        return 0

    def carts_without_orders(self, return_querysets=False):
        carts = []
        for cart in self.all():
            if not cart.customerorder_set.all():
                carts.append(cart)

        if return_querysets:
            return carts

        if carts:
            return len(carts)
        return 0

class OrdersStatisticsManager(BaseStatistics):
    def accepted_orders(self):
        # Orders that are accepted can be counted
        # in the revenue
        return self.filter(accepted=True)

    def non_accepted_orders(self):
        return self.filter(accepted=False)

    def refunded_orders(self):
        """Orders where the customer asked for
        a refund are deducted from revenue
        """
        return self.filter(refund=True)

    def accepted_and_not_refunded(self):
        """Queryset of true revenue of the store"""
        return self.accepted_orders().filter(refund=False)

    def fulfilled_orders(self):
        logic = Q(accepted=True) & Q(completed=True) & Q(refund=False)
        return self.filter(logic)

    def total_refunded_orders(self):
        return self.refunded_orders().aggregate(Sum('payment'))

    def payments_by_month(self):
        queryset = self.annotate(month=TruncMonth('created_on'))
        values = queryset.values('month').annotate(quantity=Count('id'))
                    
        labels = []
        data = []
        for item in values:
            labels.append(item['month'])
            data.append(item['quantity'])
        return [labels, data]

    def latest_orders(self):
        difference = F('created_on') - datetime.timedelta(days=7)
        latest_and_awaiting = Q(created_on__gt=difference) & Q(accepted=False) & Q(completed=False)
        return self.filter(latest_and_awaiting)

    def average_total_order(self):
        carts = self.select_related('cart')
        prices = F('cart__price_post_tax') * F('cart__quantity')
        return carts.annotate(average_prices=prices).aggregate(Avg('prices'))

    def revenue(self):
        return self.fulfilled_orders().aggregate(Sum('payment'))

    def awaiting_revenue(self):
        # Orders that were not yet
        # accepted and awaiting to
        # be delivered to the customer
        return self.non_accepted_orders().aggregate(Sum('payment'))

    def profit(self):
        carts = self.prefetch_related('cart')
        profit = F('cart__price_post_tax') - F('cart__price_pre_tax')
        total_profit = Sum(profit*F('cart__quantity'), output_field=fields.DecimalField())
        return carts.annotate(total_profit=total_profit).aggregate(Sum('total_profit'))
