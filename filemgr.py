
class FileMgr:

    def createFile(self, filename):
        self.__handle = open(filename, "w")

    def writeToFile(self, txt):
        self.__handle.write(txt + "\n")

    def closeFile(self):
        self.__handle.close()