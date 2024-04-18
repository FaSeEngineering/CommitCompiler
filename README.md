# CommitCompiler
This project integrates into CI/CD pipelines of GitLab or GitHub to automate versioning and release documentation. After a commit to the master branch, the system extracts keywords from the commit message to generate version numbers. Additionally, it appends a specially formatted part of the message (written in Markdown) to a release notes document

## Features:

* Automatic version generation based on commit messages.
* Dynamic updating of a Markdown file with release notes.
* Optional PDF export using LaTeX and custom created template files.
* Dockerized system enables easy integration in CI/CD pipelines.
