class Organization(dict):
    def __init__(self, **kwargs):
        base = {
            'image': [],
            'name': 'Nawoka',
            'description': '',
            'city': 'Lille',
            'region': 'Haut-de-France',
            'zip_code': 59000,
            'fonder': {
                'name': 'John',
                'surname': 'Pendenque',
                'title': 'Founder, CEO'
            }
        }
        if kwargs:
            organization = {**organization, **kwargs}
        self.update({'organization': base})

organization = Organization()

def organization_context_processor(request):
    return {'organization': organization}