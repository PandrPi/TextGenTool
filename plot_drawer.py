import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import helper


# !!! IMPORTANT !!!
# atan(m) - angle of slope in radians, where m - slope


def basic_plot_draw(x: np.array, y: np.array, x_label: str, y_label: str, scatter_label: str, plot_title: str):
    """
    Draws the data inside the plot
    :param x: X data array
    :param y: Y data array
    :param x_label: Label for x axis
    :param y_label: Label for y axis
    :param scatter_label: label of scatter plot inside the Legends
    :param plot_title: Plot title
    """
    rank = np.log10(x)
    m, c = np.polyfit(rank, np.log10(y), 1)
    y_fit = np.power(10, m * rank + c)

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()
    ax.scatter(x, y, marker='s', s=10, label=scatter_label)
    ax.plot(x, y_fit, c='orange', label=f"{round(m, 2)} * x + {round(c, 2)}")
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    fig.canvas.mpl_connect('resize_event', lambda event: (fig.tight_layout(), fig.canvas.draw()))
    fig.canvas.manager.set_window_title('Plot window')

    ax.legend(shadow=True, fancybox=True)
    fig.tight_layout()
    plt.title(plot_title)
    plt.show()


def draw_zipf_law(word_frequencies: dict, label: str = "ρ ν"):
    """
    Calculates and draws the correlation of word's rank to a word occurrence frequency (Zipf's law)
    :param word_frequencies: A dictionary that contains data about word occurrence frequencies
    :param label: The label of resulting plot in Legends
    """
    x = np.array(range(1, len(word_frequencies) + 1))
    y = np.array([*word_frequencies.values()])

    basic_plot_draw(x, y, 'Rank', 'Frequency', label, "Zipf's law")


def draw_heaps_law(word_list: list, desired_points_number: int = 1000, label: str = "ρ ν"):
    """
    Calculates and draws the correlation of total words number to a number of unique words (Heaps' law)
    :param word_list: The list of words to process
    :param desired_points_number: The number of points in the resulting plot
    :param label: The label of resulting plot in Legends
    """
    window_position = 0

    total_world_numbers = []
    dictionary_sizes = []
    word_set = set()
    increment_size: int = len(word_list) // desired_points_number
    window_size: int = increment_size

    while window_size < len(word_list):
        word_set |= set(word_list[window_position:window_size])

        total_world_numbers.append(window_size)
        dictionary_sizes.append(len(word_set))

        window_size += increment_size
        window_position += increment_size

    x = np.array(total_world_numbers)
    y = np.array(dictionary_sizes)

    basic_plot_draw(x, y, 'Total number of words', 'Number of unique words', label, "Heaps' law")
