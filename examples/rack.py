from enum import Enum

class VialState(Enum):
    PRESENT = 0
    EMPTY = 1
    UNKNOWN = 2

class Rack():
    def __init__(self, rows: int, cols: int, row_gap: float, col_gap: float, top_left_picking_tcp: list[float]) -> None:
        self.rows = rows
        self.cols = cols
        self.row_gap = row_gap
        self.col_gap = col_gap
        self.top_left = top_left_picking_tcp
        
        self.state = [
            [VialState.UNKNOWN for _ in range(self.cols)] 
            for _ in range(self.rows)
        ]
        
    def __len__(self) -> int:
        return self.rows * self.cols
    
    def __repr__(self) -> str:
        return f'Rack(rows = {self.rows}, row_gap = {self.row_gap}, cols = {self.cols}, col_gap = {self.col_gap})'
    
    def __iter__(self):
        for i in range(self.rows):
            for j in range(self.cols):
                yield (i, j, self.state[i][j])
                
    def check_indices(self, row: int, col: int):
        if not 0 <= row < self.rows:
            raise IndexError(f"IndexError: Row {row} out of range 0...{self.cols}")
        
        if not 0 <= col < self.cols:
            raise IndexError(f"IndexError: Column {col} out of range 0...{self.cols}")
           
    def set_rack_state(self, state: list[list[VialState]]) -> None:
        self.state = state
                    
    def set_vial_state(self, row: int, col: int, vial_state: VialState):
        self.check_indices(row, col)

        self.state[row][col] = vial_state
            
    def get_vial_state(self, row: int, col: int) -> VialState:
        self.check_indices(row, col)
        
        return self.state[row][col]
                        
    def get_picking_tcp(self, row: int, col: int) -> list[float]:
        self.check_indices(row, col)
        
        pos = self.top_left.copy()
        
        pos[0] -= (row * self.row_gap)
        pos[1] -= (col * self.col_gap)

        return pos
        
    def get_above_tcp(self, row: int, col: int, vertical_gap: float) -> list[float]:
        self.check_indices(row, col)
        
        pos = self.get_picking_tcp(row, col)
        
        pos[2] += vertical_gap
        
        return pos
    
    def get_next_search_position(self) -> tuple[int, int] | None:
        for j in range(self.cols):
            for i in range(self.rows):
                if self.state[i][j] in (VialState.PRESENT, VialState.UNKNOWN):
                    return (i, j)
        return None
    
    def get_empty_spot(self) -> tuple[int, int] | None:
        for j in range(self.cols):
            for i in range(self.rows):
                if self.state[i][j] == VialState.EMPTY:
                    return (i, j)
        return None
        
    def print_state(self) -> None:
        for i in range(self.rows):
            line = ["╋", "---╋" * self.cols]
            print("".join(line))
        
            line = ["|"]
            for j in range(self.cols):
                match self.state[i][j]:
                    case VialState.PRESENT:
                        line.append(" ○ |")
                    case VialState.EMPTY:
                        line.append("   |")
                    case VialState.UNKNOWN:
                        line.append(" ? |")
                            
            print("".join(line))        
    
        line = ["╋", "---╋" * self.cols]
        print("".join(line))