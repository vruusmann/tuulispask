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

wind_height = "100m"
if len(sys.argv) > 2:
	wind_height = sys.argv[2]

def fetch_history(id, type, variable, start_date, end_date):
	url = "https://archive-api.open-meteo.com/v1/archive"
	params = {
		"latitude": latitude,
		"longitude": longitude,
		"start_date" : start_date,
		"end_date" : end_date,
		"windspeed_unit" : "ms"
	}
	params[type] = variable

	response = requests.get(url, params = params)
	print("URL: {}".format(response.url))

	with open("data/{id}.json".format(id = id), "wb") as file:
		file.write(response.content)

	data = response.json()

	return data[type][variable]

def wind_direction(id, start_date, end_date):
	type = "hourly"
	variable = "winddirection_{wind_height}".format(wind_height = wind_height)
	title = "Hourly Wind Direction at {wind_height} in degrees ({start_date} to {end_date})".format(wind_height = wind_height, start_date = start_date, end_date = end_date)

	values = fetch_history(id, type, variable, start_date, end_date)

	plt = wind_direction_plot(values, title)
	plt.savefig("plots/{id}.png".format(id = id))
	plt.show()

def wind_direction_plot(values, title):
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
	plt.title(title, pad=20, fontsize=18)

	# Add grid
	ax.yaxis.grid(True)

	plt.tight_layout()

	return plt

def wind_speed(id, start_date, end_date):
	type = "hourly"
	variable = "wind_speed_{wind_height}".format(wind_height = wind_height)
	title = "Hourly Wind Speed at {wind_height} in m/s ({start_date} to {end_date})".format(wind_height = wind_height, start_date = start_date, end_date = end_date)

	values = fetch_history(id, type, variable, start_date, end_date)

	plt = wind_speed_plot(values, title)
	plt.savefig("plots/{id}.png".format(id = id))
	plt.show()

def wind_speed_plot(values, title):
	quantiles = None

	if len(values) > 100:
		quantiles = numpy.quantile(values, [0.05, 0.20, 0.50, 0.80, 0.95]).tolist()
		print("Quantiles: {}".format(quantiles))

	# Create histogram
	plt.figure(figsize=(12, 8))
	plt.hist(values, bins=30, edgecolor='black')

	if quantiles:
		for quantile in quantiles:
			if quantile in (quantiles[0], quantiles[-1]):
				color = "red"
				linestyle = "-"
			else:
				color = "black"
				linestyle = "--"
			plt.axvline(x=quantile, color=color, linestyle=linestyle)

	plt.title(title, fontsize=18)
	plt.xlabel('Wind Speed (m/s)', fontsize=16)
	plt.ylabel('Frequency', fontsize=16)
	plt.grid(True, alpha=0.3)

	plt.tight_layout()

	return plt

# Calculate dates for past year
end_date = datetime.now() - timedelta(days=2)
start_date = end_date - timedelta(days=365)

start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

wind_direction("{location}_wind_direction_past_year".format(location = location), start_date_str, end_date_str)
wind_speed("{location}_wind_speed_past_year".format(location = location), start_date_str, end_date_str)