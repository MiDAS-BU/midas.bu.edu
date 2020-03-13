#!/usr/bin/env python3
# cSpell:disable


def main():

	import os
	import shutil
	import yaml
	import contextlib
	import sys
	from pathlib import Path
	from jinja2 import Template, Environment, FileSystemLoader
	from datetime import datetime

	abspath = os.path.abspath(__file__)
	dname = os.path.dirname(abspath)
	os.chdir(f"{dname}/..")

	class DummyFile(object):
		def write(self, x): pass

	# silence stdout
	@contextlib.contextmanager
	def nostdout():
		save_stdout = sys.stdout
		sys.stdout = DummyFile()
		yield
		sys.stdout = save_stdout

	def recreateDir(path, ignore_errors=False):
		shutil.rmtree(path, ignore_errors=ignore_errors)
		Path(path).mkdir(parents=True, exist_ok=True)

	def loadData(file):
		with open(Path(src) / "assets" / "config" / f"{file}.yml") as dataFile:
			data = yaml.load(dataFile, Loader=yaml.FullLoader)
			return data

	def generateClasses(templates):
		classes = loadData("classes")
		for _class in classes:
			(Path(dist) / "classes" / _class["code"]).mkdir(parents=True, exist_ok=True)
			templates.get_template("class.html").stream(_class=_class).dump(
				str(Path(dist) / "classes" / _class["code"] / "index.html" )
			)

	# filters
	def formatDate(input):
		date = datetime.strptime(input, "%m/%d/%y")
		return date.strftime('%A, %b %d')

	def sortByLastName(input):
		def sortFunc(person):
			names = person["name"].split()
			return names[len(names) - 1]
		return sorted(input, key = sortFunc)

	def sortByDate(input):
		def sortFunc(obj):
			return datetime.timestamp(datetime.strptime(obj["when"], "%m/%d/%y"))
		return sorted(input, key = sortFunc)

	def limit(input, n):
		return input[:n]

	dist = "./dist"
	src = "./website"

	templates = Environment(loader=FileSystemLoader(searchpath=str(Path(src) / "templates")))
	templates.filters['formatDate'] = formatDate
	templates.filters['sortByLastName'] = sortByLastName
	templates.filters['sortByDate'] = sortByDate
	templates.filters['limit'] = limit

	# create dist structure
	recreateDir(dist, ignore_errors=True)

	shutil.copytree(Path(src) / "assets", Path(dist) / "assets")
	(Path(dist) / "assets" / "unminified").mkdir(parents=True, exist_ok=True)

	generateClasses(templates)

	# render templates
	for path in (Path(src) / "templates").glob('*.html'):
		if not any(page in str(path) for page in ["layout", "class"]):
			templates.get_template(path.name).stream(
				seminars=loadData("seminars"),
				people=loadData("people"),
				publications=loadData("publications")
			).dump(str(Path(dist) / path.name))

if __name__ == '__main__':
	main()
