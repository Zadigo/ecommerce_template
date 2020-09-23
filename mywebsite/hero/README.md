# Hero application

The main purpose of this application is to simplify the integration of a home page for your Django application. The hero application uses [MD Bootrap's free landing page template](https://mdbootstrap.com/freebies/jquery/landing-page/).

## Getting started

The main hero page starts with the [hero.html](./templates/pages/hero.html) page which return extends `base` or ``base_site` depending on your configuration.

You will want to have this main structure on your `base` or `base_site` file in order to have the components appear.

```
{% extends "base_site.html" %}

{% block main_tag_style %}...{% endblock %}

{% block main %}
    <!-- HERO -->
    {% include "components/hero/base.html" %}
    
    <!-- MAIN -->
    {% include "components/benefits/base.html" %}
{% endblock %}
```

As you can see from the above, the main block divides two sections: the hero section from the benefits one (which corresponds to the lower section of the page for additional product information and so on).

## Exploring the components

Adding a new component is very easy.

# Support / Development

If you are interested in me participating in some other projects for you relate to the current work that I have done I am currently available for remote and on-site consulting for small, large and enterprise teams. Please contact me at pendenquejohn@gmail.com with your needs and let's work together!
