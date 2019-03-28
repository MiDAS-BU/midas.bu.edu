# MiDAS website

Deployment link: [midaslab-bu.github.io/website](https://midaslab-bu.github.io/website/).

## Instructions

The website is built in a way that enables easy updates on changing data.

### How to add / update / remove a person profile

Update the JSON in [website/json/people.json](./website/json/people.json).
The correct entry format is the following:

	{
		"name": "FirstName LastName",
		"image": "images/people/link-to-avatar.jpeg",
		"position": "e.g. PhD Researcher",
		"website": "http://link-to-personal-webspage",
		"category": "students"
	}

All fields are **required**.
The `name` can contain middle names if necessary.
The `image` must be a path.
If the image is inside this website's `images/` directory (preferred), then the path is *relative*, otherwise the full URL (i.e. `https://...`) must be provided).
It is recommended to be consistent in `position` naming (e.g. avoid having *phd student* and *PhD Researcher*).
The `website` must be a full URL - either to BU hosted webpage (`http://cs-people.bu.edu/...`), or to personal website.

The category must strictly be one of the defined categories.
As of now we support *(PhD) students*, *faculty* and *(graduate) alumni*.
The categories are defined in the same JSON file and define the ID used by `people` objects, title displayed on the page and if the section is collapsible.
Although it is possible to add / update / remove categories, it is recommended that the website manager does it.

The profiles inside a category are sorted alphabetically byt he last name, except PostDocs come before PhD students.
For this purpose, the last name is the last word in `name`.

### How to add / update / remove a publication

Update the JSON in [website/json/publications.json](./website/json/publications.json).
An example of the correct entry format is the following:

	{
		"title": "A Comparative Evaluation of Order-Preserving and Order-Revealing Schemes and Protocols",
		"authors": "D. Bogatov, G. Kollios and L. Reyzin",
		"venue": "VLDB",
		"date": {
			"year": 2019
		},
		"links": {
			"pdf": "https://dbogatov.org/assets/custom/docs/ore-benchmark.pdf",
			"abstract": "https://ia.cr/2018/953"
		}
	}

All fields are **required**, except `links`.
`title`, `authors` and `venue` will be displayed as is.
For authors the convention is to use the first letter of the first name and full last name.
The `year` will be used to sort the list of publications and display the latest.

`links` are *optional*.
**If a paper has no link(s), just do not include them.**
**Do not leave fields empty.**
PDF link is supposed to immediately download PDF file.
Abstract link will be displayed as "External" and is supposed to lead to a paper webpage, e.g. ePrint, arxiv, ACM.
One or both of them may not be included, then the links will not be displayed.
Please make sure that the links are working (some links, for example, work only from a specific domain).

The papers will be rendered in the ascending order by year (within one year the order is undefined).
The number of rendered papers is set by `publicationsDisplayed` variable in [website/js/main.js](./website/js/main.js).

### Small edits and deployment

It is possible to make slight text changes to the HTML page, just be sure it does not break the layout.

The deployment is done through GitHub pages.
GitHub hosts a content of `gh-pages` branch.
To push to this branch we have a convenient script [deploy.sh](./deploy.sh).
What it does is it pushes a subtree (the `website` directory) to the branch.
Run this script to publish the latest commit (note that you need to commit to master first).

### Template and files in the root

We have purchased [this template](https://wrapbootstrap.com/theme/particles-personal-agency-template-WB05N7852) for our website.
We used a tiny fraction of its content.
If you want to add a section or a page, look at the template, it mau already have it.

The files in the root are for development purposes and are not published.
`.dockerignore`, `Dockerfile` and `nginx.conf` allow to build a docker image with the website (e.g. for Kubernetes).
`.editorconfig` defines some formatting rules.
`.gitlab-ci.yml` define CI configuration (Gitlab format), it builds/tests/publishes the website, but does so internally using pre-configured Gitlab.
You may safely ignore these files.
