#!/usr/bin/env python
import optparse
import sys
from collections import defaultdict

optparser = optparse.OptionParser()
optparser.add_option("-d", "--data", dest="train", default="data/hansards", help="Data filename prefix (default=data)")
optparser.add_option("-e", "--english", dest="english", default="e", help="Suffix of English filename (default=e)")
optparser.add_option("-f", "--french", dest="french", default="f", help="Suffix of French filename (default=f)")
optparser.add_option("-t", "--threshold", dest="threshold", default=0.5, type="float", help="Threshold for aligning with Dice's coefficient (default=0.5)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
(opts, _) = optparser.parse_args()
f_data = "%s.%s" % (opts.train, opts.french)
e_data = "%s.%s" % (opts.train, opts.english)

sys.stderr.write("Training with the joint model...")
bitext = [[sentence.strip().split() for sentence in pair] for pair in zip(open(f_data), open(e_data))[:opts.num_sents]]
f_count = defaultdict(int)
e_count = defaultdict(int)
fe_count = defaultdict(int)
fe_prob = defaultdict(float)
ef_count = defaultdict(int)
ef_prob = defaultdict(float)
alignments = defaultdict(int)

def writeAlignments(): 
  for (f, e) in bitext:
    for (i, f_i) in enumerate(f): 
      max = 0
      index = -1
      for (j, e_j) in enumerate(e):
      	 p1 = fe_prob[(f_i,e_j)]
	 p2 = ef_prob[(e_j,f_i)]
	 p3 = 
	 score = p1*p2
         if score > max:
          max = score
          index = j
      for (j, e_j) in enumerate(e):
	alignments[i] = index
        sys.stdout.write("%i-%i " % (i,index))
    sys.stdout.write("\n")

def learnEnglish(iterations):
  #initialize Theta 0 with uniform distribution
  for (n,(f,e)) in enumerate(bitext):
    for f_i in set(f):
      for e_j in set(e):
        p = (1/float(len(e)))
        fe_prob[(f_i,e_j)] = p
    if n % 500 == 0:
      sys.stderr.write(".")

  k = 0
  while k < iterations:
    k += 1
    
    #initialize all counts to 0
    for (n, (f, e)) in enumerate(bitext):
      for f_i in set(f):
        f_count[f_i] = 0
        for e_j in set(e):
          fe_count[(f_i,e_j)] = 0
      for e_j in set(e):
        e_count[e_j] = 0
      if n % 500 == 0:
        sys.stderr.write(".")
    
    #compute expected counts
    for (n, (f,e)) in enumerate(bitext):
      for f_i in set(f):
        Z = 0
        for e_j in set(e):
          Z += fe_prob[(f_i,e_j)]
        for e_j in set(e):
          c = fe_prob[(f_i,e_j)] / Z
          fe_count[(f_i,e_j)] += c
          e_count[e_j] += c
    for (f,e) in fe_count:
      fe_prob[(f,e)] = fe_count[(f,e)] / e_count[e]

def learnFrench(iterations):
  #initialize Theta 0 with uniform distribution
  for (n,(f,e)) in enumerate(bitext):
    for e_j in set(e):
      for f_i in set(f):
        p = (1/float(len(f)))
        ef_prob[(e_j, f_i)] = p
    if n % 500 == 0:
      sys.stderr.write(".")

  k = 0
  while k < iterations:
    k += 1
    
    #initialize all counts to 0
    for (n, (f, e)) in enumerate(bitext):
      for e_j in set(e):
        e_count[e_j] = 0
        for f_i in set(f):
          ef_count[(e_j,f_i)] = 0
      for f_i in set(f):
        f_count[f_i] = 0
      if n % 500 == 0:
        sys.stderr.write(".")
    
    #compute expected counts
    for (n, (f,e)) in enumerate(bitext):
      for e_j in set(e):
        Z = 0
        for f_i in set(f):
          Z += ef_prob[(e_j, f_i)]
        for f_i in set(f):
          c = ef_prob[(e_j, f_i)] / Z
          ef_count[(e_j, f_i)] += c
          f_count[f_i] += c
    for (e,f) in ef_count:
      ef_prob[(e,f)] = ef_count[(e,f)] / f_count[f]

learnEnglish(5)
learnFrench(5)
writeAlignments()