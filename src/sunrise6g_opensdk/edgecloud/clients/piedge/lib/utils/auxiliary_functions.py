def equal_ignore_order(a, b):
    """Use only when elements are neither hashable nor sortable!"""
    unmatched = list(b)
    for element in a:
        try:
            unmatched.remove(element)
        except ValueError:
            return False
    return not unmatched


def check_availability(element, collection: iter):
    return element in collection


def return_equal_ignore_order(a, b):
    """Use only when elements are neither hashable nor sortable!"""
    equal = []
    for element in a:
        # if b is not None:

        if element in b:
            equal.append(element)
    return equal


def prepare_name_for_k8s(name):
    name = name.lower()
    # deployed_name = deployed_name.replace("-", "")
    name = name.replace("_", "")
    deployed_name_ = "".join([i for i in name if not i.isdigit()])
    return deployed_name_


def prepare_name(name, driver):
    if driver != "docker":
        name = name.lower()
        # deployed_name = deployed_name.replace("-", "")
        name = name.replace("_", "")
        deployed_name_ = "".join([i for i in name if not i.isdigit()])
        return deployed_name_.rstrip("-")
    else:
        return name
