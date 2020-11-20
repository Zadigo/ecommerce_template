import numpy
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class BraCalculator:
    size_columns = [
        [80, [[76, 78], [79, 81], [82, 84], [85, 87], [88, 90], [91, 93]]],
        [85, [[81, 83], [84, 86], [87, 89], [90, 92], [93, 95], [96, 98]]],
        [90, [[86, 88], [89, 91], [92, 94], [95, 97], [98, 100], [101, 103]]],
        [95, [[91, 93], [94, 96], [97, 99], [100, 102], [103, 105], [106, 108]]],
        [100, [[99, 101], [102, 104], [105, 107], [108, 110], [111, 113]]]
    ]

    def __init__(self, bust, chest):
        if bust < 63 or bust > 87:
            raise ValidationError(_("La taille du buste n'est pas valide"))

        index, size = self._find_size(bust)
        cup = self._find_cup(index, chest)

        self.size = size
        self.cup = cup

    @property
    def get_full_bra_size(self):
        return f'{self.size}{self.cup}'

    def _sizes(self, index=None):
        """
        Based on the index provided, this picks the correct
        row in the sizes columns.

        Result
        ------

            [size1, size2, ...]
        """
        sizes = [size[0] for size in self.size_columns]
        return sizes if not index else sizes[index]

    def _find_size(self, bust):
        """
        This method finds the correct bracket based on the
        size of a person's bust

        Result
        ------

            Returns the index of th
        """
        busts = [
            [63, 67],
            [68, 72],
            [73, 77],
            [78, 82],
            [83, 87]
        ]
        for index, limits in enumerate(busts):
            is_found = self._compare(bust, limits[0], limits[1])
            if is_found:
                return index, self._sizes(index=index)

    def _find_cup(self, index, chest):
        """
        Returns the correct cup based on 
        """
        column = self.size_columns[index]

        letters = ['A', 'B', 'C', 'D', 'E', 'F']

        for i, size in enumerate(column[1]):
            is_match = self._compare(chest, size[0], size[1])
            if is_match:
                if i == 4:
                    # There is no cup A for size 100,
                    # in which case, we have to increase
                    # the index by one to have 'A'
                    i = i + 1 
                else:
                    letter = letters[i]
                    return letter
    
    @staticmethod
    def _compare(value, upper, lower):
        return all([value >= upper, value <= lower])

class TSizeTranslator(BraCalculator):
    t_sizes = [
        (['85A', '90B'], 'T0'),
        (['90A', '85B'], 'T1'),
        (['95A', '90B', '85C'], 'T2'),
        (['95B', '90C', '85D'], 'T3'),
        (['95C', '90D'], 'T4')
    ]
    def convert_size(self):
        for size in self.t_sizes:
            if self.bra_size in size[0]:
                return size[1]
            else:
                return False
