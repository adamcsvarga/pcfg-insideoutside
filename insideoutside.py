# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 11:04:23 2016

Program for unsupervised training of PCFG with the inside-outside algorithm.

Files required: pcfg.txt 
                -- file containing PCFG in CNF (if no probabilities
                are supplied, uniform distribution will be assumed), where 
                rules are of form
               A -> B C (p) OR
               Z -> x (p)      , where (p) is the optional probability
               
               terminals.txt and nonterminals.txt
               --- newline-separated list of terminals
               and nonterminals, respectively. The first nonterminal must be
               the initial S symbol
               
               If pcfg.txt is not present, from these latter two the program 
               will generate all possibilities as an initial set of rules
               
               training.txt -- a newline-separated list of training sentences
               
               pos.txt -- this is optional; it should contain unary rules
               (with our without probabilities) producing terminals. Used when
               pcfg.txt is not available, to avoid generating all possible
               unary rules
              
               
The final set of rules with probabilities will be produced in output.txt

@author: Ádám Varga
"""

import os.path, sys

def inside(words, unary_rules, binary_rules, nts):
    
    """ Calculates inside probbilities.
        Input: sentence as list of words, unary and binary rules, nonterminals
        Output: table of inside probabilities
    """    
    # initialize empty n*n matrix   
    inside_probs = []
    new = []
    for i in range(0, len(words)):
        for j in range(0, len(words)):
            new.append({})
        inside_probs.append(new)
        new = []
    
    # fill main diagonal with unary rule probabilities
    for i in range(0, len(words)):
        for unary_rule in unary_rules:
            if unary_rule[1] == words[i]:
                inside_probs[i][i][unary_rule[0]] = unary_rule[2]
                
    # fill diagonals starting from main diagonal, going towards upper
    # right-hand corner
    j = 1
    while j < len(words):
        for i in range(0, len(words)):
            if (i + j) < len(words):
                # check for all possible binary rules
                for nt_left in nts:
                    for nt_right in nts:
                        for binary_rule in binary_rules:
                            if binary_rule[1] == nt_left and binary_rule[2] \
                            == nt_right:
                                sum_prob = 0
                                # add up probabilities corresponding to the 
                                # rule
                                for d in range(i, i + j):
                                    if nt_left in inside_probs[i][d].keys() \
                                    and nt_right in \
                                    inside_probs[d + 1][i + j].keys():
                                        sum_prob += binary_rule[3] * \
                                        inside_probs[i][d][nt_left] * \
                                        inside_probs[d + 1][i +j][nt_right]
                                        
                                if sum_prob > 0:
                                    if binary_rule[0] in \
                                    inside_probs[i][i + j].keys():
                                        inside_probs[i][i + j][binary_rule[0]]\
                                        += sum_prob
                                    else:
                                        inside_probs[i][i + j][binary_rule[0]]\
                                        = sum_prob                            
        j += 1
        

    return inside_probs
        
def outside(words, inside_probs, binary_rules, nts):
    
    """ Calculates outside probbilities.
        Input: sentence as list of words, table of inside probabilities,
        binary rules, nonterminals
        Output: table of outside probabilities
    """    

    # initialize empty n*n matrix   
    outside_probs = []
    new = []
    for i in range(0, len(words)):
        for j in range(0, len(words)):
            new.append({})
        outside_probs.append(new)
        new = []
    
    # default upper right-hand corner rule
    outside_probs[0][len(words) - 1]['S'] = 1.0
    
    # fill diagonals starting from the upper right-hand corner, going towards
    # main diagonal
    j = len(words) - 1 
    while j >= 0:
        for i in range(0, len(words)):
            if (i + j) < len(words):
                # check rules to the right
                for nt_start in nts:
                    for nt_right in nts:
                        for binary_rule in binary_rules:
                            if binary_rule[0] == nt_start and binary_rule[2] \
                            == nt_right and binary_rule[1] != nt_right:
                                sum_prob = 0
                                # add up probabilities corresponding to the 
                                # rule
                                for e in range(i + j + 1, len(words)):
                                    if nt_start in outside_probs[i][e].keys() \
                                    and nt_right in \
                                    inside_probs[i + j + 1][e].keys():
                                        sum_prob += binary_rule[3] * \
                                        outside_probs[i][e][nt_start] * \
                                        inside_probs[i + j + 1][e][nt_right]
                                if sum_prob > 0:
                                    if binary_rule[1] in \
                                    outside_probs[i][i + j].keys():
                                        outside_probs[i][i + j] \
                                        [binary_rule[1]] += sum_prob
                                    else:
                                        outside_probs[i][i + j] \
                                        [binary_rule[1]] = sum_prob
                                        
                # check rules above
                for nt_start in nts:
                    for nt_left in nts:
                        for binary_rule in binary_rules:
                            if binary_rule[0] == nt_start and binary_rule[1] \
                            == nt_left:
                                sum_prob = 0
                                # add up probabilities corresponding to the 
                                # rule
                                for e in range(0, i):
                                    if nt_start in \
                                    outside_probs[e][i + j].keys() and \
                                    nt_left in inside_probs[e][i - 1].keys():
                                        sum_prob += binary_rule[3] * \
                                        outside_probs[e][i + j][nt_start] * \
                                        inside_probs[e][i - 1][nt_left]
                                if sum_prob > 0:
                                    if binary_rule[2] in \
                                    outside_probs[i][i + j].keys():
                                        outside_probs[i][i + j] \
                                        [binary_rule[2]] += sum_prob
                                    else:
                                        outside_probs[i][i + j] \
                                        [binary_rule[2]] = sum_prob                        
        
        j -= 1
        
    return outside_probs

def train_iterate(words, inside_probs, outside_probs, binary_rules):
    
    """Performs a training iteration based on inside-outside algorithm
       Input: sentence as list of words, table of insie and outside 
              probabilities, binary rules
       Output: updated set of binary rules
    """
    
    updated_rules = []

    for binary_rule in binary_rules:
        numerator = 0
        for i in range(0, len(words)):
            for j in range(i + 1, len(words)):
                if binary_rule[0] in outside_probs[i][j].keys():
                        inside_sum = 0
                        for d in range(i, j):
                            if binary_rule[1] in inside_probs[i][d].keys() \
                            and binary_rule[2] in inside_probs[d + 1][j].keys():
                                inside_sum += \
                                inside_probs[i][d][binary_rule[1]] * \
                                inside_probs[d + 1][j][binary_rule[2]]                                
                        outside_sum = outside_probs[i][j][binary_rule[0]] * \
                        binary_rule[3]
                        numerator += inside_sum * outside_sum
        
        denominator = 0
        for i in range(0, len(words)):
            for j in range(i, len(words)):
                if binary_rule[0] in outside_probs[i][j].keys() and \
                binary_rule[0] in inside_probs[i][j].keys():
                    denominator += outside_probs[i][j][binary_rule[0]] * \
                    inside_probs[i][j][binary_rule[0]] 
               
        try:
            new_prob = numerator / denominator
        except ZeroDivisionError:
            new_prob =  0.0
        
        if new_prob == 0.0:
            new_prob = binary_rule[-1]
        updated_rules.append((binary_rule[0], binary_rule[1], binary_rule[2],\
        new_prob))
        
    return updated_rules
    
def check_improvement(old_rules, new_rules):
    
    """Check changes between old and new set of rules.
       Input: two sets of binary rules
       Output: max difference between old and new probabilities"""
    
    max_improvement = 0

    for i in range(0, len(old_rules)):
        if abs(old_rules[i][-1] - new_rules[i][-1]) > max_improvement:
            max_improvement = abs(old_rules[i][-1] - new_rules[i][-1])
    
    return max_improvement
    
def print_rules(u_rules, b_rules, output_file):
    
    """Print rule to log files
    Input: unary and binary rules, output filename
    Output: ---"""
    
    # empty file    
    with open(output_file, 'w'):
        pass
    
    unary_rules, binary_rules = u_rules, b_rules
    
    #sort and print binary rules
    #binary_rules.sort(key=lambda x: x[-1])
    for binary_rule in binary_rules:
        if binary_rule[-1] >= 0.0:
            with open(output_file, 'a+') as o:
                o.write(' '.join([binary_rule[0], '->', binary_rule[1], \
                binary_rule[2], str(binary_rule[3]), '\n']))
            
    # print unary rules
    for unary_rule in unary_rules:
        if unary_rule[-1] >= 0.0:
            with open(output_file, 'a+') as o:
                o.write(' '.join([unary_rule[0], '->', str("'" + unary_rule[1] + "'"), \
                str(unary_rule[2]), '\n']))
    
def training(unary_rules, binary_rules, nts, i):
    
    """Performs inside-outside training on a set of training sentences
        and a set of PCFG rules
        Input: unary and binary rules and nonterminals; training.txt should
        exist in directory; i: postfix of output.txt
        Output: trained binary rules"""
        
    # read training file
    try:
        with open('training.txt') as f:
            sents = f.readlines()
    except IOError:
        print("Could not find file 'training.txt'")
        sys.exit(-1)
        
    # create log dir
    if not os.path.exists('log'):
        os.makedirs('log')
    
    iterations = 0
    ud_rules = binary_rules
    # perform first iteration of training
    #print('Original rules:\n', ud_rules)
    print('Training ' + str(i) + '...\n')
    for sent in sents:
        words = sent.split()

        inside_probs = inside(words, unary_rules, ud_rules, nts)
        outside_probs = outside(words, inside_probs, ud_rules, nts)
        ud_rules = train_iterate(words, inside_probs, outside_probs, \
        ud_rules)
        
        #print(inside_probs)
        #print(outside_probs)
        
    iterations += 1
    #print('Updated rules after iteration', iterations, '\n', ud_rules)
    print('Iteration', iterations)
    print_rules(unary_rules, binary_rules, 'log/' + str(iterations) + '.log')
    

    # train until change in rule probabilities is higher than 1e-04
    impr = check_improvement(binary_rules, ud_rules)
    threshold = 1e-04
    while impr >= threshold:
    #while iterations < 2:
        # get rid of zero probabilities
        temp_u = []
        for ud_rule in ud_rules:
            if ud_rule[-1] != 0.0:
                temp_u.append(ud_rule)
        ud_rules = temp_u
        binary_rules = ud_rules
        
        for sent in sents:
            words = sent.split()
            
            inside_probs = inside(words, unary_rules, ud_rules, nts)
            outside_probs = outside(words, inside_probs, ud_rules, nts)
            ud_rules = train_iterate(words, inside_probs, outside_probs, \
            ud_rules)
            
            #print(inside_probs)
            #print(outside_probs)
            
        iterations += 1
        #print('Updated rules after iteration', iterations, '\n', ud_rules)
        impr = check_improvement(binary_rules, ud_rules)
        print('Iteration', iterations, ";max improvment", impr)
        print_rules(unary_rules, binary_rules, 'log/' + str(iterations) + \
        '.log')
        
    print('Training terminated because of too small improvement')
    print_rules(unary_rules, binary_rules, 'output_' + str(i) + '.txt')
    return ud_rules
    
def check_prob(lines):
    """ Checks if lines read from file are probabilistic or not.
    Input: list of grammar rules as read from grammar file
    Output: boolean"""
    
    try:
        float(lines[0].split()[-1]) # check if last field is numerical
        if len(lines[0].split()) > 3:
            return True
        else:
            return False
    except ValueError:
        return False
        
def set_initial_probabilities(rules):
    """Sets initial probabilities for rules, assuming uniform distribution
    Input: list of rule tuples
    Output: list of rule tuples w\ uniform initial probabilities"""
    
    rule_set = set()
    for rule in rules:
        if rule[0] not in rule_set:
            rule_set.add(rule[0])
            count = 0
            for r in rules:
                if r[0] == rule[0]:
                    count += 1
                try:
                    prob = 1.0 / count
                except ZeroDivisionError:
                    prob = 0.0
                for i in range(0, len(rules)):
                    if rules[i][0] == rule[0]:
                        t = list(rules[i])
                        t[-1] = prob
                        rules[i] = tuple(t)
                            
    return rules
                              
    
def read_grammar():
    """Reads input files and builds the initial grammar.
       Output: set of unary and binary rules and set of nonterminals"""
       
    binary_rules, unary_rules, nts, ts = [], [], [], []
    
    try:
        with open('nonterminals.txt') as f:
            nlines = f.readlines()
    except IOError:
        print("File 'nonterminals.txt' could not be found")
        sys.exit(-1)
        
    try:
        with open('terminals.txt') as f:
            tlines = f.readlines()
    except IOError:
        pass
        
    # create list of nonterminals
    for nline in nlines:
            nts.append(nline.split('\n')[0])
    
    # grammar supplied
    if os.path.isfile('pcfg.txt'):
          with open('pcfg.txt') as f:
              lines = f.readlines()

          is_probabilistic = check_prob(lines)
          
          # pcfg
          if is_probabilistic:
              # check if all probabilities are provided
              for line in lines:
                  l = line.split(' ')
                  if not(len(l) == 5 or len(l) == 4):
                      print("'pcfg.txt' should contain probabilities for each \
                      rule or no probabilities at all.")
                      sys.exit(-1)
              for line in lines:
                  l = line.split(' ')
                  if len(l) == 5: # binary rule with prob
                      if float(l[4]) > 1.0:
                          print("Probabilities can't be higher than 1.0")
                          sys.exit(-1)
                      else:
                          binary_rules.append((l[0], l[2], l[3], float(l[4])))
                  elif len(l) == 4: # unary rule with prob
                      if float(l[3]) > 1.0:
                          print("Probabilities can't be higher than 1.0")
                          sys.exit(-1)
                      else:
                          unary_rules.append((l[0], l[2], float(l[3])))


          # cfg
          else:
              for line in lines:
                  #print(line)
                  l = line.split()
                  #print(l, len(l), l[0])
                  if len(l) >= 4: # binary rule
                      binary_rules.append((l[0], l[2], l[3], 0.0))
                  elif len(l) >= 3: # unary rule
                      unary_rules.append((l[0], l[2], 0.0))
          
              # set initial probabilities
              binary_rules = set_initial_probabilities(binary_rules)
              unary_rules = set_initial_probabilities(unary_rules)

              
    # no grammar supplied
    else:
        # create list of terminals
        for tline in tlines:
            ts.append(tline.split('\n')[0])
            
        # create all CNF binary rules
        try:
            prob = 1.0 / ((len(nts) - 1) * (len(nts) - 2))
        except ZeroDivisionError:
            prob = 0.0
        for nt_start in nts:
            for nt_left in nts:
                for nt_right in nts:
                        binary_rules.append((nt_start, nt_left, nt_right,\
                        prob))
        
        # look for unary rules        
        if os.path.exists('pos.txt'):
            with open('pos.txt') as f:
                plines = f.readlines()
            
            # check if probabilities are present            
            is_probabilistic = check_prob(plines)
            if is_probabilistic:
                for pline in plines:
                    if len(pline.split()) != 4:
                        #print(pline)
                        print("'pos.txt' should contain probabilities for each \
                        rule or no probabilities at all.")
                        sys.exit(-1)
                for pline in plines:
                    p = pline.split()
                    if float(p[3]) > 1.0:
                        print("Probabilities can't be higher than 1.0")
                        sys.exit(-1)
                    else:
                        unary_rules.append((p[0], p[2], float(p[3])))
            else:
               for pline in plines:
                   p = pline.split()
                   unary_rules.append((p[0], p[2], 0.0))
               unary_rules = set_initial_probabilities(unary_rules)
               
            # delete 'pos tags' producing nonterminals
            for unary_rule in unary_rules:
                for i in range(0, len(binary_rules)):
                    if binary_rules[i][0] == unary_rule[0]:
                       t = list(binary_rules[i])
                       t[-1] = 0.0
                       binary_rules[i] = tuple(t)
                    
        else:
            # create all teminal productions        
            try:
                prob = 1.0 / len(ts)
            except ZeroDivisionError:
                prob = 0.0
            for nt_start in nts:
                for t in ts:
                    unary_rules.append((nt_start, t, prob))
                    
    # get rid of zero probabilities
    temp_b = []
    for binary_rule in binary_rules:
        if binary_rule[-1] != 0.0:
            temp_b.append(binary_rule)
    binary_rules = temp_b
    
    return unary_rules, binary_rules, nts
if __name__ == '__main__':
    
    unary_rules, binary_rules, nts = read_grammar()
    ud_rules = training(unary_rules, binary_rules, nts, 0)
    