from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, reverse
from django.views.generic import DetailView


class SpecialOfferView(DetailView):
    model = cart_models.Discount
    template_name = 'pages/product.html'
    context_object_name = 'product'

    def get_queryset(self):
        offer = cart_models.Discount.\
            objects.get(reference=self.kwargs['pk'])
        try:
            product = offer.product.get(
                reference=self.kwargs['product_reference'])
        except ObjectDoesNotExist:
            return redirect(reverse('shop_gender', args=['femme']))
        else:
            return product
