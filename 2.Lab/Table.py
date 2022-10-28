from pandas import DataFrame


class Table:
    def __init__(self, state_count:int, chars:list):
        self.df = DataFrame(index=range(state_count), columns=chars)
        self.state = 0

    def put(self, row:int, column:str, value:str) -> None:
        self.df.at[row, column] = value