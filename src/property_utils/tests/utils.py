def add_to(test_suite):

    def wrapper(cls):
        for test_method in {m for m in dir(cls) if m.startswith("test_")}:
            test_suite.addTest(cls(test_method))
        return cls

    return wrapper
