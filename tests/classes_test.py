class Parent:
    class Test:
        def __init__(self):
            print("test")

    def __init__(self, string):
        print(string)
        self.str1 = "func1"
        self.str2 = "func2"

    def func1(self):
        print(self.str1)

    def func2(self):
        print(self.str2)


class Child1(Parent):
    def __init__(self):
        super(Child1, self).__init__("test")
        print("eee")


child = Child1()
child.Test()
