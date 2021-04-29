class CollectAndDispatch():

    def __init__(self, f, num_states):
        self.f = f
        self.args = []
        self.num_states = num_states
        assert num_states > 0, "Error -- num states must be > 0"
        self.num_args = num_states

    def call_and_dump(self):
        try:
            result = self.f(*self.args)
        except Exception as e:
            raise e
        else:
            return result
        finally:
            self.args = []


    def add_arg(self, arg):
        self.args.append(arg)
        if len(self.args) == self.num_states:
            return self.call_and_dump()
        else:
            return None


class RefreshServerTransportAttr():

    def __init__(self):
        self._value = None

    def __set__(self, cls, value):
        self._value = cls.server.transport # this statement is really an assertion -> Class 'cls' has an attribute named 'server'. 'Server', in turn, has an attribute named 'transport'

    def __get__(self, instance, name):
        assert hasattr(instance, 'server'), "Error -- the whole point of this is to dynamically look up an attribute that is specifically named 'server.transport' and you don't even have a server attribute"
        class Instancer():
            def __init__(self, transport):
                self.transport = transport

            def write(self, message):
                encoded_string_message = str(message).encode("utf-8")
                self.transport.write(encoded_string_message)

        return Instancer(instance.server.transport)


class ServerCollector(CollectAndDispatch):

    writer = RefreshServerTransportAttr()

    def __init__(self, server, *args, **kwargs):
        self.server = server
        #self.writer = server.transport
        super().__init__(*args, **kwargs)

    def add_decorator(f):
        function_name = f.__name__
        function = super().__dict__[function_name]
        def call(self, *args, **kwargs):
            result = function(self, *args, **kwargs)
            return result
        return call


    def write(f):
        def call(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            if result is not None:
                self.writer.write(result)
            return result
        return call

    def writeln(f):
        def call(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            if result is not None:
                self.writer.write(result)
                self.writer.write("\n\r")
            return result
        return call


    @write
    def add_arg(self, arg):
        super().add_arg(arg)

    def add_prompt(f):
        def call(self, message):
            result = f(self, message)
            self.writer.write(">>>> ")
            return result
        return call

    @add_prompt
    def send_message(self, message):
        self.writer.write("your message was receieved in good faith\r\n")
        self.add_arg(message.decode('utf-8'))
        return

    @writeln
    def call_and_dump(self):
        print("calling...")
        return super().call_and_dump()


c = CollectAndDispatch(lambda x, y: x + y, 2)


class Machine():

    def __init__(self):
        self.erroring = False

    def process_command(self, input):
        pass