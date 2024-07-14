#!/usr/bin/env python3

import argparse
import os
import sys

from services import ParserService, DataService
from components import Template, ReleaseNotes, Version, ComComCLI, LogLevel, ParserArgumentException
from environments import GitLab

# Directory service
workdir = os.getcwd()

# Argument library
argLib = {}

def addArgLib(args, value: str, default):
    arg_value = getattr(args, value)
    if arg_value is None:
        arg_value = default
        ComComCLI.log(LogLevel["DEBUG"], "Default Value", f"Setting {value} = {default}")
    argLib[value] = arg_value

# Detect md file
def detectMDFile():
    md_files = [file for file in os.listdir(workdir) if file.endswith(".md")]
    if len(md_files) == 0:
        raise ParserArgumentException("file", f"No .md file found in {workdir}", solution="Please provide a file using '--file [PATH]'.")
    elif len(md_files) > 1:
        raise ParserArgumentException("file", f"More than one .md file found in [{workdir}]", solution="Please provide a file using '--file [PATH]'.")
    if md_files[0].lower() == "readme.md":
        raise ParserArgumentException("file", f"Detected '{md_files[0]}' is the only .md file in [{workdir}]", solution="Please provide a file using '--file [PATH]'.")
    ComComCLI.log(LogLevel["INFO"], "Detected .md file", f"Using '{md_files[0]}' as input file.")
    return md_files[0]

# Create Example 
def createExample():

    # Release Notes
    (mdFile, layout, exVers,exBuild) = Template.useExample()
    notes = ReleaseNotes(layout, mdFile, exVers, exBuild)
    notes.create()

    # vInfo.json
    version = Version(exVers, exBuild)
    version.create()

# Creating Release Notes
def create():

    # Files
    layout = argLib["layout"]
    mdFile = argLib["file"]

    # Options
    optionals = argLib["variables"]
    outputName = argLib["output"]
    vinfoName = argLib["vinfo"]
    logo = argLib["logo"]
    nologo = argLib["nologo"]
    
    # Select Compilation Method
    if argLib["gitlab"]:
        gitlab = GitLab()
        gitlab.useSSH(argLib["ssh"])
        gitlab.addKnownHosts(gitlab.getVariable("CI_SERVER_HOST"))
        gitlab.use(layout, mdFile, 
                   optionals=optionals, outputName=outputName, vInfoOutputName=vinfoName, 
                   logo=logo, nologo=nologo)
    else:
        exVers = argLib["version"]
        exBuild = argLib["build"]
        notes = ReleaseNotes(layout, mdFile, exVers, exBuild, 
                             optionals=optionals, outputName=outputName, 
                             logo=logo, nologo=nologo)
        notes.create()
        version = Version(exVers, exBuild, outputName=vinfoName)
        version.create()

# Clear
def clear():
    Template.clear()

# Main method
def main():

    # Status
    ComComCLI.printHeadline("CommitCompiler", "Starting the automated release documentation process.")

    # Create Parser
    parser = argparse.ArgumentParser(description="Example argparse application.")
    subparsers = parser.add_subparsers(dest="command")

    # Parser: Log Level
    parser.add_argument("--verbose", action="store_true", help="Sets the log level to 'Debug' and prints the most information about the processes of Commit Compiler.")
    parser.add_argument("--loglevel", type=str, help="Sets the log level to the specified value. Allowed are [\"DEBUG\",\"INFO\",\"WARNING\",\"ERROR\",\"CRITICAL\"]. Default value is 'INFO'.")
    
    # Parser: Example
    parser.add_argument("--example", action="store_true", help="Generates an example.md file and converts it to example.pdf and vInfo.json")

    # Parser: Layout
    parser.add_argument("--layout", type=str, help="Sets the layout .html file which is used for the markdown to .pdf conversion. If not specified the default layout.html is used.")

    # Parser: File (markdown release notes)
    parser.add_argument("--file", type=str, help="CommitCompiler tries to detect the markdown file itself. If it doesn't work you can specify the file with this argument.")

    # Parser: Output (name of the .pdf file)
    parser.add_argument("--output", type=str, help="Sets the name of the output .pdf file. If not specified, CommitCompiler will use the name of the original markdown file.")

    # Parser: vInfo (name of the resulting vInfo.json file)
    parser.add_argument("--vinfo", type=str, help="Sets the name of the output .json file. If not specified, CommitCompiler will name this file 'vInfo.json'.")

    # Parser: Logo
    parser.add_argument("--logo", type=str, help="Defines the logo .png file used in the layout. If not specified, CommitCompiler will use it's logo.")

    # Parser: No Logo
    parser.add_argument("--nologo", action="store_true", help="Prevents the default logo or a 'logo.png' file from the working directory to be used in the output pdf.")

    # Parser: Variables: SET Command
    variables_parser = subparsers.add_parser("set")
    variables_parser.add_argument("set", nargs=argparse.REMAINDER, help="Comma-separated key=value pairs for additional variables.")

    # Parser: SSH
    parser.add_argument("--ssh", help="SSH keys to be used by GitLab in order to push the changes back to the repository.")    

    # Git Environments
    parser.add_argument("--gitlab", action="store_true", help="Will perform the versioning with GitLab as VCS in mind. For more info check the documentation.")

    # Version & Buildnumber
    parser.add_argument("--version", type=str)
    parser.add_argument("--build", type=str)

    # Parse arguments
    args = parser.parse_args()

    # Log Levels
    if args.verbose: 
        ComComCLI.SetLogLevel(LogLevel["DEBUG"])
        print()
        ComComCLI.log(LogLevel["DEBUG"], "Log Level", "Set log level to: 'DEBUG'.")

    if args.loglevel:
        if args.loglevel.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ParserArgumentException("loglevel", f"Invalid loglevel provided: '{args.loglevel}'", solution="Provide a valid loglevel: [\"DEBUG\",\"INFO\",\"WARNING\",\"ERROR\",\"CRITICAL\"]")
        if args.verbose:
            ComComCLI.log(LogLevel["WARNING"], "No Impact", f"Using the 'verbose' attribute and specifying ' --loglevel {args.loglevel}' will prevent the loglevel from beeing set.")
        else:
            ComComCLI.SetLogLevel(args.loglevel)

    # Status
    ComComCLI.logSection("Processing Request")
    ComComCLI.printSeparator()
    ComComCLI.log(LogLevel["DEBUG"], "Running Environment", f"Running CommitCompiler in '{workdir}'")

    # Standalone args
    argLib["example"] = args.example
    if argLib["example"]:
        ComComCLI.logSection("Creating Example")
        createExample()
        ComComCLI.printExitSuccess("Succesfully created an example.")
        return
    
    # Layout
    addArgLib(args, "layout", Template.use())
    ComComCLI.log(LogLevel["INFO"], "Set layout file", f"Setting the layout .html file to: {argLib["layout"]}")

    # File (markdown)
    if args.file: argLib["file"] = args.file
    else: argLib["file"] = detectMDFile()
    ComComCLI.log(LogLevel["INFO"], "Using .md file", f"Using '{argLib["file"]}' as input for CommitCompiler.")

    # Output (pdf): either specified or name of markdown file
    addArgLib(args, "output", None)
    if args.output:
        ComComCLI.log(LogLevel["INFO"], "Set output .pdf file", f"Setting the output .pdf file to: {args.output}")
    
    # vInfo (name of the resulting vInfo.json file)
    addArgLib(args, "vinfo", "vInfo.json")
    if args.vinfo:
        ComComCLI.log(LogLevel["INFO"], "Set output .json file", f"Setting the output .json file to: {args.vinfo}")

    # NoLogo
    addArgLib(args, "nologo", False)
    if args.nologo:
        if args.logo:
            ComComCLI.log(LogLevel["WARNING"], "No Impact", f"Using the 'nologo' attribute and specifying a logo '--logo {args.logo}' will prevent the logo from beeing used.")

    # Logo
    addArgLib(args, "logo", None)
    if args.logo:
        ComComCLI.log(LogLevel["INFO"], "Using logo", f"Using '{args.logo}' as logo.")

    # Variables: SET Command
    if args.command == "set" and args.set:
        argLib["variables"] = ParserService.parseVariables(args)
        for name, value in argLib["variables"].items():
            ComComCLI.log(LogLevel["INFO"], "Variables", f"Creating variable: {name} = {value}")
    else:
        argLib["variables"] = {}

    # SSH authentication
    addArgLib(args, "ssh", None)
    if args.ssh:
        if not args.gitlab:
            ComComCLI.log(LogLevel["WARNING"], "No Impact", "Using the 'ssh' authentication and not using any git environment is not recommended (security vulnerability).")

    # Use GitLab Environment
    addArgLib(args, "gitlab", args.gitlab)
    if args.gitlab:
        if not args.ssh: raise ParserArgumentException.Mismatch("gitlab", "ssh")
        if args.version or args.build:
            ComComCLI.log(LogLevel["WARNING"], "No Impact", "Using the 'gitlab' environment and providing either '--version' or '--build' will not have any impact on the output.")

    # Version and Build
    addArgLib(args, "version", None) 
    addArgLib(args, "build", None) 

    # Verify mandatory arguments
    if not ( (argLib["version"] and argLib["build"]) or argLib["gitlab"] ):
        raise ParserArgumentException.MultipleMissing()

    # Execute
    create()

    # Status
    ComComCLI.printExitSuccess("Succesfully compiled your commit.")

# Run
if __name__ == "__main__":
    try:
        main()
    except ParserArgumentException as pae:
        print()
        ComComCLI.printExitParserError(pae)
        sys.exit(2)
    except Exception as e:
        ComComCLI.printExitError("CommitCompiler crashed with the following error:",e)
        sys.exit(1)
    finally:
        print()
        clear()


