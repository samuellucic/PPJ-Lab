class Table:
    def __init__(self, state_count:int, chars:list, sync:list):
        self.df = dict()
        for i in range(state_count):
            self.df[i] = dict()

        self.sync = sync

    def put(self, row:int, column:str, value:str) -> None:
        self.df[row][column] = value

    def get(self, row: int, column: str) -> str:
        if not self.df.get(row).get(column):
            return "nan"

        return self.df[row][column]

    def getRow(self, row:int) -> dict:
        return self.df[row]
