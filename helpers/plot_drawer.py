import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from scipy import stats
from scipy.optimize import curve_fit

# !!! IMPORTANT !!!
# atan(m) - angle of slope in radians, where m - slope
from helpers import helper


def nonlin_curve_func(values, a, b):
    return a * values ** b


def get_nonlinear_fit_quality(x, y, popt) -> float:
    residuals = y - nonlin_curve_func(x, *popt)
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return 1.0 - (ss_res / ss_tot)


def draw_regression_curves(ax, x, y):
    regression, pcov1 = curve_fit(nonlin_curve_func, x, y, p0=(0.5, 1.0), method='lm')
    a, b = regression
    fit_quality = round(get_nonlinear_fit_quality(x, y, regression) * 100, 2)
    ax.plot(x, nonlin_curve_func(x, a, b), c='#ff9113',
            label="y=$\mathregular{{{0}*x^{{{1}}}}}$, R={2}%".format(round(a, 2), round(b, 2), fit_quality))

    x_log = np.log10(x)
    regression = stats.linregress(x_log, np.log10(y))
    a, b = regression.slope, regression.intercept
    fit_quality = round(regression.rvalue * 100, 2)
    ax.plot(x, np.power(10, a * x_log + b), c='#57b812',
            label="y={0}*x+{1}, R={2}%".format(round(a, 2), round(b, 2), fit_quality))


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

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()

    draw_regression_curves(ax, x, y)

    ax.scatter(x, y, marker='s', s=14, label=scatter_label)
    ax.tick_params(labelbottom=True, labeltop=True, labelleft=True, labelright=True,
                   bottom=True, top=True, left=True, right=True, which='both')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    fig.canvas.mpl_connect('resize_event', lambda event: (fig.tight_layout(), fig.canvas.draw()))
    fig.canvas.manager.set_window_title('Plot window')

    ax.legend(prop={'size': 11})
    fig.tight_layout()
    plt.title(plot_title)
    plt.show()


def get_plot_label_from_parameters(params: dict) -> str:
    label = ''
    for k, v in params.items():
        label += f"{k}={v} "
    return label[:-1]


def draw_zipf_law(word_frequencies: dict, model_parameters: dict):
    """
    Calculates and draws the correlation of word's rank to a word occurrence frequency (Zipf's law)

    :param word_frequencies: A dictionary that contains data about word occurrence frequencies
    :param model_parameters: The parameters of models that are the result of GenModel.get_params_for_plot method
    """
    x = np.array(range(1, len(word_frequencies) + 1))
    y = np.array([*word_frequencies.values()])
    label = get_plot_label_from_parameters(model_parameters)  # the label of resulting plot in Legends

    basic_plot_draw(x, y, 'Rank', 'Frequency', label, "Zipf's law")


def draw_heaps_law(word_list: list, model_parameters: dict, desired_points_number: int = 10000):
    """
    Calculates and draws the correlation of total words number to a number of unique words (Heaps' law)

    :param word_list: The list of words to process
    :param desired_points_number: The number of points in the resulting plot
    :param model_parameters: The parameters of models that are the result of GenModel.get_params_for_plot method
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
    label = get_plot_label_from_parameters(model_parameters)  # the label of resulting plot in Legends

    basic_plot_draw(x, y, 'Total number of words', 'Number of unique words', label, "Heaps' law")


def draw_taylor_law(word_list: list, model_parameters: dict, desired_points_number: int = 150):
    """
    Calculates and draws the correlation of average unique words number to a mean square deviation of this number
    (Taylor's law)

    :param word_list: The list of words to process
    :param desired_points_number: The number of points in the resulting plot
    :param model_parameters: The parameters of models that are the result of GenModel.get_params_for_plot method
    """
    text_size = len(word_list)

    word_array = np.asarray(word_list)
    dictionary_sizes, std_values, window_sizes = helper.do_taylor(word_array, text_size, desired_points_number)

    # return None

    x = dictionary_sizes
    y = std_values
    label = get_plot_label_from_parameters(model_parameters)  # the label of resulting plot in Legends

    basic_plot_draw(x, y, 'D', 'σ(D)', label, "Taylor's law")
