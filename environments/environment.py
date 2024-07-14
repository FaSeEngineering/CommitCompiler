import subprocess
import os

from typing import Dict, List

from services import DataService
from components import ComComCLI, LogLevel

# Container Environment
class ContainerEnvironment:
    
    # Constructor
    def __init__(self) -> None:
        pass

    # Environment Variables
    def getVariable(self, name: str) -> str:
        value = os.getenv(name)
        if value is None:
            e = self.VariableNotFoundException(f"Environment variable '{name}' not found.")
            ComComCLI.log(LogLevel["WARNING"], "Using a non-existing environment variable", e)
            raise e
            #return "none"
        else:
            ComComCLI.log(LogLevel["DEBUG"], "Accessing environment variable", f"Name: {name}")
            return value
    
    class VariableNotFoundException(Exception):
        pass

    # SSH
    def useSSH(self, sshKey):
        ComComCLI.logSection("SSH Authentication")
        ComComCLI.printSeparator()
        try:
            status = self.__start_ssh_agent()
            ComComCLI.log(LogLevel["INFO"], "Starting SSH Service", f"Status: {status}")
            self.__add_ssh_key(sshKey)
        except Exception as e:
            ComComCLI.log(LogLevel["ERROR"], "Starting SSH Service failed.", e)
            raise e

    def addKnownHosts(self, host):
        self.__add_to_known_hosts(host)

    def __start_ssh_agent(self):
        process = subprocess.Popen(['ssh-agent', '-s'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception(f"Failed to start ssh-agent: {stderr.decode('utf-8')}")
        for line in stdout.decode('utf-8').split(';'):
            if line.startswith('SSH_AUTH_SOCK') or line.startswith('SSH_AGENT_PID'):
                key, _, value = line.partition('=')
                os.environ[key] = value
        return "Running"

    def __add_ssh_key(self, key_string):
        cmd = f"echo \"{key_string}\" | tr -d '\r' | ssh-add -"
        try:
            subprocess.run(cmd, check=True, shell=True)
            ComComCLI.log(LogLevel["INFO"], "SSH keys added", "Status: OK")
        except Exception as e:
            ComComCLI.log(LogLevel["ERROR"], "Adding SSH keys failed.", e)
            raise e
        
    def __add_to_known_hosts(self, hostname):
        try:
            ssh_dir = os.path.expanduser('~/.ssh')
            if not os.path.exists(ssh_dir):
                os.makedirs(ssh_dir, mode=0o700)
            result = subprocess.run(['ssh-keyscan', hostname], capture_output=True, text=True, check=True)
            host_key = result.stdout
            known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
            with open(known_hosts_path, 'a') as known_hosts_file:
                known_hosts_file.write(host_key)
            ComComCLI.log(LogLevel["INFO"], f"Adding {hostname} to known hosts.", f"Host key for {hostname} added to {known_hosts_path}.")
        except subprocess.CalledProcessError as e:
            ComComCLI.log(LogLevel["ERROR"], f"Adding {hostname} key to known hosts failed.", e)
            raise e
    
# Git Environment
class GitEnvironment(ContainerEnvironment):

    # Properties
    @property
    def DefaultCommitMessage(self):
        return self.__commitMessage.format(timestamp=DataService.Timestamp())
    
    # Constructor
    def __init__(self) -> None:
        super().__init__()
        self.__commitMessage = "This commit was automatically created by CommitCompiler at {timestamp}. Release documentation has been updated."
    
    # Git
    __commands = { 
        "remote": ["/usr/bin/git", "remote", "set-url", "origin", "git@{server}:{path}.git"],
        "checkout": ["/usr/bin/git", "checkout", "-B", "{branch}", "origin/{branch}"],
        "fetch": ["/usr/bin/git", "fetch", "origin"],
        "config.email": ["/usr/bin/git", "config", "--global", "user.email", "{email}"],
        "config.author": ["/usr/bin/git", "config",  "--global", "user.name", "{author}"],
        "add": ["/usr/bin/git", "add"],
        "commit": ["/usr/bin/git", "commit", "-m", "\"{message}\""],
        "push": ["/usr/bin/git", "push", "origin", "{branch}", "-o", "ci.skip"]
    }

    def command(self, command_name, **kwargs):
        if command_name not in self.__commands:
            raise ValueError(f"Command '{command_name}' not found")
        command_template = self.__commands[command_name]
        try:
            if kwargs is None:
                return self.__commands[command_name]
            else:
                formatted_command = [part.format(**kwargs) if '{' in part else part for part in command_template]
        except KeyError as e:
            raise ValueError(f"Missing required argument for {command_name}: {e}")
        return formatted_command

    # Execution
    def execute(self, commands: Dict[str, List[str]]) -> None:
        ComComCLI.logHeader()
        try:
            for key, cmd in commands.items():
                ComComCLI.log(LogLevel["INFO"], f"Executing: {key}", "HIDDEN")
                ComComCLI.log(LogLevel["DEBUG"], f"Executing: {key}", f"{cmd}")
                if os.name == "posix":
                    subprocess.run(cmd, check=True)
        except Exception as e:
            ComComCLI.log(LogLevel["ERROR"], f"Executing: {key}", e)
            raise e
