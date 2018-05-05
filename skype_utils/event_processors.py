from skpy import SkypeEventLoop


class SkypeEventProcessor(SkypeEventLoop):

    def onEvent(self, event):
        #print(repr(event))
        if repr(event).__contains__('SkypeCallEvent'):
             print("it is a call")
             print(event.time)
