# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 18:06:53 2020

@author: Khalil
"""

#==============================================================================
# Acquire requirements DOE design results and 
# get dictionary data from design log and resiliance log
def plot_stagespace(attribute,ds_s,req_vec,req_thresh,MADS_output_dir,plot_id):
    
    from sample_requirements import NOMAD_call
    
    import numpy as np
    import random
    import copy
    import os
        
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib import rcParams

    plt.close('all')
    
    #==========================================================================
    # read weight data
    current_path = os.getcwd()
 
    attribute_label = attribute[0]
    
    # This is not necessary if `text.usetex : True` is already set in `matplotlibrc`.    
    mpl.rc('text', usetex = True)
    rcParams['font.family'] = 'serif'
    my_dpi = 100
    fig1 = plt.figure(figsize=(700/my_dpi, 500/my_dpi), dpi=my_dpi)
    ax1 = fig1.gca() 

    fig2 = plt.figure(figsize=(700/my_dpi, 500/my_dpi), dpi=my_dpi)
    ax2 = fig2.gca() 
    # generate random color for branch
    colors = [[1,0,0],
              [0,1,0],
              [0,0,1]]

    branch_id = 1; legend_h_f1 = []; legend_h_f2 = []; legend_labels = []
    # loop over data points
    for ds in ds_s:

        eval_point = ds
        call_type = 1
        [outs,weight] = NOMAD_call(call_type,req_vec,req_thresh,eval_point,MADS_output_dir)
        resiliance = [thresh - item  for thresh,item in zip(req_thresh,outs[1::])]
        
        # Get design index
        i = 0
        x_data = [0]; R_data = [0.0]; w_data = [0.0]; s_data = [] # concept
        for i in range(6):
            x_data += [i+1]
            R_data += [resiliance[i]]
            w_data += [weight[i]]

            if i < (len(ds)-2):
                s_data += [ds[i+2]]
            else:
                s_data += [-1]
        
        plot_h1, = ax1.plot(x_data, R_data, ':', color = colors[branch_id-1], linewidth = 2.5 )
        # plt.plot(x_data, y_data, 'o', markersize=10, markevery=len(x_data), color = [0,0,0])
        plot_h2, = ax1.plot(x_data, R_data, 'o', color = [0,0,0], markersize=6 )
        legend_h_f1 += [plot_h1]

        plot_h1, = ax2.plot(x_data, w_data, ':', color = colors[branch_id-1], linewidth = 2.5 )
        # plt.plot(x_data, y_data, 'o', markersize=10, markevery=len(x_data), color = [0,0,0])
        plot_h2, = ax2.plot(x_data, w_data, 'o', color = [0,0,0], markersize=6 )
        legend_h_f2 += [plot_h1]
        
        # legend label generation
        label = ''.join(['$C = %i' %(ds[1]),
                         '~S = \{', 
                         ',~'.join(map(str,s_data)),'\}$'])

        legend_labels += [label]

        branch_id += 1
    
    # Figure 2 settings
    ax2.fill_between(x_data[1::], 0.0, w_data[1::], facecolor="none", hatch="//", edgecolor=colors[branch_id-2], linewidth=0.0)
    ax2.tick_params(axis='both', which='major', labelsize=14) 
    ax2.set_xlabel('Design stage number', fontsize=14)
    ax2.set_ylabel('Weight (kg)', fontsize=14)
    ax2.set_xticks(list(range(6+1)), list(map(str,['']+list(range(1,6+1)))))
    ax2.set_xlim((-0.4,6.7))
    ax2.set_ylim((0,21))
    ax2.legend(legend_h_f2, legend_labels, loc='lower right', fontsize = 10)

    fig_file_name = '%i_stagespace_weight.pdf' %(plot_id)
    save_folder = 'DOE_results'
    save_directory = os.path.join(current_path,save_folder,fig_file_name)
    fig2.savefig(save_directory, bbox_inches='tight')

    # Figure 1 settings
    req_thresh = [0.0] + req_thresh # design stage 0
    plot_req, = ax1.plot(x_data, req_thresh, '-', color = [0,1,0], linewidth = 2.5 )
    legend_h_f1 += [plot_req]; legend_labels += ['Requirement threshold']

    # ax1.fill_between(x_data, 0.0, req_thresh, facecolor="none", hatch="XX", edgecolor="g", linewidth=0.0)
    ax1.tick_params(axis='both', which='major', labelsize=14) 
    ax1.set_xlabel('Design stage number', fontsize=14)
    ax1.set_ylabel(attribute_label, fontsize=14)
    ax1.set_xticks(list(range(6+1)), list(map(str,['']+list(range(1,6+1)))))
    ax1.set_xlim((-0.4,6.7))
    ax1.set_ylim((0.0,1.15))
    ax1.legend(legend_h_f1, legend_labels, loc='lower right', fontsize = 10)

    fig_file_name = '%i_stagespace_res.pdf' %(plot_id)
    save_folder = 'DOE_results'
    save_directory = os.path.join(current_path,save_folder,fig_file_name)
    fig1.savefig(save_directory, bbox_inches='tight')

    return fig1, fig2

#==============================================================================
# MAIN CALL
if __name__ == "__main__":
    
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    
    current_path = os.getcwd()
    MADS_output_folder = 'MADS_output'
    MADS_output_dir = os.path.join(current_path,MADS_output_folder)

    attribute = ['$P(n_{safety}(\mathbf{T}) \ge n_{th})$']

    # plot 1
    plot_id = 1
    req_thresh = [ 0.01, 0.1, 0.3, 0.3, 0.8, 0.9 ]
    ds_s = [ [5 , 1 , 2 , 1 , -1 , -1 , 0 ] ]
    req_vec = [36, 36, 36, 36, 36, 36]

    plot_stagespace(attribute,ds_s,req_vec,req_thresh,MADS_output_dir,plot_id)
    
    # plot 2
    plot_id = 2
    req_thresh = [ 0.01, 0.1, 0.3, 0.3, 0.8, 0.9 ]
    ds_s = [ [5 , 1 , 2 , 1 , -1 , -1 , 0 ] ]
    req_vec = [5, 11, 10, 48, 32, 27]

    plot_stagespace(attribute,ds_s,req_vec,req_thresh,MADS_output_dir,plot_id)
   
    # plot 3
    plot_id = 3
    req_thresh = [ 0.01, 0.1, 0.3, 0.3, 0.8, 0.9 ]
    ds_s = [ [5 , 1 , 2 , 1 , -1 , -1 , 0 ],
             [6,  1,  3, -1, -1, -1, -1, 2] ]
    req_vec = [5, 11, 10, 48, 32, 27]

    plot_stagespace(attribute,ds_s,req_vec,req_thresh,MADS_output_dir,plot_id)

    # plot 4
    plot_id = 4
    req_thresh = [ 0.01, 0.1, 0.3, 0.3, 0.8, 0.9 ]
    ds_s = [ [5 , 1 , 2 , 1 , -1 , -1 , 0 ],
             [6,  1,  3, -1, -1, -1, -1, 2],
             [6 , 1 , 1 , 2 , -1 , 0 , -1, -1 ] ]
    req_vec = [5, 11, 10, 48, 32, 27]

    plot_stagespace(attribute,ds_s,req_vec,req_thresh,MADS_output_dir,plot_id)

    plt.show()
    #===========================================================================