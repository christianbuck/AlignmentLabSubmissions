#!/usr/bin/env python

import sys
import os
import time
import subprocess
import csv

class Scorer(object):

    def __init__(self, root_dir, grader, gold_data):
        self.grader = grader
        self.gold_data = gold_data
        self.colnames = ['user', 'date', 'precision', 'recall', 'aer']
        self.submissions = []
        for directory, dirnames, filenames in os.walk(root_dir):
            if 'alignment.sorted' in filenames and 'alignment' in filenames:
                alignment_file = os.path.join(directory, 'alignment')
                alignment_file = os.path.abspath(alignment_file)
                sorted_alignment_file = "%s.sorted" %alignment_file
                file_date = time.ctime(os.path.getmtime(alignment_file))
                user_name = os.path.split(directory)[-1]
                result = self._score(sorted_alignment_file)
                self.submissions.append( (user_name,
                                          file_date,
                                          result[0], result[1], result[2]) )

    def _score(self, filename):
        "score one alignment file, return (precision, recall, AER)"
        cmd = "%s -d %s -n 0" %(self.grader, self.gold_data)
        sys.stderr.write(cmd + "\n")
        process = subprocess.Popen(cmd.split(),
                                   shell=False,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out,err = process.communicate(open(filename).read())
        map(sys.stderr.write, err)
        map(sys.stderr.write, out)
        precision, recall, aer = 0.0, 0.0, 1.0
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
                self.html.append('\t<tbody>')
            else:
                self.html.append('\t<tr>')
                for val in line:
                    self.html.append("\t\t<td>%s</td>" %val)
                self.html.append('\t</tr>')

        self.html.append('\t</tbody>')
        self.html.append('</table>')

    def __str__(self):
        return "\n".join(self.html)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help="root directory, containing submissions")
    parser.add_argument('grader', help="grading script")
    parser.add_argument('gold', help="location of aligned data")
    parser.add_argument('template', help="HTML template file for leaderboad")
    args = parser.parse_args(sys.argv[1:])

    scorer = Scorer(args.root, args.grader, args.gold)
    scorer.write_csv('results.csv')

    htmltable = str(CSV2HTML('results.csv'))

    html = open(args.template).read()
    sys.stdout.write(html.replace("TABLEGOESHERE", htmltable))

    #for linenr, line in enumerate(sys.stdin):
    #    line = line.strip().split()
