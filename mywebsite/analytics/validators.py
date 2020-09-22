def validate_analytics(tag):
    is_match = re.match(r'UA\-[0-9]{8}\-[0-9]{1}', value)
    if is_match:
        return tag
    raise


def validate_tag_manager(tag):
    is_match = re.match(r'GTM\-[A-Z0-9]{7}', value)
    if is_match:
        return tag
    raise


def validate_optimize(tag):
    pass


def validate_analytics(tag):
    pass
