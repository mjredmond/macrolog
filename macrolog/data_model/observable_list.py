"""
BSD 3-Clause License

Copyright (c) 2017, Michael James Redmond, Jr.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from __future__ import print_function, absolute_import
from six import iteritems, iterkeys, itervalues
from six.moves import range

from ._observables import register_observable, get_observable, is_observable

simple_types = {int, float, str, bytes}


@register_observable
class ObservableList(list):

    is_observable = True

    types = (list,)

    def __init__(self, *args, **kwargs):
        super(ObservableList, self).__init__(*args, **kwargs)

        for i in range(len(self)):
            self[i] = self[i]

    def append(self, item):
        if type(item) not in simple_types:
            item = get_observable(item)
            item.parent = self
            item.parent_index = len(self)

        return super(ObservableList, self).append(item)

    def pop(self, index=-1):
        item = super(ObservableList, self).pop(index)
        if is_observable(item):
            item.parent = None
            item.parent_index = None
        return item

    def reverse(self):
        super(ObservableList, self).reverse()
        self._update()
        return self

    def sort(self, *, key, reverse):
        super(ObservableList, self).sort(key, reverse)
        self._update()
        return self

    def __setitem__(self, key, value):
        if type(value) not in simple_types:
            if not is_observable(value):
                value = get_observable(value)
            value.parent = self
            value.parent_index = key
        return super(ObservableList, self).__setitem__(key, value)

    def __delitem__(self, key):
        if isinstance(key, slice):
            step = key.step
            if step is None:
                step = 1
            deleted_items = [self[i] for i in range(key.start, key.stop, step)]
        else:
            deleted_items = [self[key]]

        for item in deleted_items:
            if is_observable(item):
                item.parent = None
                item.parent_index = None

        return super(ObservableList, self).__delitem__(key)

    def _update(self):
        for i in range(len(self)):
            item = self[i]
            if is_observable(item):
                item.parent = self
                item.parent_index = i


if __name__ == '__main__':
    a = ObservableList([1, 2, 3, 4])
    print(a)