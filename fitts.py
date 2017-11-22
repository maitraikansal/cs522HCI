from tkinter import *
from tkinter.ttk import *
import random
import time
import math
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from scipy import polyfit, polyval

# -*- coding: utf-16 -*-

# ------Experiment Settings---------------
DISTANCES = [64, 128, 256, 512]
WIDTHS = [8, 16, 24, 32]
USER_NAME = "Maitrai"
REPETITIONS = 2
dwt_data = []




class Pair(object):
    """To store the information."""

    def __init__(self, distances, widths, repetitions, canvas, canvas_width):

        self.distances = distances
        self.widths = widths
        self.used_combinations = []
        self.repetitions = repetitions
        self.canvas = canvas
        self.canvas_width = canvas_width
        self.is_right = True
        self.current_count = 0
        self.distance, self.width = self.generate_width_and_distance()
        self.current_time = time.time()

    def draw_rectangles(self):
        """Draws the two rectangles of the correct width and distance."""
        self.canvas.delete("all")

        left_top = (((self.canvas_width/2) - (self.distance/2) -
                     (self.width/2)), 0)
        right_top = (((self.canvas_width/2) + (self.distance/2) -
                      (self.width/2)), 0)
        left_bottom = (((self.canvas_width/2) - (self.distance/2) +
                        (self.width/2)), self.canvas_width)
        right_bottom = (((self.canvas_width/2) + (self.distance/2) +
                         (self.width/2)), self.canvas_width)

        self.canvas.tag_bind('green', "<ButtonPress-1>", self.click)

        if self.is_right:
            self.canvas.create_rectangle(right_top[0], right_top[1],
                    right_bottom[0], right_bottom[1], tag='green', fill='green')
            self.canvas.create_rectangle(left_top[0], left_top[1],
                    left_bottom[0], left_bottom[1], fill='red')
        else:
            self.canvas.create_rectangle(right_top[0], right_top[1],
                    right_bottom[0], right_bottom[1], fill='red')
            self.canvas.create_rectangle(left_top[0], left_top[1],
                    left_bottom[0], left_bottom[1], tag='green', fill='green')

    def generate_width_and_distance(self):
        """randomizing the click events."""
        random_distance = random.choice(self.distances)
        random_width = random.choice(self.widths)
        if (random_distance, random_width) not in self.used_combinations:
            self.used_combinations.append((random_distance, random_width))
            return random_distance, random_width
        else:
            return self.generate_width_and_distance()

    def click(self, object):
        """Called upon valid interaction."""
        self.is_right = not self.is_right #time to generate new distance & width
        if len(self.used_combinations) >= (len(self.widths) * len(self.distances)):
            self.finish()
            return

        if self.current_count >= self.repetitions:
            self.current_count = 1
            self.distance, self.width = self.generate_width_and_distance()
            self.take_time()
            self.draw_rectangles()

        else: #Carry on as usual
            self.current_count += 1
            self.take_time()
            self.draw_rectangles()

    def take_time(self):
        """Records the time taken for a valid interaction"""
        time_ = round(time.time() - self.current_time, 2)


        '''with open('distance_width_time_data.csv', 'w') as csvfile:'''
        fieldnames = ['distance', 'width','ID','current_count','time']
        id = math.log2(self.distance/self.width + 1)
        if time_ > 0.00:
            dwt_data.extend([{'distance': self.distance, 'width': self.width,'ID': id,'current_count': self.current_count,'time': time_}])
        self.current_time = time.time()

    def finish(self):
        """Finalises the test
        self.canvas.delete('all')"""
        text = Label(self.canvas, text="Yay!!! You did it :D :D")
        text.pack(side='top')
        df = pd.DataFrame.from_records(dwt_data,columns = ['distance', 'width','ID','current_count','time'])
        print(df)

        coeff = polyfit(df['ID'], df['time'], 1)
        x1 = min(df['ID'])
        x2 = max(df['ID'])
        y1 = polyval(coeff, x1)
        y2 = polyval(coeff, x2)

        # Throughput (IP) = (ID/MT)
        throughput = ([], [])
        for i in range(len(df['ID'])):
            id1 = df['ID'][i]
            t = df['time'][i]
            through = id1 * 1000 / t
            throughput[1].append(through)
            throughput[0].append(id1)

        print (throughput)
            #Plotting of the two graphs
        plt.figure(num="Samples")
        plt.xlabel("Index of Difficulty")
        plt.ylabel("Movement Time (msS)")
        plt.xlim(0, max(df['ID']) * 1.2)
        plt.ylim(0, max(df['time']) * 1.2)
        plt.plot(df['ID'], df['time'], "bo", label="Samples")
        plt.plot([x1,x2], [y1, y2], "r-")

        coeff_throughput = polyfit(throughput[1], throughput[0], 1)
        x3 = min(throughput[0])
        x4 = max(throughput[0])
        y3 = polyval(coeff_throughput, x3)
        y4 = polyval(coeff_throughput, x4)

        plt.figure(num="Throughput")
        plt.xlabel("Index of Difficulty")
        plt.ylabel("Throughput (bits/s)")
        plt.xlim(0, max(throughput[0]) * 1.2)
        plt.ylim(0, max(throughput[1]) * 1.2)
        plt.plot(throughput[0], throughput[1], "yo", label="Throughput")
        plt.plot([x3,x4], [y3,y4], "r-")

        print("Regression coefficients: A={}, B={}".format(coeff[0] / 1000, coeff[1] / 1000))
        plt.show()


#Experiment setup and initialisation
master = Tk()
c = Canvas(master, width=700, height=700)
c.pack()
c.itemconfigure('yellow', fill='yellow')
c.itemconfigure('red', fill='red')
rectangle_pair = Pair(DISTANCES, WIDTHS, REPETITIONS, c, 700)
rectangle_pair.click(object)
master.mainloop()
