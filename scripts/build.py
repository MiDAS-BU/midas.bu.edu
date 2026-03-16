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
	import re
	import time
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
		cache_dir = Path("./cache")
		cache_file = cache_dir / f"{file}.json"
		cache_ttl_seconds = 30 * 60
		source_file = Path(src) / "assets" / "config" / f"{file}.yml"

		def loadCachedPublications():
			if not cache_file.exists():
				return None

			try:
				with open(cache_file) as cached_file:
					cached_payload = json.load(cached_file)
			except (OSError, json.JSONDecodeError):
				return None

			generated_at = cached_payload.get("generated_at")
			cached_names = cached_payload.get("names")
			cached_data = cached_payload.get("data")
			source_mtime = source_file.stat().st_mtime

			if generated_at is None or cached_names != list(names) or cached_data is None:
				return None
			if time.time() - generated_at > cache_ttl_seconds:
				return None
			if source_mtime > generated_at:
				return None

			print("Collecting publications: using cached DBLP results.")
			return cached_data

		def saveCachedPublications(publications):
			cache_dir.mkdir(parents=True, exist_ok=True)
			with open(cache_file, "w") as cached_file:
				json.dump({
					"generated_at": time.time(),
					"names": list(names),
					"data": publications,
				}, cached_file)

		cached_publications = loadCachedPublications()
		if cached_publications is not None:
			return cached_publications

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

			# load from DBLP search API (try primary, then fallback)
			query = f"author%3A{name}%3A"
			urls = [
				f"https://dblp.org/search/publ/api?q={query}&format=json",
				f"https://dblp.uni-trier.de/search/publ/api?q={query}&format=json",
			]
			response = None
			for url in urls:
				response = requests.get(url, timeout=20)
				if response.status_code == 200:
					break
				if response.status_code == 429:
					print(f"\n\tToo many requests to DBLP server. Please wait a few minutes.")
					exit(1)
			if response is None or response.status_code != 200:
				status = response.status_code if response is not None else "no response"
				print(f"\n\tDBLP request failed with status {status}.")
				exit(1)
			publications = json.loads(response.text)["result"]["hits"]["hit"]
			print(f"\n\t{name}: ", end = "")

			for publication in publications:

				# Do not include archives
				publication = publication["info"]
				venue = publication.get("venue")
				if not venue or venue == "CoRR" or venue == "IACR Cryptol. ePrint Arch.":
					continue		

				# Do not include specific entries (e.g., frontmatters, etc.)
				if publication["key"] == "conf/sigmod/2024ari" or publication["key"] == "journals/tist/LauwNTT25" or publication["key"] == "journals/pvldb/Koutrika023f" or publication["key"] == "journals/sigweb/LauwCSTTT23" or publication["key"] == "conf/wsdm/2023" or publication["key"] == "journals/sigir/LauwCSTTT23":
					continue

				# Do not include duplicates
				if len(list(filter(lambda p: p["title"] == publication["title"][:-1], result["publications"]))) > 0:
					print("d", end = "")
					continue

				# Parse to our format, add to list, template will automatically select latest
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
		saveCachedPublications(result)
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

	def seminarAnchorId(talk):
		talk_date = datetime.strptime(talk["when"], "%m/%d/%y")
		anchor_date = talk_date.strftime('%b') + str(int(talk_date.strftime('%d')))

		presenter = talk.get("presenter", {})
		presenter_name = presenter.get("name", "")
		name_parts = [re.sub(r"[^A-Za-z0-9]", "", part) for part in presenter_name.split()]
		speaker_key = next((part for part in reversed(name_parts) if part), "")

		if not speaker_key:
			if talk.get("departmental"):
				speaker_key = "Departmental"
			elif talk.get("special"):
				speaker_key = "Special"
			elif talk.get("empty"):
				speaker_key = "OpenSlot"
			else:
				speaker_key = "Talk"

		return f"{anchor_date}{speaker_key}"

	dist = "./dist"
	src = "./website"

	md = markdown.Markdown()
	templates = Environment(loader=FileSystemLoader(searchpath=str(Path(src) / "templates")))
	templates.filters['sortByLastName'] = sortByLastName
	templates.filters['sortByDate'] = sortByDate
	templates.filters['seminarAnchorId'] = seminarAnchorId
	templates.filters['formatDate'] = lambda input: datetime.strptime(input, "%m/%d/%y").strftime('%a, %b ') + str(int(datetime.strptime(input, "%m/%d/%y").strftime('%d')))
	templates.filters['limit'] = lambda input, n: input[:n]
	templates.filters['markdown'] = lambda input, style: f"<div class=\"markdown\" style=\"{style}\"> {Markup(md.convert(input))} </div>"

	# create dist structure
	recreateDir(dist, ignore_errors=True)

	shutil.copytree(Path(src) / "assets", Path(dist) / "assets")
	shutil.copy(Path(src) / "CNAME", Path(dist) / "CNAME")
	(Path(dist) / "assets" / "unminified").mkdir(parents=True, exist_ok=True)

	generateClasses(templates)

	# do not regenerate for each page
	publications = generatePublications("publications", "George_Kollios", "Manos_Athanassoulis", "Evimaria_Terzi", "Charalampos_E._Tsourakakis", "Mark_Crovella", "Kyle_Deeds")

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
