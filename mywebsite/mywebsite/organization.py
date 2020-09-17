from legal.context_processors import Legal

class Nawoka(Legal):
    legal_name = 'Nawoka'

    def __init__(self):
        super().__init__(google='Talent')
