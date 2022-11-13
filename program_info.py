import pickle


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ProgramInfo(metaclass=Singleton):
    def __init__(self):
        self.last_user_name = None

    @staticmethod
    def upload():
        try:
            with open('pickle/program_info.pkl', 'rb') as user_info:
                obj = pickle.load(user_info)
                return obj
        except FileNotFoundError:
            obj = ProgramInfo()
            obj.save()
            return obj

    def save(self):
        with open('pickle/program_info.pkl', 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)
