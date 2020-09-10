import click
import csv
import re


def clean_data(line):
	""""""
	pattern = r'([\[\(][^\]\)]{0,}[\]\)])'
	line = re.sub(pattern, '', line)
	lines = line.strip().split(' - ')
	return lines 


def convert_to_csv(text_file, csv_file):
	""""""
	with open(text_file, 'r') as tf, open(csv_file, "w", newline='') as cf:
		data = tf.readlines()
		writer = csv.writer(cf, delimiter=',')
		for line in data:
			writer.writerow(clean_data(line))


@click.command()
@click.argument('txtfile')
@click.argument('csvfile')
def convert(txtfile, csvfile):
	"""TXTFILE - $$$$$$$$$$   CSVFILE - $$$$$$$$$$"""

	convert_to_csv(txtfile, csvfile)


if __name__ == '__main__':
	convert()
