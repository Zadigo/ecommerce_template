import datetime
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



def zip_code_validator(zip_code):
    is_match = re.match(r'\w{5}', zip_code)
    if is_match:
        return is_match.group(0)
    raise ValidationError('Zip code is not valid')


def discount_pct_validator(pct):
    if pct < 0 or pct > 80:
        raise ValidationError('Discount should be between 0 and 70%')
    return pct


def price_validator(price):
    if price < 0:
        raise ValidationError('Price should not be below 0')
    return price


def quantity_validator(quantity):
    if quantity < 1 or quantity > 99:
        raise ValidationError("La quantité n'est pas valide")
    return quantity


def generic_size_validator(size):
    """
    A simple validator for validating the sizes that
    are entered in the database
    """
    if not size:
        raise ValidationError("La taille n'est pas reconnue")
    is_match = re.match(r'^(\d+|[A-Za-z]{1,3})[A-Za-z]?$', size)
    if is_match:
        return size.upper()
    raise ValidationError("La taille n'est pas reconnue")


def size_validator(size):
    """Checks if the size is within the accepted sizes
    and then substitutes the incoming size with the
    checked size
    
        Waist     Int.          FR              EU      UK      US      ITA

        82/86	    XS	    36 (Taille 1)	34	8	4	1
        87/91	    S	    38 (Taille 2)	36	10	6	2
        92/96	    M	    40 (Taille 3)	38	12	8	3
        97/101	    L	    42 (Taille 4)	40	14	10	4
        102/106	    XL	    44 (Taille 5)	42	16	12	5
        107/111	    XXL	    46 (Taille 6)	44	18	14	6
    """
    sizes = ['XS', 'xs', 's', 'S', 
                    'm', 'M', 'l', 'L', 'xl', 'XL']
    if size is None:
        return None
    if size not in sizes:
        raise ValidationError('Size should be one of XS, S, M or L')
    else:
        return sizes[sizes.index(size)]
    return size


def bra_size_validator(size):
    """
    A validator for implementing sizes for bras

        Bust size:

                63-67  68-72   73-77    78-82     83-87
                80      85      90       95        100

        Chest size:
            A   76-78   81-83	86-88   91-93	
            B   79-81   84-86	89-91   94-96     99- 101
            C   82-84   87-89	92-94   97-99     102-104
            D   85-87   90-92	95-97   100-102   105-107
            E   88-90   93-95	98-100  103-105   108-110
            F   91-93   96-98	101-103 106-108   111-113
    """
    is_match = re.match(r'(\d+)(\w{1})', size)

    if is_match:
        size = int(is_match.group(1))
        is_between = all([size >= 80, size <= 100])
        if not is_between:
            raise ValidationError('Size should be between 80 and 100')
        
        if size % 5:
            raise ValidationError('Size should be one of 80, 85, 90, 95 or 100')

        letters = ['A', 'B', 'C', 'D', 'E', 'F']

        letter = is_match.group(2)
        if letter not in letters:
            raise ValidationError(
                f"Letter should be one of {', '.join(letters)}")

        return size
    else:
        raise ValidationError('Size should be formatted as 90C or 80A')


def t_size_cup_validator(size):
    """
    Validates the equivalence between a  and T sizes
    for triangla bras and bandeau-bras who has sizes
    marked a T.

        85A ou 80B           T0
        90A ou 85B           T1
        95A, 90B ou 85C      T2
        95B, 90C ou 85D      T3
        95C ou 90D           T4
    """
    valid_t_sizes = ['T0' 'T1', 'T2', 'T3', 'T4']
    if not size in valid_t_sizes:
        raise ValidationError(f"Cup should be one of {', '.join(valid_t_sizes)}")
    return size


def underwear_validator(size):
    """
    Validation for uderwears
        84-88   88-92     92-96     96-100      100-104     104-108
         34      36        38        40          42          44
         T1      T1        T2        T2          T3          T3  
    """
    if size.startswith('T'):
        pass
    else:
        if size < 34 or size > 44:
            raise ValidationError('Size should be between 34 and 44')

        if size % 2:
            raise ValidationError("Size should be one of 34, 36, 38, 40, 42 and 44")
    return size


def shoe_size(size):
    if size < 35 or size > 40:
        raise ValidationError('Size should be between 35 and 40')
    return size
