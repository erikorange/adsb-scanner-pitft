
class FileMgr:

    def __init__(self):
        self.__isOpen = False

    def createFile(self, filename):
        self.__handle = open(filename, "w")
        self.__isOpen = True

    def writeToFile(self, txt):
        self.__handle.write(txt + "\n")

    def closeFile(self):
        if (self.__isOpen):
            self.__handle.close()
            self.__isOpen = False
        else:
            return