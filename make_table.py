#!/usr/bin/env python

import sys
from collections import defaultdict
from itertools import imap, izip
import os
import time
import subprocess
import csv

class Scorer(object):

    def __init__(self, root_dir, grader='./grade'):
        self.grader = grader
        self.colnames = ['user', 'date', 'precision', 'recall', 'aer']
        self.submissions = []
        for directory, dirnames, filenames in os.walk(root_dir):
            if 'alignment' in filenames:
                alignment_file = os.path.join(directory, 'alignment')
                alignment_file = os.path.abspath(alignment_file)
                file_date = time.ctime(os.path.getmtime(alignment_file))
                user_name = os.path.split(directory)[-1]
                result = self._score(alignment_file)
                self.submissions.append( (user_name,
                                          file_date,
                                          result[0], result[1], result[2]) )

    def _score(self, filename):
        "score one alignment file, return (precision, recall, AER)"
        process = subprocess.Popen(self.grader.split(),
                                   shell=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        sys.stderr.write("%s %s\n" %(self.grader, filename))
        out = process.communicate(open(filename).read())[0]
        precision, recall, aer = 0.0, 0.0, 0.0
        #look for output like this:
        #    Precision = 0.235149
        #    Recall = 0.594675
        #    AER = 0.686452
        for line in out.split('\n')[-4:]:
            if line.startswith('Precision = '):
                precision = float(line.split()[-1])
            elif line.startswith('Recall = '):
                recall = float(line.split()[-1])
            elif line.startswith('AER = '):
                aer = float(line.split()[-1])
        return (precision, recall, aer)

    def write_csv(self, filename):
        with open(filename, 'w') as fp:
            csv_writer = csv.writer(fp, delimiter=',')
            csv_writer.writerow(self.colnames)
            csv_writer.writerows(self.submissions)

class CSV2HTML(object):
    def __init__(self, filename):
        self.html = []
        self.html.append('<table cellspacing="1" class="tablesorter">')

        for linenr, line in enumerate(csv.reader(open(filename))):

            if linenr == 0:
                self.html.append('\t<thead>')
                self.html.append('\t<tr>')
                for val in line:
                    self.html.append("\t\t<th>%s</th>" %val)
                self.html.append('\t</tr>')
                self.html.append('\t</thead>')
            else:
                self.html.append('\t<tr>')
                for val in line:
                    self.html.append("\t\t<td>%s</td>" %val)
                self.html.append('\t</tr>')

        self.html.append('</table>')

    def __str__(self):
        return "\n".join(self.html)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help="root directory, containing submissions")
    parser.add_argument('grader', help="root directory, containing submissions")
    parser.add_argument('template', help="HTML template file for leaderboad")
    args = parser.parse_args(sys.argv[1:])

    scorer = Scorer(args.root)
    scorer.write_csv('results.csv')

    htmltable = str(CSV2HTML('results.csv'))

    html = open(args.template).read()
    sys.stdout.write(html.replace("TABLEGOESHERE", htmltable))

    #for linenr, line in enumerate(sys.stdin):
    #    line = line.strip().split()
