class DiscountManager(QuerySet):
    def apply_coupon(self, carts, code, total, quantity=0):
        try:
            # The code does not exist, return
            # the total
            discount = self.get(code__iexact=code)
        except:
            return total
        else:
            # Discount should be active. This is
            # a special case where the code is
            # disabled internally
            if not discount.active:
                return total

        if discount.usage_limit == 0:
            return total

        if total < discount.minimum_purchase:
            return total

        if quantity > 0 and quantity < discount.minimum_quantity:
            return total

        if discount.start_date <= datetime.datetime.date().now():
            return total

        # Adds the coupon to all the
        # selected carts
        discount.cart_set.set(*list(carts))

        if discount.value_type == 'percentage':
            final_price = total * (1 - discount.value)
        elif discount.value_type == 'fixed amount':
            final_price = total - discount.value
        elif discount.value_type == 'free shipping':
            pass

        carts.update(discounted_price=final_price)
