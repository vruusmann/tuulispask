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

def wind_rose():
	label = "Hourly Wind Direction at {wind_height} (degrees)".format(wind_height = wind_height)
	type = "hourly"
	variable = "winddirection_{wind_height}".format(wind_height = wind_height)

	values = fetch_history(type, variable)

	# Define direction bins (16 cardinal directions)
	bins = numpy.linspace(0, 360, 17)
	directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

	# Calculate frequency of wind directions
	hist, _ = numpy.histogram(values, bins=bins)
	hist = hist / hist.sum()  # Normalize to percentages

	# Create figure
	fig = plt.figure(figsize=(12, 12))
	ax = fig.add_subplot(111, polar=True)

	# Convert to radians and set North at top
	theta = numpy.radians(numpy.linspace(0, 360, 16))
	ax.set_theta_zero_location('N')
	ax.set_theta_direction(-1)

	# Plot bars
	width = 2 * numpy.pi / 16
	bars = ax.bar(theta, hist, width=width, bottom=0.0, color='skyblue', edgecolor='black')

	# Customize plot
	ax.set_title(label, va='bottom', pad=20)

	# Set direction labels
	ax.set_xticks(theta)
	ax.set_xticklabels(directions)

	# Add percentage labels
	for bar, h in zip(bars, hist):
		height = bar.get_height()
		ax.text(bar.get_x() + bar.get_width()/2., height, f'{h*100:.1f}%', ha='center', va='bottom')

	# Add grid
	ax.yaxis.grid(True)
	ax.set_rlabel_position(270)

	plt.tight_layout()

	plt.savefig("plots/{location}_{type}_{variable}.png".format(location = location, type = type, variable = variable))

	plt.show()

def wind_speed_histogram():
	label = "Hourly Wind Speed at {wind_height} (m/s)".format(wind_height = wind_height)
	type = "hourly"
	variable = "wind_speed_{wind_height}".format(wind_height = wind_height)

	values = fetch_history(type, variable)

	print("Number of values: {}".format(len(values)))

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

	plt.savefig("plots/{location}_{type}_{variable}.png".format(location = location, type = type, variable = variable))

	plt.show()

wind_rose()
wind_speed_histogram()