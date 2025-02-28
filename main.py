from datetime import datetime, timedelta
import matplotlib.pyplot as plt

import numpy
import requests
import sys

coordinates = {
	# J6ek22ru - 58°12'49.2"N 25°12'03.1"E
	"joekaaru" : (58.213667, 25.200861),
	# Kurmi - 58°12'28.4"N 25°08'17.9"E
	"kurmi" : (58.207889, 25.140305),
	# Laane - 58°13'42.3"N 25°13'35.0"E
	"laane" : (58.228417, 25.226389),
	# Neitsi - 58°09'22.5"N 25°08'29.1"E
	"neitsi" : (58.15625, 25.141416)
}

location = "joekaaru"
if len(sys.argv) > 1:
	location = sys.argv[1]

# Set location coordinates
latitude, longitude = coordinates[location]

# Calculate dates for past year
end_date = datetime.now() - timedelta(days=2)
start_date = end_date - timedelta(days=365)

start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

wind_height = "100m"
if len(sys.argv) > 2:
	wind_height = sys.argv[2]

def fetch_history(type, variable):
	url = "https://archive-api.open-meteo.com/v1/archive"
	params = {
		"latitude": latitude,
		"longitude": longitude,
		"start_date" : start_date_str,
		"end_date" : end_date_str
	}
	params[type] = variable

	response = requests.get(url, params = params)
	data = response.json()

	return data[type][variable]

def wind_direction():
	type = "hourly"
	variable = "winddirection_{wind_height}".format(wind_height = wind_height)
	label = "Hourly Wind Direction at {wind_height} (degrees)".format(wind_height = wind_height)

	values = fetch_history(type, variable)

	plt = wind_direction_plot(values, label)
	plt.savefig("plots/{location}_{type}_{variable}.png".format(location = location, type = type, variable = variable))
	plt.show()

def wind_direction_plot(values, label):
	fig = plt.figure(figsize=(12, 12))
	ax = fig.add_subplot(111, projection='polar')

	# Convert degrees to radians and adjust for meteorological convention
	theta = numpy.radians(values)
	theta = theta % (2 * numpy.pi)  # Ensure values stay within 0-2π

	# Create bins for directions (16 cardinal directions)
	bins = numpy.linspace(0, 2*numpy.pi, 17)

	# Calculate histogram
	hist, _ = numpy.histogram(theta, bins=bins)

	# Plot bars
	width = 2*numpy.pi/16  # Width of each bar
	bars = ax.bar(bins[:-1], hist, width=width, color='#4682B4', alpha=0.7, edgecolor='black')

	# Customize the plot
	ax.set_theta_zero_location('N')  # Put 0° (North) at top
	ax.set_theta_direction(-1)       # Clockwise direction
	ax.set_xticks(numpy.linspace(0, 2*numpy.pi, 8, endpoint=False))
	ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

	# Add title
	plt.title(label, pad=20, fontsize=18)

	# Add grid
	ax.yaxis.grid(True)

	plt.tight_layout()

	return plt

def wind_speed():
	type = "hourly"
	variable = "wind_speed_{wind_height}".format(wind_height = wind_height)
	label = "Hourly Wind Speed at {wind_height} (m/s)".format(wind_height = wind_height)

	values = fetch_history(type, variable)

	plt = wind_speed_plot(values, label)
	plt.savefig("plots/{location}_{type}_{variable}.png".format(location = location, type = type, variable = variable))
	plt.show()

def wind_speed_plot(values, label):
	quantiles = numpy.quantile(values, [0.05, 0.20, 0.50, 0.80, 0.95]).tolist()
	print("Quantiles: {}".format(quantiles))

	# Create histogram
	plt.figure(figsize=(12, 8))
	plt.hist(values, bins=30, edgecolor='black')

	for quantile in quantiles:
		if quantile in (quantiles[0], quantiles[-1]):
			color = "red"
			linestyle = "-"
		else:
			color = "black"
			linestyle = "--"
		plt.axvline(x=quantile, color=color, linestyle=linestyle)

	plt.title(f'{label} Distribution ({start_date_str} to {end_date_str})'.format(label = label), fontsize=18)
	plt.xlabel('{label}'.format(label = label), fontsize=16)
	plt.ylabel('Frequency', fontsize=16)
	plt.grid(True, alpha=0.3)

	plt.tight_layout()

	return plt

wind_direction()
wind_speed()
