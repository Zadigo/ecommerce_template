import re


class Responsive:
    """A class that detects if a request comes from a mobile
    or not by testing the User-Agent of the request.

    Description
    -----------

        Returns True or False if a mobile or not
    """
    def __init__(self, request):
        first_test = False
        second_test = False

        try:
            user_agent = request.META.get('HTTP_USER_AGENT')
        except AttributeError:
            user_agent = None
        
        if user_agent:
            if 'Mobile' in user_agent:
                first_test = True
            else:
                first_test = False

            # Additional test. Detect if iPhone
            # or Android. Confirms for sure then
            # that it is indeed a mobile phone
            os_pattern = r'(i[p|P]hone|Android)'
            try:
                is_match = re.search(os_pattern, user_agent)
            except:
                second_test = False
            else:
                if is_match:
                    self.mobile_type = is_match.group(1)
                    second_test = True
                else:
                    second_test = False

        self.mobile = all([first_test, second_test])

    def __call__(self, request):
        return self.mobile


def responsive_context_processor(request):
    check_if_mobile = Responsive(request)
    return {'is_mobile': check_if_mobile.mobile}
