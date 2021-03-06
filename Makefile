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
# Simple top level makefile for deptools
#
# usage:
#  make all check
#  make PREFIX=/yout/prefix install # PREFIX defaults to /usr/local
#
#  Actually each project should copy the dependencies script on it's top level directory.
#

PREFIX?=/usr/local
DEPTOOL_REPO=http://github.com/guillon/deptools.git
DEPTOOL_REV=origin/master
SCRIPTS=dependencies

all: $(SCRIPTS)

$(SCRIPTS): Makefile

$(SCRIPTS): %: %.in
	(sed -e 's|@DEPTOOL_REPO@|$(DEPTOOL_REPO)|g' -e 's|@DEPTOOL_REV@|$(DEPTOOL_REV)|g' $< > $@ && chmod 755 $@) || rm -f $@

clean:
	rm -f $(SCRIPTS)

distclean: clean

install: | $(PREFIX)
	install -m 755 $(SCRIPTS) $(PREFIX)/

$(PREFIX):
	install -d $(PREFIX)

check: check-tests check-examples

check-tests: all
	deptools/test.sh

check-examples: all
	examples/run_all_examples.sh

.PHONY: all clean distclean install check check-tests check-examples