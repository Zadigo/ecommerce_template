# Analytics Application

This application simplifies the utilization of analytics tags in your Django project.

## Getting started

```
TEMPLATES = [
    {
        "OPTIONS": {
            "context_processors": [
                ...
                analytics.context_processors.analytics
            ]
        }
    }
]
```

Once the `Analytics` database is created, you can simply store your tags and they will persist in the templates.

# Template tags

```
{% facebook "..." %}

# Google Analytics, Google Optimize

{% google_analytics "UA-XXXX" "UA-XXXX" %}
```

# Support / Development

If you are interested in me participating in some other projects for you relate to the current work that I have done I am currently available for remote and on-site consulting for small, large and enterprise teams. Please contact me at pendenquejohn@gmail.com with your needs and let's work together!
