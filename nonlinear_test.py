import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

# x_data = np.array([
#     71.138, 244.29729, 349.70953, 431.4371, 500.0021, 560.084, 614.22815, 663.7636, 709.3182, 752.1256, 792.2629,
#     830.2825, 866.0309, 900.13336, 933.0144, 964.46924, 994.8197, 1023.2174, 1052.7523, 1079.5145, 1105.6735,
#     1130.7849, 1155.9775, 1179.4, 1203.5927, 1226.8718, 1248.44, 1269.625, 1292.4286, 1313.4478, 1333.4154, 1352.4603,
#     1371.8853, 1391.4576, 1413.4656, 1429.875, 1447.9814, 1465.7358, 1483.8628, 1500.16, 1518.4897, 1534.3334,
#     1552.1702, 1565.8223, 1582.25, 1596.6046, 1613.3334, 1628.3096, 1644.6097, 1659.225, 1673.4359, 1686.5264, 1702.5,
#     1716.6757, 1730.0278, 1743.0571, 1757.1143, 1771.1177, 1784.6471, 1796.2122, 1807.3125, 1821.75, 1832.6129,
#     1846.8387, 1857.9333, 1873.1, 1882.5172, 1896.3103, 1910.3793, 1918.1072, 1931.75, 1942., 1953.2593, 1966.3704,
#     1976.4615, 1986.5, 1999.8462, 2008.24, 2019.72, 2030.0, 2039.2916, 2049.875, 2061.0417, 2066.1738, 2079.2173,
#     2091.5652, 2107.9565, 2110.8635, 2119.1365, 2132.8635, 2136., 2150.0476, 2158.8096, 2169.762, 2182.1904, 2184.75,
#     2197.5, 2208.25, 2218.05, 2229.3])
#
# y_data = np.array([
#     4.2071075, 10.871503, 15.700845, 19.982838, 24.854362, 27.80242, 32.25932, 35.96926, 39.866123, 44.01076, 46.931053,
#     51.25696, 55.140606, 58.702488, 61.113293, 65.117905, 68.66276, 71.3804, 74.75307, 77.59679, 80.52035, 83.91699,
#     86.75006, 89.16108, 92.98994, 96.424194, 98.99, 101.97417, 104.23416, 106.94542, 110.55996, 111.28953, 114.85345,
#     117.166016, 120.518166, 122.210884, 125.15021, 127.27213, 130.5845, 133.47424, 136.40114, 138.0254, 139.36136,
#     142.79547, 146.08157, 148.84503, 150.99884, 152.80637, 154.20099, 156.23212, 159.61072, 162.37656, 163.55263,
#     165.74255, 168.47543, 171.81483, 172.28809, 174.19238, 174.8971, 179.6579, 182.44029, 183.06096, 185.71739,
#     187.63383, 190.73035, 191.9485, 194.93547, 195.9592, 197.12701, 200.64241, 201.60951, 206.49509, 207.92209,
#     208.37772, 213.59149, 214.53873, 216.9558, 221.94743, 222.98494, 223.01193, 228.26437, 226.67401, 227.55649,
#     230.58464, 232.48636, 233.47095, 234.86934, 237.09114, 237.0992, 238.41586, 243.28409, 247.03722, 244.96251,
#     244.00916, 246.03593, 251.43822, 252.23927, 252.15526, 252.76006, 253.76566])

x_data = np.array([
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    77,
    78,
    79,
    80,
    81,
    82,
    83,
    84,
    85,
    86,
    87,
    88,
    89,
    90,
    91,
    92,
    93,
    94,
    95,
    96,
    97,
    98,
    99,
    100,
])

y_data = np.array([
    0.99,
    1.43,
    1.71,
    2.01,
    2.25,
    2.45,
    2.62,
    2.84,
    2.99,
    3.18,
    3.3,
    3.43,
    3.61,
    3.7,
    3.9,
    4.02,
    4.12,
    4.26,
    4.33,
    4.5,
    4.59,
    4.7,
    4.77,
    4.9,
    5.01,
    5.1,
    5.18,
    5.3,
    5.4,
    5.5,
    5.6,
    5.68,
    5.75,
    5.8,
    5.9,
    5.96,
    6.1,
    6.15,
    6.25,
    6.32,
    6.41,
    6.5,
    6.6,
    6.62,
    6.7,
    6.8,
    6.88,
    6.9,
    7.02,
    7.07,
    7.12,
    7.2,
    7.29,
    7.33,
    7.4,
    7.5,
    7.55,
    7.6,
    7.65,
    7.7,
    7.8,
    7.88,
    7.93,
    7.98,
    8.09,
    8.1,
    8.2,
    8.2,
    8.31,
    8.4,
    8.4,
    8.5,
    8.54,
    8.6,
    8.65,
    8.7,
    8.8,
    8.8,
    8.89,
    8.95,
    9.03,
    9.07,
    9.1,
    9.2,
    9.2,
    9.27,
    9.3,
    9.4,
    9.4,
    9.5,
    9.54,
    9.6,
    9.64,
    9.7,
    9.7,
    9.8,
    9.8,
    9.9,
    9.95,
    9.97,
])


def func(x, a, b):
    return a + x ** b


lin_reg_1 = stats.linregress(x_data, y_data)
lin_reg_2 = stats.linregress(np.log10(x_data), np.log10(y_data))
nonlin_reg_1, pcov1 = curve_fit(func, x_data, y_data, p0=(0.0, 1.0), method='lm')
nonlin_reg_2, pcov2 = curve_fit(func, np.log10(x_data), np.log10(y_data), p0=(0.0, 1.0), method='lm')

residuals = y_data - func(x_data, *nonlin_reg_1)
ss_res = np.sum(residuals**2)
ss_tot = np.sum((y_data - np.mean(y_data))**2)
r_squared = 1 - (ss_res / ss_tot)

x = np.linspace(x_data.min(), x_data.max(), num=100)
y = func(x, nonlin_reg_1[0], nonlin_reg_1[1])

# Plot the original signal and overlay the noisy signal to show the scale of the noise
plt.plot(x_data, y_data, 'b')
plt.plot(x, y, 'r')
plt.xlabel('x')
plt.ylabel('y (blue) and yNoise (red)')
plt.show()

#
#
# # function for genetic algorithm to minimize (sum of squared error)
# def sum_of_squared_error(parameter_tuple):
#     warnings.filterwarnings("ignore")  # do not print warnings by genetic algorithm
#     val = func(x_data, *parameter_tuple)
#     return numpy.sum((y_data - val) ** 2.0)
#
#
# def generate_initial_parameters():
#     # min and max used for bounds
#     max_x = max(x_data)
#     min_x = min(x_data)
#     max_y = max(y_data)
#     min_y = min(y_data)
#
#     parameter_bounds = [[min_x, max_x], [min_x, max_x], [min_y, max_y]]
#
#     # "seed" the numpy random number generator for repeatable results
#     result = differential_evolution(sum_of_squared_error, parameter_bounds, seed=3)
#     return result.x
#
#
# # generate initial parameter values
# geneticParameters = generate_initial_parameters()
#
# # curve fit the test data
# fittedParameters, pcov = curve_fit(func, x_data, y_data, geneticParameters)
#
# print('Parameters', fittedParameters)
#
# modelPredictions = func(x_data, *fittedParameters)
#
# absError = modelPredictions - y_data
#
# SE = numpy.square(absError)  # squared errors
# MSE = numpy.mean(SE)  # mean squared errors
# RMSE = numpy.sqrt(MSE)  # Root Mean Squared Error, RMSE
# Rsquared = 1.0 - (numpy.var(absError) / numpy.var(y_data))
# print('RMSE:', RMSE)
# print('R-squared:', Rsquared)
#
#
# ##########################################################
# # graphics output section
# def model_and_scatter_plot(graph_width, graph_height):
#     f = plt.figure(figsize=(graph_width / 100.0, graph_height / 100.0), dpi=100)
#     axes = f.add_subplot(111)
#
#     # first the raw data as a scatter plot
#     axes.plot(x_data, y_data, 'D')
#
#     # create data for the fitted equation plot
#     x_model = numpy.linspace(min(x_data), max(x_data))
#     # x_model = numpy.linspace(-10000, 10000)
#     y_model = func(x_model, *fittedParameters)
#
#     # now the model as a line plot
#     axes.plot(x_model, y_model)
#
#     axes.set_xlabel('X Data')  # X axis data label
#     axes.set_ylabel('Y Data')  # Y axis data label
#
#     plt.show()
#     plt.close('all')  # clean up after using pyplot
#
#
# model_and_scatter_plot(800, 600)
