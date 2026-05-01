import argparse
from traffic_light import TrafficLight
import time

MIN_NAOH = 0
MAX_NAOH = 50

STARTING_TOP_LEFT = [0.247303237, -0.50343651, 0.061092968, -0.000494386386, 3.10905968, 0.0322229148]
STARTING_BOTTOM_RIGHT = [2.06852955e-01, -5.83576160e-01,  6.73237370e-02, -5.29288419e-04, 3.10908896e+00,  3.22737449e-02]
FINISHING_TOP_LEFT = [-0.202857386, -0.519052008, 0.0701338522, -0.000535411239, 3.10906964, 0.032215583]
FINISHING_BOTTOM_RIGHT = [-0.201603630, -0.600121052, 0.0584810206, -0.000566768370, 3.10907973, 0.0322309248]
STIRRER = [0.01291479, -0.49279505,  0.14928015, -0.68575716, -3.05472425,  0.06999038]

def input_volumes(vials, cols):
    volumes = {}
    
    for i in range(vials):
        row, col = divmod(i, cols)
        volume = input(f"\n - NaOH (ml) in starting rack position [{row}, {col}]: ")
        
        while not volume.isnumeric() or float(volume) < MIN_NAOH or float(volume) > MAX_NAOH:
            print(f"\nError: Please input an integer between {MIN_NAOH} and {MAX_NAOH}")
            volume = input(f"\n - NaOH (ml) in starting rack position [{row}, {col}]: ")
        
        volumes[(row, col)] = int(volume)

    return volumes

def verify_volumes(vials, cols, rows):
    while(True):
        volumes = input_volumes(vials, cols)
        
        column_header = f"\n  {'     '.join([str(i) for i in (range(cols))])}"
        
        print(column_header)
        
        for row in range(rows):
            current_row = ""
            for col in range(cols):
                vol = volumes.get((row, col), 0)
                current_row += f"{vol:02d}ml   "
            
            print(f"{row} {current_row}")
        
        if(input("\nDoes this look correct (y/N): ").lower() == "y"):
            return volumes

def main():
    parser = argparse.ArgumentParser(description="Blue Bottle Experiment CLI")
    
    # Dimensions
    parser.add_argument("--start_rows", type=int, default=2, help="Number of rows in starting rack")
    parser.add_argument("--start_cols", type=int, default=4, help="Number of columns in starting rack")
    parser.add_argument("--end_rows", type=int, default=1, help="Number of rows in finishing rack")
    parser.add_argument("--end_cols", type=int, default=4, help="Number of columns in finishing rack")
    
    # Experimental variables
    parser.add_argument("--vials", type=int, required=True, help="Number of vials")

    args = parser.parse_args()
    
    print("====Traffic Light Experiment CLI ====")
    
    if args.vials > (args.start_rows * args.start_cols):
        print(f"Error: {args.vials} vials won't fit in the starting rack!")
        return
    if args.vials > (args.end_rows * args.end_cols):
        print(f"Error: {args.vials} vials won't fit in the finishing rack!")
        return
            
    volumes = verify_volumes(args.vials, args.start_cols, args.start_rows)
    
    experiment = TrafficLight()
    experiment.setup_starting_rack(cols=4, rows=2, row_gap=0.04434444625, col_gap=0.0262839015, top_left_tcp=STARTING_TOP_LEFT, bottom_right_tcp=STARTING_BOTTOM_RIGHT)
    experiment.setup_finishing_rack(cols=4, rows=1, row_gap=1, col_gap=0.027318555500000006, top_left_tcp=FINISHING_TOP_LEFT, bottom_right_tcp=FINISHING_BOTTOM_RIGHT)
    experiment.setup_stirrer(STIRRER)
    experiment.setup_volumes(volumes)
    
    print("Starting experiment...")
    experiment.run(args.vials)
            
if __name__ == "__main__":
    main()