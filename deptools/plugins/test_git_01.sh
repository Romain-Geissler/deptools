#!/bin/sh
set -e

error() {
    echo "error: $*"
    exit 1
}

dir=`dirname $0`
dir=`cd $dir; pwd`
TEST="env PYTHONPATH=$dir/.. python $dir/git.py"

tmpdir=`mktemp -d `
tmpbase=`basename $0 .sh`.tmp

cd $tmpdir
cwd=$tmpdir

# Be sure that git is present
git --version

# Be sure we are not in a git repository while performing this test
git log -n1 >/dev/null 2>&1 && \
    echo "error: this script must not run in a git repository" && exit 1

# Clean from previous runs
rm -rf ${tmpbase}*

# Prepare bare git
mkdir -p ${tmpbase}.1.git
cd ${tmpbase}.1.git
git init  # Note: --bare does not seem to work on git 1.5.4.3.
cd ..

# Prepare tree from work dir and push to bare
mkdir -p ${tmpbase}.1.work
cd ${tmpbase}.1.work
git init
git remote add origin $cwd/${tmpbase}.1.git
echo "a file" >afile
git add afile
git commit -m 'Added afile'
git push origin master
cd ..

# Prepare dependency spec
cat >${tmpbase}.1.dep <<EOF
name: a_test_dep
component:
  alias: ${tmpbase}.dep
  format: git
  label: master
  repos: $cwd/${tmpbase}.1
  revision: HEAD
EOF

# A deptools session
$TEST ${tmpbase}.1.ser new ${tmpbase}.1.dep
$TEST ${tmpbase}.1.ser clone 
$TEST ${tmpbase}.1.ser dump
$TEST ${tmpbase}.1.ser dump_actual
$TEST ${tmpbase}.1.ser update
$TEST ${tmpbase}.1.ser execute touch bfile
$TEST ${tmpbase}.1.ser execute git add bfile
$TEST ${tmpbase}.1.ser commit -m 'Added empty bfile'
$TEST ${tmpbase}.1.ser rebase
$TEST ${tmpbase}.1.ser deliver
$TEST ${tmpbase}.1.ser execute touch cfile
$TEST ${tmpbase}.1.ser execute git add cfile
$TEST ${tmpbase}.1.ser commit -m 'Added empty cfile'

# Add a new file in the work repository
cd ${tmpbase}.1.work
echo "d file" >dfile
git add dfile
git commit -m 'Added dfile'
git fetch origin
git rebase origin/master
git push origin master
cd ..

# A second deptools session
$TEST ${tmpbase}.1.ser rebase
$TEST ${tmpbase}.1.ser deliver
$TEST ${tmpbase}.1.ser list

# Now checks that the repository is ok
git clone ${tmpbase}.1.git ${tmpbase}.final
cd ${tmpbase}.final
[ -f afile -a  "`cat afile`" = "a file" ] || error "missing afile"
[ -f bfile -a "`cat bfile`" = "" ] || error "missing bfile"
[ -f cfile -a "`cat cfile`" = "" ] || error "missing cfile"
[ -f dfile -a "`cat dfile`" = "d file" ] || error "missing dfile"

# Notify success
echo SUCCESS

rm -rf $tmpdir
