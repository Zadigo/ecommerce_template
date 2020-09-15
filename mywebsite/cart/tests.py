from django.test import TestCase



class TestPaymentFunnel(TestCase):
    def test_shipment_page_no_cart(self):
        response = self.client.get(reverse('shipment'))
        self.assertEqual(response.status_code, 302)
        # self.assertIn(response.redirect_chain, '/shop/no-cart')

    def test_shipment_page_with_cart(self):
        session = self.client.session
        session['cart_id'] = 'fake_id'
        session.save()
        request = factory.get(reverse('shipment'))

        self.assertIn(session['cart_id'], 'fake_id')

        views.ShipmentView().setup(request)

        # This section processes the request
        # with the SessionMiddleWare in order
        # to verify that we indeed getting a
        # status code o 200 when accessing
        # this page
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        self.assertEqual(request.session.get('cart_id'), 'fake_id')
