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
                    
            poses[location][coord] = file.readline()
            
            file.readline()
            line = file.readline()

    with open('pose_measurements/rack_poses.json', 'w') as file:
        file.write(json.dumps(poses, indent=4))

if __name__ == "__main__":
    convert_poses()