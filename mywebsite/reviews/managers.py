from django.db.models.query import QuerySet
from django.db.models.aggregates import Avg, Count

class ReviewManager(QuerySet):
    def reviews(self, product_id):
        return self.filter(id=product_id)
        
    def average_rating(self, product_id):
        reviews = self.reviews(product_id)
        return reviews.aggregate(Avg('rating'))

    def number_of_reviews(self, product_id):
        reviews = self.reviews(product_id)
        return reviews.aggregate(Count('rating'))
