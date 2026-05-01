import matplotlib.pyplot as plt
from vial import Vial
import os

def graph_results(vials: list[Vial], folder, timeout):
    num_vials = len(vials)
    
    volumes = [vial.volume for vial in vials]
    time_to_green = [vial.yellow_to_green for vial in vials]
            
    for i in range(num_vials):
        marker = 'o'
        colour = 'green'
        volume = volumes[i]
        time = time_to_green[i]
        
        if time is None:
            time = timeout
            marker = 'x'
            colour = 'red'
        
        plt.scatter(volume, time, marker=marker, color=colour)
        
        if i < num_vials-1:            
            x = [volume, volumes[i+1]]
            
            next_time = time_to_green[i+1] if time_to_green[i+1] is not None else timeout
            y = [time, next_time]
            
            if time < timeout > next_time:
                plt.plot(x, y, color='green', linestyle='-', alpha=0.8)
            else:
                plt.plot(x, y, color='red', linestyle='--', alpha=0.4)
        
    plt.ylabel("Time to green (s)")
    plt.ylim(0, (timeout * 1.1))
    
    plt.xlabel("Volume of NaOH (ml)")
    
    x_buffer = (max(volumes) - min(volumes)) * 0.1

    plt.xlim(min(volumes) - x_buffer, max(volumes) + x_buffer)
    plt.title("Effect of NaOH on reaction speed in the Traffic Light Experiment")

    plt.axhline(y=timeout, color="grey", linestyle=":", label="Timeout")
    plt.legend()
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    path = os.path.join(folder, "results_graph.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.show()
    
    plt.close()