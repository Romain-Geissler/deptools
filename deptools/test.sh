#!/bin/sh
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

set -e
dir=`dirname $0`

[ "$DEBUG" = "" ] || set -x

failed=0

exit_func() {
    echo
    [ $failed = 1 ] || echo "PASSED: all tests passed"
    [ $failed = 0 ] || echo "FAILED: some tests failed"
}

failed() {
  echo "TEST-UNEXPECTED-FAIL | $*" >&2
  failed=1
}

success() {
  echo "TEST-PASS | $*" >&2
}

trap "exit_func" 0 1 15

for i in $dir/test_*.sh $dir/plugins/test_*.sh
do
    echo "Running $i"
    ($i && success $i) || failed $i
done

