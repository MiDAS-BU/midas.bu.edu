# MiDAS website

Deployment link: [midas.bu.edu](https://midas.bu.edu).

## Instructions

The website is built in a way that enables easy updates of dynamic data.
Simply use `./scripts/build.py` to assemble the website.
You may need to install dependencies `pip3 install -r requirements.txt`.
Upon completion, the script will put the website in `./dist` directory.

Alternatively, if you have Docker installed, use the following one-liner:
```bash
docker run -it -v ${PWD}:/code dbogatov/docker-images:python-extras-latest /code/scripts/build.py
```

### How to change dynamic data

Look at [configs](./website/assets/config).
You need to modify these files according to commented instructions and using examples in these files.
Afterwards use `./scripts/build.py` to assemble the website, and open HTML from `./dist` directory.

It is possible to make slight text changes to the HTML page, just be sure it does not break the layout.

The deployment is done through GitHub pages.
GitHub hosts a content of `gh-pages` branch.
To push to this branch we have a convenient script [deploy.sh](./deploy.sh).
What it does is it pushes a subtree (the `dist` directory) to the branch.
Run this script to publish the latest commit (note that you need to commit to master first).

### Template and files in the root

We have purchased [this template](https://wrapbootstrap.com/theme/particles-personal-agency-template-WB05N7852) for our website.
We used a tiny fraction of its content.
If you want to add a section or a page, look at the template, it mau already have it.

The files in the root are for development purposes and are not published.
`.dockerignore`, `Dockerfile` and `nginx.conf` allow to build a docker image with the website (e.g. for Kubernetes).
`.editorconfig` defines some formatting rules.
`.gitlab-ci.yml` define CI configuration (Gitlab format), it builds/tests/publishes the website, but does so internally using pre-configured Gitlab.
`requirements.txt` define pip packages needed to assemble the website.
You may safely ignore these files.
