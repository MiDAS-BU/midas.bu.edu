#!/usr/bin/env python3
# cSpell:disable


def main():

	import os
	import shutil
	import yaml
	import contextlib
	import sys
	import markdown
	from pathlib import Path
	from jinja2 import Template, Environment, FileSystemLoader
	from markupsafe import Markup
	from datetime import datetime
	from string import digits
	import requests
	import json


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

	def generatePublications(file, *names):
		# parse JSON list / object from DBLP into a string
		def authorsToString(publicationJson):
			result = ""
			authors = publicationJson["authors"]["author"]
			
			if isinstance(authors, dict):
				return authors["text"]
				print("THIS SHOULD BE SUPER RARE!")
			else:
				for author in authors:
					cur_author=author['text'].rstrip(digits)
					cur_author=cur_author.strip()
					# print("["+cur_author+"]")
					result += f"{cur_author}, "
				return result[:-2]

		# load from file first
		result = loadData(file)
		print("Collecting publications:", end = "")

		for name in names:

			# load from DBLP search API
			response = requests.get(f"https://dblp.org/search/publ/api?q=author%3A{name}%3A&format=json")
			publications = json.loads(response.text)["result"]["hits"]["hit"]
			print(f"\n\t{name}: ", end = "")

			for publication in publications:

				# Do not include archives
				publication = publication["info"]
				if publication["venue"] == "CoRR" or publication["venue"] == "IACR Cryptol. ePrint Arch.":
					continue

				# Do not include duplicates
				if len(list(filter(lambda p: p["title"] == publication["title"][:-1], result["publications"]))) > 0:
					print("d", end = "")
					continue

				# Parse to our format, add to list, template will aoutomaticaaly select latest
				result["publications"] += [{
					"title": publication["title"][:-1], # remove period
					"authors": authorsToString(publication),
					"venue": publication["venue"],
					"date": {
						"year": int(publication["year"])
					},
					"links": {
						"abstract": publication["ee"]
					}
				}]
				print(".", end = "")
		print()
		return result

	# filters

	def sortByLastName(input):
		def sortFunc(person):
			names = person["name"].split()
			return names[len(names) - 1]
		return sorted(input, key = sortFunc)

	def sortByDate(input):
		def sortFunc(obj):
			return datetime.timestamp(datetime.strptime(obj["when"], "%m/%d/%y"))
		return sorted(input, key = sortFunc)

	dist = "./dist"
	src = "./website"

	md = markdown.Markdown()
	templates = Environment(loader=FileSystemLoader(searchpath=str(Path(src) / "templates")))
	templates.filters['sortByLastName'] = sortByLastName
	templates.filters['sortByDate'] = sortByDate
	templates.filters['formatDate'] = lambda input: datetime.strptime(input, "%m/%d/%y").strftime('%A, %b %d')
	templates.filters['limit'] = lambda input, n: input[:n]
	templates.filters['markdown'] = lambda input, style: f"<div class=\"markdown\" style=\"{style}\"> {Markup(md.convert(input))} </div>"

	# create dist structure
	recreateDir(dist, ignore_errors=True)

	shutil.copytree(Path(src) / "assets", Path(dist) / "assets")
	shutil.copy(Path(src) / "CNAME", Path(dist) / "CNAME")
	(Path(dist) / "assets" / "unminified").mkdir(parents=True, exist_ok=True)

	generateClasses(templates)

	# do not regenerate for each page
	publications = generatePublications("publications", "George_Kollios", "Manos_Athanassoulis", "Evimaria_Terzi", "Charalampos_E._Tsourakakis")

	# render templates
	for path in (Path(src) / "templates").glob('*.html'):
		if not any(page in str(path) for page in ["layout", "class"]):
			templates.get_template(path.name).stream(
				seminars=loadData("seminars"),
				people=loadData("people"),
				publications=publications,
				exam=loadData("depth-exam")
			).dump(str(Path(dist) / path.name))

if __name__ == '__main__':
	main()
