#!/usr/bin/env python
#
# This software is delivered under the terms of the MIT License
#
# Copyright (c) 2009 Christophe Guillon <christophe.guillon.perso@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

import os, sys
def check_python_version_():
    try:
        assert sys.hexversion >= 0x02040000
    except:
        print >>sys.stderr, 'deptools: warning: python version >= 2.4 is required'
        sys.exit(1)
check_python_version_()  

import getopt, copy

# non standard package, use local version
import yaml

# SourceManagers
from plugins import SourceManager 
from plugins import PluginLoader

version = "0.0.1"

class DefaultConfig:
    def __init__(self):
        self.dep_file = "DEPENDENCIES"
        self.configuration = "default"

class Config:
    def __init__(self, params):
        self.dep_file = params.dep_file
        self.configuration = params.configuration

    def parse_options(self, opts, args):
        for o, a in opts:
            if o in ("-f", "--file"):
                self.dep_file = a
            if o in ("-c", "--config"):
                self.configuration = a

    def check(self):
        return True


class DependencyFile:
    def __init__(self, content = None):
        self.content = content
    def dump(self, ostream = sys.stdout):
        print >>ostream, yaml.dump(self.content)
    def load(self, istream = sys.stdin):
        self.content = yaml.load(istream)

class Dependency:
    def __init__(self, config):
        self.config = config
        self.deps = None
        self.components = []
        self.load()
        self.prepare()

    def load(self):
        if self.config.dep_file == "-":
            stream = sys.stdin
        else:
            stream = file(self.config.dep_file)
        deps =  DependencyFile()
        deps.load(stream)
        self.deps = deps.content
        
    def dump(self, component_names=[]):
        DependencyFile(self.deps).dump()

    def dump_actual(self, component_names=[]):
        if component_names == []:
            component_names = self.deps['configurations'][self.config.configuration]
        deps_actual = copy.deepcopy(self.deps)
        for component in self.components:
            name = component.name()
            if name in component_names:
                actual = component.get_actual_revision()
                deps_actual['repositories'][name]['revision'] = actual
        DependencyFile(deps_actual).dump()

    def dump_head(self, component_names=[]):
        if component_names == []:
            component_names = self.deps['configurations'][self.config.configuration]
        deps_head = copy.deepcopy(self.deps)
        for component in self.components:
            name = component.name()
            if name in component_names:
                head = component.get_head_revision()
                deps_head['repositories'][name]['revision'] = head
        DependencyFile(deps_head).dump()

    def prepare(self):
        configurations = self.deps.get("configurations")
        if configurations == None or type(configurations) != type({}):
            raise Exception, "Missing configurations map in dependency file: " + self.config.dep_file
        components = configurations.get(self.config.configuration)
        if components == None or type(components) != type([]):
            raise Exception, "Missing components list specification for configuration: " + self.config.configuration
        repositories = self.deps.get("repositories")
        if repositories == None or type(repositories) != type({}):
            raise Exception, "Missing repositories map in dependency file: " + self.config.dep_file
        self.components = []
        for component in components:
            repository = repositories.get(component)
            if repository == None or type(repository) != type({}):
                raise Exception, "Missing repository map for component: " + component
            format = repository.get("format")
            if format == None or type(format) != type(""):
                raise Exception, "Missing format specification for component: " + component
            self.components.append(SourceManager.get_plugin(format)(component, repository))

    def foreach(self, command, args=[]):
        for component in self.components:
            if command == "execute":
                component.execute(args)
            elif command == "extract":
                component.extract(args)
            elif command == "extract_or_updt":
                component.extract_or_updt(args)
            elif command == "update":
                component.update(args)
            elif command == "commit":
                component.commit(args)
            elif command == "rebase":
                component.rebase(args)
            elif command == "deliver":
                component.deliver(args)
            elif command == "dump":
                component.dump(args)
            elif command == "dump_actual":
                component.dump_actual(args)
            elif command == "dump_head":
                component.dump_head(args)
            elif command == "list":
                component.list(args)
            else:
                error("unexpected command! " + command)

    def exec_cmd(self, command, args=[]):
        if command == "dump":
            self.dump(args)
        elif command == "dump_actual":
            self.dump_actual(args)
        elif command == "dump_head":
            self.dump_head(args)
        else:
            self.foreach(command, args)

def print_error(msg):
  print "error: " +  msg

def error(msg):
  print_error(msg)
  sys.exit(1)

def usage(config):
  print "usage: " + sys.argv[0] + " [options...] [cmd...]"
  print


def print_error(msg):
  print os.path.basename(sys.argv[0]) + ": error: " + msg

def error(msg):
  print_error(msg)
  sys.exit(1)

def usage(config):
  print "usage: " + sys.argv[0] + " [options...] [command...]"
  print
  print "where command is one of:"
  print " list: list all dependencies"
  print " extract: extract all dependencies"
  print " update: update all dependencies"
  print " extract_or_updt: extract all dependencies or update if already existing"
  print " commit: commit all dependencies"
  print " freeze: freeze all dependencies revisions"
  print " execute: execute command for all dependencies"
  print " dump: dumps to stdout the dependencies"
  print " dump_actual: dumps to stdout the dependencies with actual revisions"
  print " dump_head: dumps to stdout the dependencies at head revisions"
  print ""
  print "where options are:"
  print " -f|--file <dep_file> : dependency file. Default [" + config.dep_file + "]"
  print " -c|--config <configuration> : configuration to use from the dependency file. Default [" + config.configuration + "]"
  print " -q|--quiet : quiet mode"
  print " -v|--version : output this script version"
  print " -h[--help : this help page"

def main():
    pdir = os.path.dirname(sys.argv[0])        
    pdir = os.path.abspath(pdir) 
    def_config = DefaultConfig()
    config = Config(def_config)
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "f:c:qvh", ["file=", "config=", "quiet", "version", "help"])
    except getopt.GetoptError, err:
        print_error(str(err))
        usage(def_config)
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage(def_config)
            sys.exit(0)
        elif o in ("-v", "--version"):
            print "deptool.py version " + version
            sys.exit(0)
    config.parse_options(opts, args)
    if not config.check():
        sys.exit(2)
    if len(args) == 0:
        error("missing command, try --help for usage")
    dependency = Dependency(config)
    dependency.exec_cmd(args[0], args[1:])

if __name__ == "__main__":
  main()
