# Cart application

## Before starting

Before running the whole project, if you wish to use the cart payment system from the cart application, you have to provide the following Stripe keys.

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

If not provided, you will get a `ImproperlyConfigured` error.
