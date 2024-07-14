# CommitCompiler

When ever a new build is successfully done and a new version of an application or other versioned files is ready for release, it is a good idea to create documentation of this version. **CommitCompiler** supports during this process. It is able to convert markdown (.md) files containing release information into a .pdf file. Additionally, a JSON file containing build information can be created (_vInfo.json_). If **GitLab** is used for version control, this process can be mostly automated by providing _ssh credentials_ for the repository and following the __CommitCompiler GitLab Workflow__.

---

You can find the latest built of [**CommitCompiler**](https://hub.docker.com/r/faseengineering/commit-compiler) on Docker Hub. 

## How to use CommitCompiler

The application is based inside a docker container. Therefore, it's more easy to integrate it in a CI/CD pipeline. To run **CommitCompiler** two possibilities are available (verison 1.0.0):

1. Use manual arguments

   ```bash
   comcom --version "0.1.2" --build "build_id"
   ```

2. Use **CommitCompiler GitLab Workflow**

   ```bash
   comcom --gitlab --ssh "AUTHORIZED_SSH_KEY"
   ```

Both of the above calls of `comcom` are the minimum required argument set. For all further documentation, the command `comcom *` will represent one of those two minimum required argument sets.

### Additional arguments

Next to the minimum required arguments, additional arguments can be provided to influence the output of `comcom`. The following arguments are supported:

#### Logging

**CommitCompiler** supports logging at different levels. You can either inspect all possible logs using `--verbose` or `--loglevel DEBUG`. Additionally, you can set all other supported log levels:

| **Level** | **Description** | **Value** |
| - | - | - |
| CRITICAL | Shows only system critical logs | 50 |
| ERROR | Shows only critical and error logs | 40 |
| WARNING | Shows critical, error and warning logs | 30 |
| INFO | Shows all levels above or equal to 20 | 20 |
| DEBUG | Shows all levels above or equal to 10 | 10 |

You can specify the log levels using:

```bash
comcom * --loglevel LEVEL
```

#### Results

By default **CommitCompiler** will use the following values for its results:

| **Result** | **Value** | **Description** |
| - | - | - |
| markdown file | ReleaseNotes.md | The version tracking file, written in markdown |
| PDF file | {MarkdownFile}.pdf | The resulting PDF document. It will have the same name as the markdown file by default. |
| json file | vInfo.json | The resulting JSON file containing built information. |

You can change the default values using the following commands

1. Markdown File [^1]:

   ```bash
   comcom * --file "path/to/markdown.md"
   ```
   [^1]: You can provide a path from the working directory of the application, but it needs to begin without "./" or "/".

2. PDF File [^2]:

   ```bash
   comcom * --output "output.pdf"
   ```
   [^2]: Pay attention! This command cannot accept a path since the output directory of the PDF file will always be in the working directory plus "/release". 

3. vInfo.json [^1]:

   ```bash
   comcom * --vinfo "version.json"
   ```

Next to the output files, **CommitCompiler** uses template files to achieve a successful result. It will use the following default files to create its results:

| **File** | **Value** | **Description** |
| - | - | - |
| HTML Layout | layout.html | The layout file where the converted markdown content is placed in. This file will define the layout of the output PDF file. |
| Logo | logo.png | In the default layout a logo is configured. If no additional logo is provided, the logo of **CommitCompiler** is used. |

You can change the files using the following commands:

1. Layout File [^1]: 

   ```bash
   comcom * --layout "path/to/html_layout.html"
   ```

2. Logo [^1] [^3]:

   ```bash
   comcom * --logo "path/to/logo.png"
   ```

   [^3]: Pay attention! Currently only .png files are supported as logos.

#### Providing additional variables

The design of **CommitCompiler** lets the user pass additional variables which will be added to the provided (or default) layout file. Adding a variable can be done by:

```bash
comcom * set variable1=value1, variable2="value 2" 
```

Note, that this is not an argument but a command, thus it needs to be added in the end of the overall execution string. 

**Example of adding multiple variables**:
```bash
comcom * set title="MyTitle", subtitle="MySubTitle", website-url="https://example.com", website-alias="A Website Example"
```

### Example release documentation

If you want to tryout **CommitCompiler** you can do this by running:

```bash
comcom --example
```

Which will generate a set of example files in the `/usr/src/app` directory of the container. This lets you inspect on how the system is working and how the results will look like. 


## Using the default layout

Like described earlier, **CommitCompiler** uses a default layout file to generate the output PDF document. Next to the required arguments `--verion` and `--build`, the default layout needs more information for a pretty result. Have a look at the section **Providing additional variables** for more information on how to provide additional information.

### Predefined variables

Some variables are predefined. If a custom layout is made, those values can be used within the _layout.html_ file.

| **Variable** | **Description** |
| - | - |
| `{{version}}` | The version identifier for the current release. |
| `{{build}}` | The build number (e.g. commit hash) for the current release. |
| `{{content}}` | The content of the release notes will be placed where this variable is set. |
| `{{doctitle}}` | Specifies the title of the document |
| `{{date}}` | A timestamp beeing created when executing CommitCompiler |
| `{{website-url}}` | The url for your website |
| `{{website-alias}}` | An alias (beeing displayed) for the url of your website |
| `{{logo}}` | A converted logo which can be integrated in the image URL |

### Custom Layout

If the layout needs to be customized, this can be done by creating a HTML file. Within this file, the predefined or additional variables can be set. Any variable provided to **CommitCompiler** like described in the section **Providing additional variables** can be set in the HTML document. If variables are set like:

```bash
comcom * --layout "custom.html" set attribue="An Attribute", variable="A variable"
```

They can be used in the custom layout _custom.html_ like:

```xml
<html_tag attr="{{attribute}}">{{variable}}</html_tag>
```

___