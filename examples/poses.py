import json

def convert_poses():
    starting_rack = {}
    finishing_well = {}
    finishing_rim = {}

    poses = {
        'starting': starting_rack,
        'finishing_well': finishing_well,
        'finishing_rim': finishing_rim,
    }

    with open("pose_measurements/messy_rack_poses.txt") as file:    
        line = file.readline()
        
        while line:
            location, coord = line.strip().split(sep=":")
            
            file.readline()
            
            poses[location][coord] = file.readline()
            
            line = file.readline()

    with open('pose_measurements/rack_poses.json', 'w') as file:
        file.write(json.dumps(poses, indent=4))
    
def get_rack_poses():
    with open("pose_measurements/rack_poses.json") as file:
        raw_poses = json.load(file)
        
    poses = {}
    
    for name, dict in raw_poses.items():
        poses[name] = {}
        for coord, pose in dict.items():
            
            cleaned_post = pose.replace("[", "").replace("]", "").strip()
                        
            float_pose = [float(x) for x in cleaned_post.split()]
                        
            poses[name][eval(coord)] = float_pose
                
    return poses
            
def average_row_gap(poses: dict, rows: int, cols: int):
    sum = 0
    
    for i in range(cols):
        for j in range(rows-1):
            sum += abs(poses[(j, i)][0] - poses[(j+1, i)][0])

    average = sum / (cols * (rows - 1))
    
    return average
    
def average_column_gap(poses: dict, rows: int, cols: int):
    sum = 0
    
    for i in range(rows):
        for j in range(cols-1):
            print(f"comparing {(i, j)} with {(i, j+1)}")
            sum += abs(poses[(i, j)][1] - poses[(i, j+1)][1])

    average = sum / (rows * (cols - 1))
    
    return average
    
if __name__ == "__main__":
    poses = get_rack_poses()
    
    print(poses['starting'][(0, 0)])
    print(poses['finishing_rim'][(0, 0)])
    
    starting_row_gap = average_row_gap(poses['starting'], 2, 4)
    starting_col_gap = average_column_gap(poses['starting'], 2, 4)
    print(f"Start row gap: {starting_row_gap}")
    print(f"Start column gap: {starting_col_gap}")
    
    finishing_well_col_gap = average_column_gap(poses['finishing_well'], 1, 4)
    finishing_rim_col_gap = average_column_gap(poses['finishing_rim'], 1, 4)
    finishing_col_gap = (finishing_well_col_gap + finishing_rim_col_gap) / 2
    
    print(f"Finishing column gap: {finishing_col_gap}")