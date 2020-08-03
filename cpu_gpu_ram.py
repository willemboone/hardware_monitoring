#!/usr/bin/env python
"""Script to monitor the main component of your machine using psutil library
documentation URL: https://psutil.readthedocs.io/en/latest/
"""
import psutil
import datetime as dt
import csv
import os
import time
import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

__author__ = "Willem Boone"
__email__ = "willem.boone@outlook.com"

GIGA = 10**9
DIRECTORY = "D:/monitoring"


class Monitor(object):
    """offers functions to monitor main components of you machine"""

    def __init__(self, directory=DIRECTORY):
        self.directory = directory
        self.start = dt.datetime.now()
        print("starting time: ", self.start)

        # file
        self.new_file()

    def new_file(self):
        """creates csv file per day to stream data to
        if the file of a particular day already exists, nothing will happen
        if it does not exist yet, a new file with the date in its name will be created"""

        self.file = self.directory + "/{}_{}_{}.csv".format(self.start.year, self.start.month, self.start.day)
        if not os.path.exists(self.file):
            with open(self.file, "w+") as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["time", "ram", "cpu_perc"])

    def measure(self, interval=5):
        """executes the hardware status measurements and streams data to csv file
        :param interval (int) interval in seconds to measure CPU"""
        now = dt.datetime.now()

        # RAM memory
        used_ram = psutil.virtual_memory().used / GIGA
        available_ram = psutil.virtual_memory().total / GIGA
        ram_perc = used_ram / available_ram

        # CPU
        cpu_perc = psutil.cpu_percent(interval=interval) / 100

        # write to csv
        with open(self.file, mode='a') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([now, round(ram_perc, 2), round(cpu_perc, 2)])

    def daily_monitor(self, interval=60):
        """runs self.measure in an infinite loop, streaming data to date specified txt file
        :param interval (int) seconds in between 2 measurements"""
        while True:
            if dt.datetime.now().date() == self.start.now().date():
                self.measure()
                time.sleep(interval)
            else:
                self.new_file()

    def visualize(self, file=None, save=True):
        if file is None:
            df = pandas.read_csv(self.file, sep=',')
        else:
            df = pandas.read_csv(file, sep=',')

        df.set_index('time', inplace=True)
        df.index = pandas.to_datetime(df.index)
        ax = df.plot(style='.-')
        plt.grid()
        ax.xaxis_date()
        ax.set_ylim([0, 1.01])

        locator = mdates.AutoDateLocator(maxticks=24)
        formatter = mdates.ConciseDateFormatter(locator)

        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        if save:
            fig = plt.gcf()
            fig.set_size_inches(20, 10)
            file = self.directory + "/{}_{}_{}.png".format(self.start.year, self.start.month, self.start.day)
            plt.savefig(file)
        else:
            plt.show()

    @staticmethod
    def status(interval=5):
        print("CPU stats")
        print("-" * 25)
        current_freq, min_freq, max_freq = psutil.cpu_freq()
        print("cpu min_freq: ", min_freq / 1000, " kHz")
        print("cpu max_freq: ", max_freq / 1000, " kHz")
        print("cpu current freq: ", current_freq / 1000, " kHz")
        print("cpu usage: ", psutil.cpu_percent(interval=interval), " %")

        print("RAM stats")
        print("-" * 25)
        print("total memory: ", psutil.virtual_memory().total/GIGA, " GB")
        print("available memory: ", psutil.virtual_memory().available/GIGA, " GB")
        print("used memory: ", psutil.virtual_memory().used/GIGA, "GB")
        print("free memory: ", psutil.virtual_memory().free/GIGA, "GB")
        print("ram usage: {:4.2f} %".format(psutil.virtual_memory().used/psutil.virtual_memory().total))


if __name__ == "__main__":
    monitor = Monitor()

    # show machine stats
    monitor.status()

    # start monitoring
    monitor.daily_monitor(interval=60)

    # to visualize
    #monitor.visualize()
    #monitor.visualize("D:/monitoring/2020_7_25.csv")
