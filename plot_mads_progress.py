# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 05:20:27 2020

@author: Khalil
"""

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rcParams
import random
from itertools import permutations 
import math
import random
from random import randrange
from simanneal import Annealer
import csv

class PlotOptimizationProgress():

    """Test annealer with a travelling salesman problem.
    """

    # pass extra data (the distance matrix) into the constructor
    def __init__(self, state, P_analysis_strip, dictionary, opt_bb_calls, attribute, fig):
        self.P_analysis_strip = P_analysis_strip
        self.dictionary = dictionary
        self.opt_bb_calls = opt_bb_calls
        self.fig = fig
        self.attribute = attribute
        self.n_fcalls = 0
        self.state = []
        self.line = []
        
#        super(PlotOptimizationProgress, self).__init__(state)  # important!

    def move(self):
        """Get the branch components"""
        self.state = self.opt_bb_calls[self.n_fcalls];
        self.energy()
        
    def energy(self):
        """Calculates the length of the route."""
        ind = self.P_analysis_strip.index(self.state)
        x_data = self.dictionary['weight'][ind]
        y_data = self.dictionary['n_f_th'][ind]
        
        e = -y_data;
        self.n_fcalls += 1;
        #print('Number of function calls: %i' %(self.n_fcalls))
        #=====================================================================#
        # Plot progress
        # generate random color for branch
        r = random.random()
        g = random.random()
        b = random.random()
        rgb = [r,g,b]
                
        x_data = []
        y_data = []
        
        for it in range(len(self.state[1::])):
            ind = self.P_analysis_strip.index(self.state[0:it+2])
            x_data += [dictionary['weight'][ind]]
            y_data += [dictionary[attribute[0]][ind]]
        
        ax = self.fig.gca()
        if len(self.line) > 0:
            self.line[0].remove()
        
        self.line = ax.plot(x_data, y_data, 's-', color = 'm', linewidth = 3.0, markersize = 7.5 );
        current_path = os.getcwd()
        fig.savefig(os.path.join(current_path,'progress','tradespace_%i.png' %(self.n_fcalls)), 
                    format='png', dpi=100,bbox_inches='tight')
        
        plt.pause(0.0005)
        plt.show()
        #=====================================================================#
        return e

# %% Import raw data and stip permutation indices = -1
from scipy.io import loadmat
from plot_tradespace import plot_tradespace

# one-liner to read a single variable
P_analysis = loadmat('DOE_permutations.mat')['P_analysis']
#P_analysis = P_analysis[0:44]

attribute = ['n_f_th','Safety factor ($n_{safety}$)']
#attribute = ['resiliance_th','Requirement satisfaction ratio ($V_{{C}\cap{R}}/V_{R}$)']

P_analysis_strip = []
for item in P_analysis:
    # Get permutation index
    permutation_index = []
    for arg in item:
        if not int(arg) == -1:
            permutation_index += [int(arg)] # populate permutation index
    P_analysis_strip += [permutation_index]

[fig, ax, dictionary, start, wave, cross] = plot_tradespace(attribute);

# %% Begin combinatorial optimization

# read MADS log file
bb_evals = [];
with open('mads_bb_calls.log') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        
        row_strip = [];
        for item in row:
            if int(item) != -1:
                row_strip += [int(item)];
                
        bb_evals += [row_strip]
        line_count += 1


# iterate through MADS bb evals
current_path = os.getcwd()
optproblem = PlotOptimizationProgress(bb_evals[0],P_analysis_strip, dictionary, bb_evals, attribute, fig);

for bb_call in bb_evals:
    optproblem.move()

print('\nNumber of function calls: %i' %(optproblem.n_fcalls))

# read MADS log file
opt_points = [];
with open('mads_x_opt.log') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=' ')
    line_count = 0
    for row in csv_reader:
        row = [int(item) for item in row]
        row_strip = row[1::]
                
        opt_points += [row_strip]
        line_count += 1

x_data = []; y_data = [];
for it in range(len(opt_points[0][1::])):
    ind = P_analysis_strip.index(opt_points[0][0:it+2])
    x_data += [dictionary['weight'][ind]]
    y_data += [dictionary[attribute[0]][ind]]

optproblem.line[0].remove()
ax.plot(x_data, y_data, '-', color = 'r', linewidth = 4.0 );
fig.savefig(os.path.join(current_path,'progress','tradespace_%i.png' %(optproblem.n_fcalls)), format='png', dpi=100,bbox_inches='tight')