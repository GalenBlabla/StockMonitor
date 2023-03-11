
import inspect
from fetcher import fetcher
from fetcher import monitor


def get_custom_classes(module):
    """
    Returns a list of all the custom classes defined in the given module.
    """
    classes = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__module__ == module.__name__ and not inspect.isbuiltin(obj):
            classes.append(obj)
    return classes


if __name__ == '__main__':
    fetcher_classes = get_custom_classes(fetcher)
    monitor_classes = get_custom_classes(monitor)
    print(fetcher_classes)
    print(monitor_classes)
