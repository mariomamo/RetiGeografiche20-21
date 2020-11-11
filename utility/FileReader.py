def readFromFile(filePath: str):
    with open(filePath, 'r') as file:
        return file.readlines()
