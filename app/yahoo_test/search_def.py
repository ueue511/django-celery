from django.db.models import Q


class Seach_All_data():
    def __init__(self, data, search_data):
        self.data = data
        self.search_data = search_data

    def search_go(self):
        data = [self.data.filter(Q(serach_name__iexact=self.search_name_one)).distinct()
                for self.search_name_one in self.search_data]
        return data
