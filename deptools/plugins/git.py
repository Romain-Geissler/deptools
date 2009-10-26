from subprocess import call
from subprocess import check_call
from plugins import SourceManager
import os, sys
import yaml

verbose = 0

class GitConfig:
    def __init__(self):
        self.git = 'git'
        self.verbose = 0

class GitManager(SourceManager):
    """ This class implements the git format manager plugin.
    The tests for this class are in test_git_*.sh.
    The command line interface for this class is implemented in the
    GitManagerCmdLine class below.
    The Configuration class for this class is the GitConfig class.
    """
    name = "git"
    description = "git repository manager"
    
    def __init__(self, name, component, config = GitConfig()):
        self.name = name
        self.component = component
        self.config = config
        if component['alias'] != None:
            self.basename = component['alias']
        else:
            self.basename = os.path.basename(self.component['repos'])
            if self.basename.endswith(".git"):
                self.basename = self.basename.rsplit('.', 1)[0]
        self.cwd = os.getcwd()

    def _cmd(self, args):
        if self.config.verbose:
            print " ".join(args)
        check_call(args)
    
    def _subcmd(self, args):
        if not os.path.exists(self.basename):
            raise Exception, "path does not exist: " + self.basename
        os.chdir(self.basename)
        self._cmd(args)
        os.chdir(self.cwd)
        
    def execute(self, args):
        if self.config.verbose:
            print "Execute " + self.basename
        self._subcmd(args)

    def clone(self, args = []):
        if self.config.verbose:
            print "Clone " + self.basename
        try:
            if os.path.exists(self.basename):
                raise Exception, "path exists: " + self.basename
            self._cmd([self.config.git, 'clone', self.component['repos'], self.basename])
            self._subcmd([self.config.git, 'checkout', self.component['label']])
        except Exception, e:
            raise Exception, "cannot clone component: " + str(e)
        
    def update(self, args = []):
        if self.config.verbose:
            print "Update " + self.basename
        try:
            self._subcmd([self.config.git, 'fetch', 'origin'])
            self._subcmd([self.config.git, 'merge', 'origin/' + self.component['label']])
        except Exception, e:
            raise Exception, "cannot update component: " + str(e)

    def commit(self, args = []):
        if self.config.verbose:
            print "Commit " + self.basename
        try:
            self._subcmd([self.config.git, 'commit' ] + args)
        except Exception, e:
            raise Exception, "cannot commit component: " + str(e)

    def rebase(self, args = []):
        if self.config.verbose:
            print "Rebase " + self.basename
        try:
            self._subcmd([self.config.git, 'fetch', 'origin'])
            self._subcmd([self.config.git, 'rebase', 'origin/' + self.component['label']])
        except Exception, e:
            raise Exception, "cannot rebase component: " + str(e)

    def deliver(self, args = []):
        if self.config.verbose:
            print "Deliver " + self.basename
        try:
            self._subcmd([self.config.git, 'push', 'origin', self.component['label']])
        except Exception, e:
            raise Exception, "cannot deliver component: " + str(e)

    def dump(self, args = []):
        if self.config.verbose:
            print "Dump " + self.basename
        print yaml.dump(self.component)

    def get_actual_revision(self, revision):
        try:
            self._subcmd([self.config.git, 'log', '--pretty=oneline', '-n1', revision])
        except Exception, e:
            raise Exception, "cannot get actual revision: " + str(e)
        return "TODO"

    def dump_actual(self, args = []):
        if self.config.verbose:
            print "Dump_actual " + self.basename
        actual = self.component
        actual['revision'] = self.get_actual_revision(actual['revision'])
        print yaml.dump(actual)

    def list(self, args = []):
        if self.config.verbose:
            print "List " + self.basename
        if self.component['alias'] != None:
            alias_str = "," + self.component['alias']
        else:
            alias_str = ""
        print self.name + "," + self.component['label'] + "@" + self.component['revision'] +  "," + self.component['repos'] + alias_str


class GitManagerCmdLine:
    """ This is a comand line class proxy for the GitManager class.
    The principle is to maintain a serial file for the GitManager object
    and apply internal method to the deserialized file, then serialize
    the object back to file.
    The special command new starts a new session by creating an object
    from a yaml dump of the constructors arguments.
    There is probably a much better way to implement the exec_cmd function
    by invoking directly the method name.
    Also the serialization of the GitManager class may be refactored into
    a generic support, perhaps in a metaclass.
    Refer to test_git_01.sh for example of usage.
    """
    def __init__(self, args):
        self._serial = args[0]
        self._manager = None
        self._exec_cmd(args[1], args[2:])

    def _serialize_manager(self, manager, ostream = sys.stdout):
        print >> ostream, yaml.dump(manager)

    def _deserialize_manager(self, istream = sys.stdin):
        return yaml.load(istream)

    def _new_session(self, args_serials):
        params_stream = open(args_serials[0], "r")
        params = yaml.load(params_stream)
        self._manager = GitManager(params['name'], params['component'])

    def _store_session(self):
        ofile = open(self._serial, "w")
        self._serialize_manager(self._manager, ofile)

    def _restore_session(self):
        ifile = open(self._serial, "r")
        self._manager = self._deserialize_manager(ifile)

    def _exec_cmd(self, cmd_name, args):
        if cmd_name == "new":
            self._new_session(args)
        else:
            self._restore_session()
            if cmd_name == "execute":
                self._manager.execute(args)
            elif cmd_name == "clone":
                self._manager.clone(args)
            elif cmd_name == "update":
                self._manager.update(args)
            elif cmd_name == "commit":
                self._manager.commit(args)
            elif cmd_name == "rebase":
                self._manager.rebase(args)
            elif cmd_name == "deliver":
                self._manager.deliver(args)
            elif cmd_name == "dump":
                self._manager.dump(args)
            elif cmd_name == "dump_actual":
                self._manager.dump_actual(args)
            elif cmd_name == "list":
                self._manager.list(args)
            else:
                print "unexpected command: ignored: " + " ".join(args)
        self._store_session()

if __name__ == "__main__":
    GitManagerCmdLine(sys.argv[1:])
else:
    if verbose == 1:
        print "Loading " + __name__         