class Data:

    def __init__(self, line=None, uniform=None) -> None:
        self.line = line
        
        if line:
            line = line.split()
            
            self.uniform = line[0]
            self.row = line[1]
            self.string = " ".join(line[2:])
        else:
            self.uniform = uniform

    def __str__(self) -> str:
        return self.line if self.line else self.uniform