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

		# dblp's JSON search API now sits behind a bot-detection challenge (see
		# https://dblp.org/robots.txt), so publications are fetched via dblp's
		# public SPARQL endpoint instead.
		DBLP_SPARQL_ENDPOINT = "https://sparql.dblp.org/sparql/dblp"

		EXCLUDED_KEYS = {
			"conf/sigmod/2024ari", "journals/tist/LauwNTT25", "journals/pvldb/Koutrika023f",
			"journals/sigweb/LauwCSTTT23", "conf/wsdm/2023", "journals/sigir/LauwCSTTT23",
		}

		def authorsToString(author_names):
			return ", ".join(name.rstrip(digits).strip() for name in author_names)

		def runSparqlQuery(query):
			response = requests.post(
				DBLP_SPARQL_ENDPOINT,
				data={"query": query},
				timeout=30,
				headers={"Accept": "application/sparql-results+json"},
			)
			if response.status_code != 200:
				print(f"\n\tDBLP SPARQL request failed with status {response.status_code}.")
				exit(1)
			try:
				return response.json()["results"]["bindings"]
			except (ValueError, KeyError):
				print(f"\n\tDBLP SPARQL returned an unexpected response.")
				exit(1)

		# load from file first
		result = loadData(file)
		print("Collecting publications:", end = "")

		for name in names:

			display_name = name.replace("_", " ")
			bindings = runSparqlQuery(f"""
				PREFIX dblp: <https://dblp.org/rdf/schema#>
				SELECT ?pub ?title ?venue ?year ?ee WHERE {{
					?creator dblp:primaryCreatorName "{display_name}" .
					?pub dblp:authoredBy ?creator .
					?pub dblp:title ?title .
					?pub dblp:yearOfPublication ?year .
					OPTIONAL {{ ?pub dblp:publishedIn ?venue . }}
					OPTIONAL {{ ?pub dblp:primaryDocumentPage ?ee . }}
				}} ORDER BY DESC(?year)
			""")
			print(f"\n\t{name}: ", end = "")

			publications = []
			for binding in bindings:
				venue = binding.get("venue", {}).get("value")
				if not venue or venue == "CoRR" or venue == "IACR Cryptol. ePrint Arch.":
					continue

				key = binding["pub"]["value"].removeprefix("https://dblp.org/rec/")
				if key in EXCLUDED_KEYS:
					continue

				publications.append({
					"key": key,
					"pub": binding["pub"]["value"],
					"title": binding["title"]["value"],
					"venue": venue,
					"year": binding["year"]["value"],
					"ee": binding.get("ee", {}).get("value"),
				})

			# fetch ordered author names for the surviving publications in one batched query
			authors_by_pub = {}
			if publications:
				values = " ".join(f"<{p['pub']}>" for p in publications)
				author_bindings = runSparqlQuery(f"""
					PREFIX dblp: <https://dblp.org/rdf/schema#>
					SELECT ?pub ?ord ?authorName WHERE {{
						VALUES ?pub {{ {values} }}
						?pub dblp:hasSignature ?sig .
						?sig dblp:signatureCreator ?c .
						?sig dblp:signatureOrdinal ?ord .
						?c dblp:primaryCreatorName ?authorName .
					}} ORDER BY ?pub ?ord
				""")
				for binding in author_bindings:
					authors_by_pub.setdefault(binding["pub"]["value"], []).append(binding["authorName"]["value"])

			for publication in publications:

				# Do not include duplicates
				if len(list(filter(lambda p: p["title"] == publication["title"][:-1], result["publications"]))) > 0:
					print("d", end = "")
					continue

				# Parse to our format, add to list, template will automatically select latest
				entry = {
					"title": publication["title"][:-1], # remove period
					"authors": authorsToString(authors_by_pub.get(publication["pub"], [])),
					"venue": publication["venue"],
					"date": {
						"year": int(publication["year"])
					},
					"links": {},
				}
				if publication["ee"]:
					entry["links"]["abstract"] = publication["ee"]
				result["publications"] += [entry]
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
	# Charalampos_E._Tsourakakis left BU, no longer pulled into publications
	publications = generatePublications("publications", "George_Kollios", "Manos_Athanassoulis", "Evimaria_Terzi", "Mark_Crovella", "Kyle_Deeds")

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
