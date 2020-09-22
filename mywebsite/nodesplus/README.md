# Analytics Application

This application introduces some of the most common template tags for an e-commerce website (example: transforming 12 to 12€ or a 5% discount code to -5%)

## Getting started

Call the node_plus templatetag in the templates in which to use it's functionnalities.

```
{% load nodes_plus %}
```

### Price to text

Transform a number [which is a price] to a price. For instance 12 would become 12€.

```
{{ price|price_to_text:"€" }}
```

### Number to percentage

Transform a number to percentage. 12 would become 12%.

```
{{ price|number_to_percentage }}
```

### Discount as text

Get the true representation of a discounted percentage. 12 would become -12%

```
{{ price|discount_as_text }}
```

### Discount as html

Get the true representation of a discounted percentage but as an html tag.

```
{{ price|discount_as_html }}

>> <strike>-12%</strike>
```

### Impressions

Transform a queryset to a dict for Google Analytics impressions for example.

```
<script>
    dataLayer.push(
        {% impressions queryset "field1" "field2" %}
    )
</script>
```

NOTE: This returns a dictionnary of values for the fields that you specified `{ "field1": "value", "field2": "value" }`.

# Support / Development

If you are interested in me participating in some other projects for you relate to the current work that I have done I am currently available for remote and on-site consulting for small, large and enterprise teams. Please contact me at pendenquejohn@gmail.com with your needs and let's work together!
