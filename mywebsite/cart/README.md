# Cart application

## Before starting

To use the cart's session payment system, you must provide the Stripe API keys as below:

```
STRIPE_DEBUG = True

STRIPE_API_KEYS = {
    'test': {
        'publishable': '',
        'secret': ''
    },
    'live': {
        'publishable': '',
        'secret': ''
    }
}
```

These keys are available on your [Stripe account.](https://stripe.com).

## How the payment system works

__The payment system is session based.__ This was done in order to allow none authenticated users to be able to purchase without having to create any account.

When the customer clicks on add to cart, a unique token called `cart_id` is created in his session. At each additional products in the cart, this cart ID is used to regroup all the items present in that cart.

A product is created in cart's database __if it does not have or share the same characteristics as any others present in the cart.__

For instance, this will add a new item to the cart:

```
product = models.Product.objects.get(id=1, color="Blue")

models.Cart.objects.create(cart_id="cartxxx", product=product, quantity=1)

>> <Cart [new Product in cart]>
```

However, running the same piece of code will only just add 1 to the already existing item in the cart. __The product with color blue and ID of 1 will then have its quantity updated to 2.__

This technique allows us to keep track of each individual item's quantity even when they have exact same references but with completely different variants.

When the customer tries to purchase the cart, all items having the same cart ID are aggregated.

### Understanding SessionPaymentBackend class

When a customer comes on an e-commerce platform, the flow is almost exactly the same:

    - Adds product to cart
    - Goes to cart
    - Fills in his shipping informations
    - Goes to payment page
    - Pays / Payment is processed
    - Gets redirected to success page

In order to orchestrate all of this efficiently, the system is based on this `SessionPaymentBackend` class which wraps the main Stripe functionnalities.

```
class SessionPaymentBackend(PaymentMixin):
    def process_payment(self, ...):
        ...

    def create_stripe_customer_and_process_payment(self, ...):
        ...

    def create_new_order(self, ...):
        ...

    def create_new_customer_locally(self, ...):
        ...
```

What this does is interract with the database at each step of the funnel by:

    - Pre processing the user information before accessing the payment page
    - Processing the payment once the customer clicks pay
    - Create a new order in the CustomerOrder database
    - Clear the session from any cart ID

# Support / Development

If you are interested in me participating in some other projects for you relate to the current work that I have done I am currently available for remote and on-site consulting for small, large and enterprise teams. Please contact me at pendenquejohn@gmail.com with your needs and let's work together!
