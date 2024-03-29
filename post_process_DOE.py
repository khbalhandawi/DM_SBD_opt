# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 18:06:53 2020

@author: Khalil
"""
import sys, os
import random
from numpy import random
import pickle
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import rcParams
from matplotlib.ticker import MaxNLocator
from scipy.spatial import ConvexHull, convex_hull_plot_2d
from scipy.io import loadmat
from sample_requirements import scaling
import copy
import csv

#==============================================================================
# Acquire requirements DOE design results and 
# get dictionary data from design log and resiliance log
def plot_tradespace(attribute,filename_opt,filename_res,filename_weight,
    plot_true = True, n_points = 100000 ):
        
    if plot_true:
        plt.close('all')
    
    current_path = os.getcwd()
    filepath = os.path.join(current_path,'DOE_results',filename_opt)
    
    data = []
    
    attribute_label = attribute[0]
    
    data = np.loadtxt(filepath, skiprows = 1, delimiter=",")
    
    # Read raw data
    with open(filepath) as f:
        line = f.readline()
        list_names = line.split(',')
        list_names[-1] = list_names[-1].split('\n')[0]
        
    # assign data to dictionary
    data = data.transpose()
    dictionary = dict(zip(list_names, data))
    #==========================================================================
    # read resiliance data
    current_path = os.getcwd()
    filepath = os.path.join(current_path,'Input_files',filename_res)
    
    data = []
    
    attribute_label = attribute[0]
    
    # Read raw data
    with open(filepath) as f:
        lis = [line.split() for line in f]        # create a list of lists
        for i, x in enumerate(lis):              #print the list items 
            if i == 0:
                list_names = x[0].split(',')
            elif i == 1:
                line_data = x[0].split(',')
                line_data = [float(i) for i in line_data]
                data = np.array([line_data])
            else:
                line_data = x[0].split(',')
                line_data = [float(i) for i in line_data]
                data = np.vstack((data,line_data))
            
    # assign data to dictionary
    data = data.transpose()
    dictionary_res = dict(zip(list_names, data))
    #==========================================================================
    # read weight data
    current_path = os.getcwd()
    filepath = os.path.join(current_path,'Input_files',filename_weight)
    
    data = []
    
    attribute_label = attribute[0]
    
    # Read raw data
    with open(filepath) as f:
        lis = [line.split() for line in f]        # create a list of lists
        for i, x in enumerate(lis):              #print the list items 
            if i == 0:
                list_names = x[0].split(',')
            elif i == 1:
                line_data = x[0].split(',')
                line_data = [float(i) for i in line_data]
                data = np.array([line_data])
            else:
                line_data = x[0].split(',')
                line_data = [float(i) for i in line_data]
                data = np.vstack((data,line_data))
            
    # assign data to dictionary
    data = data.transpose()
    dictionary_weight = dict(zip(list_names, data))
    
    # %% Initialize combinatorial optimization
    
    if plot_true:
        # This is not necessary if `text.usetex : True` is already set in `matplotlibrc`.    
        mpl.rc('text', usetex = True)
        rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}',
                                           r'\usepackage{amssymb}']
        rcParams['font.family'] = 'serif'
        my_dpi = 100
        fig = plt.figure(figsize=(700/my_dpi, 500/my_dpi), dpi=my_dpi)
    
    branch_id = 1
    designs = []; designs_padded = []
    # loop over data points
    for data in zip(dictionary['concept'],
                    dictionary['s1'],dictionary['s2'],dictionary['s3'],
                    dictionary['s4'],dictionary['s5'],dictionary['s6'],
                    dictionary['w1'],dictionary['w2'],dictionary['w3'],
                    dictionary['w4'],dictionary['w5'],dictionary['w6'],
                    dictionary['R1'],dictionary['R2'],dictionary['R3'],
                    dictionary['R4'],dictionary['R5'],dictionary['R6']):
        
        [c,s1,s2,s3,s4,s5,s6,w1,w2,w3,w4,w5,w6,R1,R2,R3,R4,R5,R6] = data
        
        if c != -1:
            
            resiliance = [R1,R2,R3,R4,R5,R6]
            weight = [w1,w2,w3,w4,w5,w6]
            
            # Get design index
            i = 0
            design_index = [int(c),]; x_data = []; y_data = []
            for arg in [s1,s2,s3,s4,s5,s6]:
                if not int(arg) == -1:
                    design_index += [int(arg)] # populate permutation index
                
                x_data += [i+1]
                y_data += [resiliance[i]]
                
                i += 1
            
            design_index_padded = copy.deepcopy(design_index)
            if len(design_index) < 6:
                design_index_padded += [-1]*(6-len(design_index))
            
            designs_padded += [design_index_padded]
            designs += [design_index]
            
            if plot_true:
                # generate random color for branch
                r = random.random()
                g = random.random()
                b = random.random()
                rgb = [r,g,b]

                plt.plot(x_data, y_data, ':', color = rgb, linewidth = 2.5 )
                # plt.plot(x_data, y_data, 'o', markersize=10, markevery=len(x_data), color = [0,0,0])
                plot_h, = plt.plot(x_data, y_data, 'o', color = [0,0,1], markersize=6 )
            
            branch_id += 1
            
            if branch_id == n_points + 1:
                break
      
    if plot_true:
        ax = plt.gca() 
        ax.tick_params(axis='both', which='major', labelsize=14) 
        
        plt.title("Tradespace", fontsize=20)
        plt.xlabel('Design stage number', fontsize=14)
        plt.ylabel(attribute_label, fontsize=14)
    
        return dictionary,dictionary_res,dictionary_weight,designs,designs_padded,fig,ax,plot_h
    else:
        return dictionary,dictionary_res,dictionary_weight,designs,designs_padded

#==============================================================================
# Import feasibility data
def import_feasibility(filename_feas):
    
    current_path = os.getcwd()
    filepath = os.path.join(current_path,'DOE_results',filename_feas)
    
    data = np.loadtxt(filepath, skiprows = 1, delimiter=",")
    
    # Read raw data
    with open(filepath) as f:
        line = f.readline()
        list_names = line.split(',')
        list_names[-1] = list_names[-1].split('\n')[0]
        
    # assign data to dictionary
    data = data.transpose()
    dictionary = dict(zip(list_names, data))
    feasiblity = (np.sum(data[1:], axis = 1) * 100) / len(data[0])

    return data, feasiblity
    
#==============================================================================
# Calculate filtered outdegree
def filtered_outdegree(dictionary_weight):
    
    design_list = []; FO = []
    for data in zip(dictionary_weight['concept'],
                    dictionary_weight['i1'],dictionary_weight['i2'],
                    dictionary_weight['i3'],dictionary_weight['i4'],
                    dictionary_weight['i5']):
        design_list += [[int(x) for x in data]]

        deposits = data[1:]
        if data[0] == 0: # wave stiffener
            FO += [2 - sum(d != -1 for d in deposits)]
        elif data[0] == 1: # hatched stiffener
            FO += [5 - sum(d != -1 for d in deposits)]
        elif data[0] == 2: # tubular stiffener
            FO += [3 - sum(d != -1 for d in deposits)]

    return FO
    
#==============================================================================
# Call MADS and get Pareto optimal solutions from MADS
def system_command(command):
    import subprocess
    from subprocess import PIPE,STDOUT
    #CREATE_NO_WINDOW = 0x08000000 # Creat no console window flag

    p = subprocess.Popen(command,shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                         ) # disable windows errors

    for line in iter(p.stdout.readline, b''):
        line = line.decode('utf-8')
        print(line.rstrip()) # print line by line
        # rstrip() to reomove \n separator

def NOMAD_call_BIOBJ(req_index,weight_file,res_ip_file,excess_ip_file,
                     res_th_file,excess_th_file,P_analysis_strip,
                     attribute,cost,evaluate):
    
    if evaluate: # run bi-objective optimization

        command = "categorical_biobj %i %s %s %s %s %s" %(req_index,weight_file,res_ip_file,excess_ip_file,res_th_file,excess_th_file)
        print(command)
        system_command(command)
    
    [x_data, y_data] = get_pareto(P_analysis_strip,attribute,cost)

    return x_data, y_data

#==============================================================================
# Get Pareto optimal solutions from MADS
def get_pareto(P_analysis_strip,attribute,cost):
    
    filename = 'mads_x_opt_pareto.log'
    current_path = os.getcwd()
    filepath = os.path.join(current_path,'MADS_output',filename)
    
    # %% read MADS log file
    opt_points = []
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ')
        line_count = 0
        for row in csv_reader:
            row = [int(item) for item in row]
            row_strip = row[1::]
                    
            opt_points += [row_strip]
            line_count += 1
    
    # iterate through MADS bb evals
    current_path = os.getcwd()
    print('\nNumber of pareto points: %i' %(line_count))
    for point in opt_points:
        print(point)
    
    x_data = []; y_data = []
    for point in opt_points:
        ind = P_analysis_strip.index(point)

        attribute_Pareto = attribute[ind]
        cost_Pareto = cost[ind]
        
        x_data += [cost_Pareto]
        y_data += [attribute_Pareto]
        
    return x_data, y_data

#==============================================================================
# rank designs and get histogram distribution
def rank_designs(designs):
    
    # one-liner to read a single variable
    filename = 'DOE_permutations.mat'
    current_path = os.getcwd()
    filepath = os.path.join(current_path,'Input_files',filename)
    
    P_analysis = loadmat(filepath)['P_analysis']
    
    index = 0; P_analysis_strip = []
    histogram = np.zeros(len(P_analysis), dtype = int) 
    
    P_analysis_strip = []
    for P_i in P_analysis:

        # Get permutation index
        permutation_index = []
        for arg in P_i:
            if not int(arg) == -1:
                permutation_index += [int(arg)] # populate permutation index
        P_analysis_strip += [permutation_index]
        
        # loop over data points
        for design in designs:

            # check if permutation index contained within branch
            if design == permutation_index:
                histogram[index] += 1
        
        index += 1 

    return histogram,P_analysis_strip

#==============================================================================
# Get pie chart distribution for each deposit and concept
def get_dstribution(d_types,k,design_list):
    
    dist = np.zeros(len(d_types), dtype = int) 
    
    index = 0  
    for d_type in d_types:
        
        # loop over data points
        for design in design_list:
            # check if permutation index contained within branch
            if design[k] == d_type:
                dist[index] += int(1)   
        
        index += 1
        
    return dist

#==============================================================================
# Convert color floats to hex
def rgb2hex(color):
    """Converts a list or tuple of color to an RGB string

    Args:
        color (list|tuple): the list or tuple of integers (e.g. (127, 127, 127))

    Returns:
        str:  the rgb string
    """
    return f"#{''.join(f'{hex(c)[2:].upper():0>2}' for c in color)}"

#==============================================================================
# Extract designs inside specific concept
def extract_designs(designs,concept):
    
    designs_extract = []
    for design in designs:
        if design[0] == concept:
            designs_extract += [design]

    return designs_extract

#==============================================================================
# compute convex hull and hyper rectangle volume
def get_HP_volume(points_x,points_y,lb,ub):
    lb_CV = np.array([min(points_x),min(points_y)])
    ub_CV = np.array([max(points_x),max(points_y)])

    lb_CV_n = scaling(lb_CV,lb,ub,1)
    ub_CV_n = scaling(ub_CV,lb,ub,1)

    v_HP = np.prod(ub_CV_n - lb_CV_n)
    
    return v_HP

#==============================================================================
# compute convex hull shortest distance to pareto
def shortest_distance(x_pareto,y_pareto,point_x,point_y):

    distances = []
    for x_p, y_p in zip(x_pareto,y_pareto):
        diff = np.array([x_p - point_x, y_p - point_y])
        dist = np.linalg.norm(diff)
        distances += [dist]

    shortest = min(distances)

    return shortest

#==============================================================================
# Histogram colors generator
def color_generator(new_colors,color_file,indices = [],histogram = []):

    # ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', ...]
    colors_default = plt.rcParams['axes.prop_cycle'].by_key()['color']

    top_10 = indices[:10]
    if new_colors:
        colors = []
        for i in range(0,len(histogram)):
            r = random.random()
            g = random.random()
            b = random.random()
            rgb = [int(r*256),int(g*256),int(b*256)]
            colors += [rgb2hex(rgb).lower()]
        
        # color top 10 designs using default color palette
        for i,color in zip(top_10,colors_default):
            colors[i] = color

        with open(color_file, 'wb') as pickle_file:
            pickle.dump(colors,pickle_file)
    else:
        fid = open(color_file, 'rb')
        colors = pickle.load(fid)
        fid.close()

    return colors,colors_default

#==============================================================================
# Parallel plots for tradespace
def parallel_plots(input_data,output_data,in_data_labels,out_data_labels,plot_filename,c_index=6):
    import plotly.graph_objs as go # Used to create data structure for plotly
    from plotly.offline import plot, iplot, init_notebook_mode # Import offline plot functions from plotly

    #=============================================================================#
    #Create Data Structure

    data_list = []; i_index = 0
    for in_data,in_label in zip(input_data.T,in_data_labels):
        if i_index == c_index:
            data_list += [dict(label = in_label, values = in_data, tickformat=".2f%",constraintrange = [2.0,3.0])]
        else:
            data_list += [dict(label = in_label, values = in_data, tickformat=".2f%")]

        i_index += 1

    for out_data,out_label in zip(output_data.T,out_data_labels):
        data_list += [dict(label = out_label, values = out_data, tickformat=".2f%")]
        

    # colorscale = [
    #     [0.00,"#0000FF"],
    #     [0.01,"#00FFA5"],
    #     [0.02,"#00FF00"],
    #     [0.05,"#FFA500"],
    #     [1.00,"#FF0000"],
    # ]

    colorscale = 'tealrose'

    data_pd = [
        go.Parcoords(
            line = dict(color = output_data[:,1],
                        colorscale = colorscale,
                        cmin = 0,
                        cmax = 70,
                        showscale = True),
            dimensions = data_list
        )
    ]

    plot(data_pd, show_link=False, filename = plot_filename, auto_open=True)


#==============================================================================
# MAIN CALL
if __name__ == "__main__":

    #==============================================================================
    # Read system arguments

    if len(sys.argv) == 3:
        n_points = int(float(sys.argv[1]))
        plot_index = int(float(sys.argv[2]))
    else:
        n_points = 100000
        plot_index = 1

    # plot_option = "DPSRF"
    plot_option = "DPSRF"; display_points = True; display_CH = True; display_centroid = True
    #==============================================================================
    # Read DOE results from file

    mpl.rcParams['font.size'] = 14.0
    
    plt.close('all')

    filename_feas = 'feasiblity_log_full.log' # <------------------------------------------ Set the desired date to postprocess
    # filename_opt = 'req_opt_E_log_full.log' # optimize with respect to excess
    filename_opt = 'req_opt_log_full.log' # optimize with respect to weight <-------------- Set the desired date to postprocess
    filename_res = 'resiliance_th.log'
    filename_excess = 'excess_th.log'
    filename_res_ip = 'resiliance_ip.log'
    filename_excess_ip = 'excess_ip.log'
    filename_weight = 'varout_opt_log.log'

    run_opt_pareto = False # run Bi-OBJ NOMAD to find Pareto front

    #attribute = ['n_f_th','Safety factor ($n_{safety}$)']
    attribute = ['Reliability ($\mathbb{P}(\mathbf{p} \in C)$)']
    
    # [fig, ax, dictionary, plot_h, designs] = plot_tradespace(attribute,True)
    [dictionary, dictionary_res, dictionary_weight, designs, designs_padded] = plot_tradespace(attribute,filename_opt,filename_res,filename_weight,plot_true=False,
        n_points=n_points)
    [histogram,P_analysis_strip] = rank_designs(designs)
    design_list = []
    for data in zip(dictionary_weight['concept'],
                    dictionary_weight['i1'],dictionary_weight['i2'],
                    dictionary_weight['i3'],dictionary_weight['i4'],
                    dictionary_weight['i5']):
        design_list += [[int(x) for x in data]]
    
    alpha = 10 # number of top designs to analyze
    alpha_F = 10 # number of top flexible designs to analyze

    #==============================================================================
    # Set based sorting

    xS = range(0,len(histogram))
    yS = sorted(histogram,reverse = True)
    indices = [x for _,x in sorted(zip(histogram,xS),reverse = True)]
    sorted_designs = [x for _,x in sorted(zip(histogram,design_list),reverse = True)]
    
    print('Top %i SBD designs:' %(alpha))
    for design in sorted_designs[:alpha]:
        print(design)
    # data for constructing tradespace of feasible designs
    # req_index = 50
    # attribute = dictionary_res['req_index_%i' %(req_index)]
    req_index = 0
    attribute = dictionary_weight['capability_th_uni']
    cost = dictionary_weight['weight']

    # Data for plotting SBD designs
    attribute_SBD = attribute[indices]
    cost_SBD = cost[indices]
    
    #==============================================================================
    # robustness sorting
    [data,robustness] = import_feasibility(filename_feas)

    xR = range(0,len(robustness))
    yR = sorted(robustness,reverse = True)
    indices_robust = [x for _,x in sorted(zip(robustness,xR),reverse = True)]
    sorted_designs_robust = [x for _,x in sorted(zip(robustness,design_list),reverse = True)]
    
    print('Top %i robust designs:' %(alpha))
    for design in sorted_designs_robust[:alpha]:
        print(design)
    # data for constructing tradespace of feasible designs
    # req_index = 50
    # attribute = dictionary_res['req_index_%i' %(req_index)]

    # Data for plotting SBD designs
    attribute_robust = attribute[indices_robust]
    cost_robust = cost[indices_robust]

    #==============================================================================
    # flexibility sorting
    FO = filtered_outdegree(dictionary_weight)

    xF = range(0,len(FO))
    yF = sorted(FO,reverse = True)
    indices_flexible = [x for _,x in sorted(zip(FO,xF),reverse = True)]
    sorted_designs_flexible = [x for _,x in sorted(zip(FO,design_list),reverse = True)]
    
    print('Top %i flexible designs:' %(alpha_F))
    for design in sorted_designs_flexible[:alpha_F]:
        print(design)
    # data for constructing tradespace of feasible designs
    # req_index = 50
    # attribute = dictionary_res['req_index_%i' %(req_index)]

    # Data for plotting SBD designs
    attribute_flexible = attribute[indices_flexible]
    cost_flexible = cost[indices_flexible]

    #==========================================================================
    # Histogram colors generator

    new_colors = False
    color_file = 'colors_histogram.pkl'
    colors,colors_default = color_generator(new_colors,color_file,indices,histogram)
    highlight_on = True
    colored_bars = False
    #==========================================================================
    # Histogram plot for robust designs
    # data for plotting histogram feasibility
    
    n_bins = 15
    x = xR[:n_bins]
    y = yR[:n_bins]
    design_indices = [i + 1 for i in indices_robust[:n_bins]]
    if colored_bars:
        design_colors = [colors[i] for i in indices_robust[:n_bins]] # Colored bars
    else:
        design_colors = colors_default[0] # blue bars
    # design_indices = list(range(1,21)

    mpl.rc('text', usetex = True)
    rcParams['font.family'] = 'serif'
    my_dpi = 100
    fig = plt.figure(figsize=(700/my_dpi, 500/my_dpi), dpi=my_dpi)
    
    barlist = plt.bar(x, y, width=0.8, bottom=None, align='center', data=None, color=design_colors )
    bar_i = 0
    for bar in barlist: # set color of first five bars
        if bar_i < alpha and highlight_on:
            bar.set_edgecolor('r')
            bar.set_linewidth(2.3)
        else:
            bar.set_edgecolor('k')
            bar.set_linewidth(1.0)
        bar_i += 1

    plt.xlabel('Design arc index $\lambda$', fontsize=14)
    # plt.xlabel('Unique design solution', fontsize=14)
    plt.ylabel('$\%$ of requirement arcs satisfied', fontsize=14) 
    plt.xticks(list(range(n_bins)), list(map(str,design_indices)))

    tight_bbox = fig.get_tightbbox(fig.canvas.get_renderer()) # get bbox for figure canvas
    fig.savefig(os.path.join(os.getcwd(),'DOE_results','histogram_DOE_R.png'), format='png', dpi=1000,bbox_inches=tight_bbox)

    #==========================================================================
    # Histogram plot for flexible designs
    # data for plotting histogram feasibility

    n_bins = 15
    x = xF[:n_bins]
    y = yF[:n_bins]
    design_indices = [i + 1 for i in indices_flexible[:n_bins]]
    if colored_bars:
        design_colors = [colors[i] for i in indices_robust[:n_bins]] # Colored bars
    else:
        design_colors = colors_default[0] # blue bars

    # design_indices = list(range(1,21)

    mpl.rc('text', usetex = True)
    rcParams['font.family'] = 'serif'
    my_dpi = 100
    fig = plt.figure(figsize=(700/my_dpi, 500/my_dpi), dpi=my_dpi)
    
    barlist = plt.bar(x, y, width=0.8, bottom=None, align='center', data=None, color=design_colors )
    bar_i = 0
    for bar in barlist: # set color of first five bars
        if bar_i < alpha_F and highlight_on:
            bar.set_edgecolor('r')
            bar.set_linewidth(2.3)
        else:
            bar.set_edgecolor('k')
            bar.set_linewidth(1.0)
        bar_i += 1

    plt.xlabel('Design arc index $\lambda$', fontsize=14)
    # plt.xlabel('Unique design solution', fontsize=14)
    plt.ylabel('Filtered outdegree $O_F$', fontsize=14) 
    plt.xticks(list(range(n_bins)), list(map(str,design_indices)))
    plt.yticks(list(range(max(yF)+1)), list(map(str,range(max(yF)+1)))) # Force integer ticks
    fig.savefig(os.path.join(os.getcwd(),'DOE_results','histogram_DOE_F.png'), format='png', dpi=1000,bbox_inches=tight_bbox)

    #==========================================================================
    # Histogram plot
    # data for plotting histogram SBD
    alpha = 10 # number of top designs to analyze

    n_bins = 15
    x = xS[:n_bins]
    print('Total frequency : %f' %(sum(yS)))
    y = yS[:n_bins]/(sum(yS)*0.01)
    design_indices = [i + 1 for i in indices[:n_bins]]
    if colored_bars:
        design_colors = [colors[i] for i in indices_robust[:n_bins]] # Colored bars
    else:
        design_colors = colors_default[0] # blue bars

    # design_indices = list(range(1,21)

    mpl.rc('text', usetex = True)
    rcParams['font.family'] = 'serif'
    my_dpi = 100
    fig = plt.figure(figsize=(700/my_dpi, 500/my_dpi), dpi=my_dpi)
    
    barlist = plt.bar(x, y, width=0.8, bottom=None, align='center', data=None, color=design_colors )
    bar_i = 0
    for bar in barlist: # set color of first five bars
        if bar_i < alpha and highlight_on:
            bar.set_edgecolor('r')
            bar.set_linewidth(2.3)
        else:
            bar.set_edgecolor('k')
            bar.set_linewidth(1.0)
        bar_i += 1

    plt.xlabel('Design arc index $\lambda$', fontsize=14)
    # plt.xlabel('Unique design solution', fontsize=14)
    plt.ylabel('Relative frequency ($\%$)', fontsize=14) 
    plt.xticks(list(range(n_bins)), list(map(str,design_indices)))
    # plt.gca().set_ylim((0,9.9))

    fig.savefig(os.path.join(os.getcwd(),'DOE_results','histogram_DOE_E_%i.png'%(plot_index)), format='png', dpi=1000,bbox_inches=tight_bbox)
    
    print("==============================")
    print("Percentage of R space dominated: %f" %(sum(y[:10])))
    print("==============================")

    #==========================================================================
    # Tradespace plot
    # data for plotting Pareto front
    [x_data, y_data] = NOMAD_call_BIOBJ(req_index,filename_weight,filename_res_ip,filename_excess_ip,
                                        filename_res,filename_excess,P_analysis_strip,attribute,cost,run_opt_pareto) # get Pareto optimal points

    my_dpi = 100
    fig = plt.figure(figsize=(700/my_dpi, 500/my_dpi), dpi=my_dpi)
    
    markersizes = [ (1/20)*(n**4) for n in reversed(range(3,len(cost_SBD[:10])+3)) ]

    l_D = '$\{c,\mathbf{D}\} \in \Omega_{cD}$'
    l_P = 'Pareto optimal design arcs'
    l_R = 'Robust design arcs'
    l_F = 'Flexible design arcs'
    l_S = 'Set-based design arcs'

    legend_h = []; legend_labels = [];
    if "D" in plot_option:

        if display_points:
            feasible, = plt.plot(cost, attribute, '.', color = [0,0,0], linewidth = 1, markersize = 3 )
        else:
            feasible = mlines.Line2D([], [], color='black', marker='x', markersize=5, linestyle='')
        legend_h += [feasible]; legend_labels += [l_D]

    if "P" in plot_option:
        pareto, = plt.plot(x_data, y_data, '-d', color = 'm', linewidth = 4.0, markersize = 7.0 )
        legend_h += [pareto]; legend_labels += [l_P]
    if "R" in plot_option:
        
        if display_points:
            Robust_design = plt.scatter( cost_robust[:alpha], attribute_robust[:alpha], s = 600, color = [0,0,1], marker = '.', zorder=3)
        else:
            Robust_design = mlines.Line2D([], [], color='blue', marker='.', markersize=7, linestyle='')
        legend_h += [Robust_design]; legend_labels += [l_R]

    if "F" in plot_option:

        if display_points:
            flexible_design = plt.scatter( cost_flexible[:alpha_F], attribute_flexible[:alpha_F], s = 300, color = [34/256,139/256,34/256], marker = '.', zorder=4 )
        else:
            flexible_design = mlines.Line2D([], [], color='green', marker='.', markersize=5, linestyle='')
        legend_h += [flexible_design]; legend_labels += [l_F]

    if "S" in plot_option:

        if display_points:
            SBD_design = plt.scatter( cost_SBD[:alpha], attribute_SBD[:alpha], s = 150, color = [1,0,0], marker = '.', zorder=5 )
        else:
            SBD_design = mlines.Line2D([], [], color='red', marker='.', markersize=5, linestyle='')
        legend_h += [SBD_design]; legend_labels += [l_S]

    plt.xlabel('Weight of stiffener $W$ (kg)', fontsize=14)
    # plt.ylabel('Requirement satisfaction ratio ($V_{{C}\cap{R}}/V_{R}$)', fontsize=14)
    plt.ylabel('Volume of capability set $V_c$', fontsize=14)

    # Convert data into a nx2 array
    pts_FE = np.hstack((np.reshape(cost, (-1, 1)), np.reshape(attribute, (-1, 1))))
    pts_R = np.hstack((np.reshape(cost_robust[:alpha], (-1, 1)), np.reshape(attribute_robust[:alpha], (-1, 1))))
    pts_F = np.hstack((np.reshape(cost_flexible[:alpha_F], (-1, 1)), np.reshape(attribute_flexible[:alpha_F], (-1, 1))))
    pts_SBD = np.hstack((np.reshape(cost_SBD[:alpha], (-1, 1)), np.reshape(attribute_SBD[:alpha], (-1, 1))))
    
    lb = np.array([min(cost),min(attribute)])
    ub = np.array([max(cost),max(attribute)])

    pts_FE = scaling(pts_FE,lb,ub,1)
    pts_R = scaling(pts_R,lb,ub,1)
    pts_F = scaling(pts_F,lb,ub,1)
    pts_SBD = scaling(pts_SBD,lb,ub,1)
    
    # get set-based convex hull data
    hull_FE = ConvexHull(pts_FE)
    CV_FE = hull_FE.volume
    # Get centroid
    cx_FE_n = np.mean(hull_FE.points[hull_FE.vertices,0])
    cy_FE_n = np.mean(hull_FE.points[hull_FE.vertices,1])
    cx_FE = scaling(cx_FE_n,lb[0],ub[0],2)
    cy_FE = scaling(cy_FE_n,lb[1],ub[1],2)
    print('Feasible set: Centroid: (%f, %f), Area: %f' %(cx_FE,cy_FE,CV_FE))
    print('Feasible set: LB: (%f, %f), UB: (%f, %f)' %(min(cost),min(attribute),
                                                       max(cost),max(attribute)))
    HV_FE = get_HP_volume(cost,attribute,lb,ub)
    print('Feasible set hyper rectangle volume: %f' %(HV_FE))

    # get set-based convex hull data
    hull_R = ConvexHull(pts_R)
    CV_R = hull_R.volume
    # Get centroid
    cx_R_n = np.mean(hull_R.points[hull_R.vertices,0])
    cy_R_n = np.mean(hull_R.points[hull_R.vertices,1])
    cx_R = scaling(cx_R_n,lb[0],ub[0],2)
    cy_R = scaling(cy_R_n,lb[1],ub[1],2)
    print('Robust set: Centroid: (%f, %f), Area: %f' %(cx_R,cy_R,CV_R))
    print('Robust set: LB: (%f, %f), UB: (%f, %f)' %(min(cost_robust[:alpha]),min(attribute_robust[:alpha]),
                                                     max(cost_robust[:alpha]),max(attribute_robust[:alpha])))
    HV_R = get_HP_volume(cost_robust[:alpha],attribute_robust[:alpha],lb,ub)
    print('Robust set hyper rectangle volume: %f' %(HV_R))
    
    # get flexible convex hull data
    hull_F = ConvexHull(pts_F)
    CV_F = hull_F.volume
    # Get centroid
    cx_F_n = np.mean(hull_F.points[hull_F.vertices,0])
    cy_F_n = np.mean(hull_F.points[hull_F.vertices,1])
    cx_F = scaling(cx_F_n,lb[0],ub[0],2)
    cy_F = scaling(cy_F_n,lb[1],ub[1],2)
    print('Flexible set: Centroid: (%f, %f), Area: %f' %(cx_F,cy_F,CV_F))
    print('Flexible set: LB: (%f, %f), UB: (%f, %f)' %(min(cost_flexible[:alpha_F]),min(attribute_flexible[:alpha_F]),
                                                       max(cost_flexible[:alpha_F]),max(attribute_flexible[:alpha_F])))
    HV_F = get_HP_volume(cost_flexible[:alpha_F],attribute_flexible[:alpha_F],lb,ub)
    print('Flexible set hyper rectangle volume: %f' %(HV_F))

    # get set-based convex hull data
    hull_SBD = ConvexHull(pts_SBD)
    CV_SBD = hull_SBD.volume
    # Get centoid
    cx_SBD_n = np.mean(hull_SBD.points[hull_SBD.vertices,0])
    cy_SBD_n = np.mean(hull_SBD.points[hull_SBD.vertices,1])
    cx_SBD = scaling(cx_SBD_n,lb[0],ub[0],2)
    cy_SBD = scaling(cy_SBD_n,lb[1],ub[1],2)
    print('SBD set: Centroid: (%f, %f), Area: %f' %(cx_SBD,cy_SBD,CV_SBD))
    print('SBD set: LB: (%f, %f), UB: (%f, %f)' %(min(cost_SBD[:alpha]),min(attribute_SBD[:alpha]),
                                                  max(cost_SBD[:alpha]),max(attribute_SBD[:alpha])))
    
    HV_SBD = get_HP_volume(cost_SBD[:alpha],attribute_SBD[:alpha],lb,ub)
    print('SBD set hyper rectangle volume: %f' %(HV_SBD))

    # compute distance to nearest pareto point
    x_data_n = scaling(x_data,lb[0],ub[0],1)
    y_data_n = scaling(y_data,lb[1],ub[1],1)

    dp_FE = shortest_distance(x_data_n,y_data_n,cx_FE_n,cy_FE_n)
    dp_R = shortest_distance(x_data_n,y_data_n,cx_R_n,cy_R_n)
    dp_F = shortest_distance(x_data_n,y_data_n,cx_F_n,cy_F_n)
    dp_SBD = shortest_distance(x_data_n,y_data_n,cx_SBD_n,cy_SBD_n)
    print('Feasible set shortest: %f' %(dp_FE))
    print('R set shortest: %f' %(dp_R))
    print('F set shortest: %f' %(dp_F))
    print('SBD set shortest: %f' %(dp_SBD))

    ax = plt.gca() 
    if display_CH:
        if "R" in plot_option:
            # Show convex hull (robust)
            start_x = hull_R.points[hull_R.vertices[0],0]; start_y = hull_R.points[hull_R.vertices[0],1]
            points_x = hull_R.points[hull_R.vertices,0]; points_y = hull_R.points[hull_R.vertices,1]
            points_x = np.append(points_x,start_x); points_y = np.append(points_y, start_y)
            
            Chull_unscaled_x = scaling(points_x,lb[0],ub[0],2) 
            Chull_unscaled_y = scaling(points_y,lb[1],ub[1],2) 

            ax.plot(Chull_unscaled_x, Chull_unscaled_y, 'b--', lw=2)
        
        if "F" in plot_option:
            # Show convex hull (flexible)
            start_x = hull_F.points[hull_F.vertices[0],0]; start_y = hull_F.points[hull_F.vertices[0],1]
            points_x = hull_F.points[hull_F.vertices,0]; points_y = hull_F.points[hull_F.vertices,1]
            points_x = np.append(points_x, start_x); points_y = np.append(points_y, start_y)

            Chull_unscaled_x = scaling(points_x,lb[0],ub[0],2) 
            Chull_unscaled_y = scaling(points_y,lb[1],ub[1],2) 

            ax.plot(Chull_unscaled_x, Chull_unscaled_y, 'g--', lw=2)
            
        if "S" in plot_option:
            # Show convex hull (SBD)
            start_x = hull_SBD.points[hull_SBD.vertices[0],0]; start_y = hull_SBD.points[hull_SBD.vertices[0],1]
            points_x = hull_SBD.points[hull_SBD.vertices,0]; points_y = hull_SBD.points[hull_SBD.vertices,1]
            points_x = np.append(points_x, start_x); points_y = np.append(points_y, start_y)

            Chull_unscaled_x = scaling(points_x,lb[0],ub[0],2) 
            Chull_unscaled_y = scaling(points_y,lb[1],ub[1],2) 

            ax.plot(Chull_unscaled_x, Chull_unscaled_y, 'r--', lw=2)
            
    if display_centroid:
        if "R" in plot_option:
            # Show centroid (robust)
            ax.plot(cx_R, cy_R, 'xb', lw=2)
        
        if "F" in plot_option:
            # Show centroid (flexible)
            ax.plot(cx_F, cy_F, 'xg', lw=2)
            
        if "S" in plot_option:
            # Show centroid (SBD)
            ax.plot(cx_SBD, cy_SBD, 'xr', lw=2)

    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.legend(legend_h, legend_labels, loc = 'lower right', fontsize = 9.0)

    ax.set_xlim([3.2040081632482553, 27.85608911395347]) # used for excess
    ax.set_ylim([-0.05000000000000002, 1.0500000000000003]) # used for excess

    fig.savefig(os.path.join(os.getcwd(),'DOE_results','tradespace_pareto_%s.png'%(plot_option)), format='png', dpi=1000,bbox_inches='tight')
    
    print(ax.get_xlim())
    print(ax.get_ylim())
    #==========================================================================
    # Pie chart plot   
    import matplotlib.gridspec as gridspec

    designs_padded_c0 = extract_designs(designs_padded,0)
    designs_padded_c1 = extract_designs(designs_padded,1)
    designs_padded_c2 = extract_designs(designs_padded,2)

    d_types = [0,1,2,3,4]
    i1 = get_dstribution(d_types,1,designs_padded_c1)
    i2 = get_dstribution(d_types,2,designs_padded_c1)
    i3 = get_dstribution(d_types,3,designs_padded_c1)
    i4 = get_dstribution(d_types,4,designs_padded_c1)
    i5 = get_dstribution(d_types,5,designs_padded_c1)
    
    d_types = [0,1,2]
    c = get_dstribution(d_types,0,designs_padded)
    
    gs = gridspec.GridSpec(2,3, 
                           width_ratios = np.ones(3,dtype=int), 
                           height_ratios = np.ones(2,dtype=int))
    
    my_dpi = 100
    fig = plt.figure(figsize=(1400/my_dpi, 1000/my_dpi), dpi=my_dpi)
    
    # Plot all stages
    iteraton = -1
    for item in [i1,i2,i3,i4,i5]:
        
        iteraton += 1
        
        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        labels = 'deposit 0', 'deposit 1', 'deposit 2', 'deposit 3', 'deposit 4'
        sizes = item
        explode = (0, 0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
        
        ax = fig.add_subplot(gs[iteraton]) # subplot
        ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
    # Plot 1st stage only
    my_dpi = 100
    fig = plt.figure(figsize=(700/my_dpi, 500/my_dpi), dpi=my_dpi)
        
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = '$D_1 = 0$', '$D_1 = 1$', '$D_1 = 2$', '$D_1 = 3$', '$D_1 = 4$'
    sizes = i1
    explode = (0, 0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    
    ax = plt.gca()
    patches, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                                shadow=False, startangle=90)
    
    for i in range(len(labels)):
        texts[i].set_fontsize(18)
        autotexts[i].set_fontsize(18)
    
    # Color a section of the pie
    patches[1].set_edgecolor('b')
    patches[1].set_linewidth(3)
    patches[1].set_hatch('\\')
        
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig.savefig(os.path.join(os.getcwd(),'DOE_results','1st_stage_pie.png'), format='png', dpi=1000,bbox_inches='tight')
    
    # Plot concept only
    my_dpi = 100
    fig = plt.figure(figsize=(700/my_dpi, 500/my_dpi), dpi=my_dpi)
        
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'concept 0', 'concept 1', 'concept 2'
    sizes = c
    explode = (0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    
    ax = plt.gca()
    ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig.savefig(os.path.join(os.getcwd(),'DOE_results','Concept_pie_chart.png'), format='png', dpi=1000,bbox_inches='tight')
    
    #==========================================================================
    # Create parallel coordinates plot
    
    # one-liner to read a single variable
    filename = 'DOE_permutations.mat'
    current_path = os.getcwd()
    filepath = os.path.join(current_path,'Input_files',filename)

    P_analysis = loadmat(filepath)['P_analysis']

    histogram = np.log10( np.reshape(histogram, (-1, 1)) / (sum(histogram)*0.01) + 1.0 ) * 50
    robustness = np.reshape(robustness, (-1, 1))
    FO = np.reshape(FO, (-1, 1))
    index = range(0,len(histogram)); index = np.reshape(index, (-1, 1))

    n_deposits = []
    for p_i in P_analysis:
        n_deposits += [np.count_nonzero(p_i != -1) - 1]
    n_deposits = np.reshape(n_deposits, (-1, 1))

    inputs = np.hstack((P_analysis,n_deposits))
    outputs = np.hstack((histogram,robustness,FO))

    variable_lbls = ['c', 'D1', 'D2', 'D3', 'D4', 'D5', 'n_deposits']
    output_lbls = ['optimality', 'robustness', 'flexibility']
    parallel_file = 'Tradespace_PCP.html'
    parallel_filepath = os.path.join(os.getcwd(),'DOE_results',parallel_file)

    parallel_plots(inputs,outputs,variable_lbls,output_lbls,parallel_filepath)

    #==========================================================================
    plt.show()
