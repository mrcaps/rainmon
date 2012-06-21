#!/opt/local/bin/python2.6

#Copyright (c) 2012, Carnegie Mellon University.
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#1. Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#3. Neither the name of the University nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.

from math import *
from copy import *
# import pywt

# Shifted Wavelet Tree class
class Swt:
    # Construct a Shifted Wavelet Tree out of given data
    def __init__(self, data):
        self.num_levels = int(log(len(data), 2));
        # Take the first power-of-two elements in given data
        self.n = 2 ** self.num_levels;
        # self.coeffs = pywt.wavedec(data, 'haar', level=self.num_levels);

        # Tree contains:
        # level 0 (= original data), level 1, level 2, ..., level n
        self.tree = [None] * (self.num_levels + 1);

        self.tree[0] = data[0 : self.n];
        b = copy(self.tree[0]);

        for level in range(1, self.num_levels + 1):
            # Number of entries at level i including over-lapping windows
            num_entries = self.n / (2 ** (level - 1)) - 1;
            self.tree[level] = [None] * num_entries;

            for i in range(0, num_entries):
                self.tree[level][i] = b[i] + b[i + 1];

            for i in range(0, num_entries / 2 + 1):
                b[i] = self.tree[level][2 * i];

    # Update tree
    def update(self, data):
        return;

    # Burst detection:
    #    w is window size
    # Returns array containing positions at which bursty windows start
    # Follows algorithm presented in work by Zhu and Shasha, 2003.
    def detect_burst(self, w, threshold):
        ret = [];

        i = int(ceil(log(w, 2)));

        for j in range(0, len(self.tree[i + 1])):
            if self.tree[i + 1][j] > threshold:
                for c in range(j * (2 ** i), (j + 1) * (2 ** i) + 1):  # Notice + 1 for the right boundary
                    y = sum(self.tree[0][c : c + (2 ** i)]);

                    if y > threshold:
                        # Detailed search in tree[0][c : c + (2 ** i)]
                        for pos in range(c, c + (2 ** i) - w + 1):
                            z = sum(self.tree[0][pos : pos + w]);

                            if z > threshold:
                                ret.append(pos);

        ret = sorted(list(set(ret))); # Remove duplicated results

        return ret;

    # Somewhat improved version of detect_burst()
    def detect_burst_alt(self, w, threshold):
        ret = [];
        i = int(ceil(log(w, 2)));

        marker = -1; # Remember how far into the array we have done detailed search

        for j in range(0, len(self.tree[i + 1])):
            if self.tree[i + 1][j] > threshold:

                candidates = self.sliding_window_search(j * (2 ** i), (j + 2) * (2 ** i), (2 ** i), threshold);

                for start in candidates:
                    end = start + (2 ** i);
                    start = max(start, marker + 1); # Skip if appropriate
                    marker = end - w; # Update marker

                    for elm in self.sliding_window_search(start, end, w, threshold):
                        ret.append(elm);

        return ret;

    # Check sliding windows of size w within [start, end)
    def sliding_window_search(self, start, end, w, threshold):
        ret = [];

        if end - start < w:
            return ret;

        aggregate = sum(self.tree[0][start : start + w]);

        if aggregate > threshold:
            ret.append(start);

        for pos in range(start + 1, end - w + 1):
            # Move sliding window by one one position
            aggregate += (self.tree[0][pos + w - 1] - self.tree[0][pos - 1]);

            if aggregate > threshold:
                ret.append(pos);

        return ret;
