# Inside-Outside PCFG Training Tool
## Created by Adam Varga, 2016

This tool can be used for training the probabilities of a Context-Free Grammar based on a corpus using the Inside-Outside Algorithm. The tool also allows for
completely unsupervised grammar induction as well as for performing training with different levels of a priori knowledge.

A toy grammar is included as an example.

1. Using the program
   Running the program requires Python 3.4. The following files should be present for succesful execution:
   * `pcfg.txt` (optional) - If a set of Chomsky Normal Form (CNF) (P)CFG rules exist that is used for initializing the learning process, it should be 
   supplied in this file. It should contain a newline-separated set of rules in the format
   
   `A -> B C probability`
   
   `D -> a probability`
   
   `A`, `B`, `C`, and `D` stand for nonterminals, and `a` is for terminals. The probabilities are optional floats; when present, they are used for initializing rule probabilities, otherwise an initial uniform distribution is assumed.
   (Note: probabilities must either be present or absent for all the lines of rules). The initial symbol is assumed to be the symbol `S`.
   
   * `terminals.txt` - Must be present when `pcfg.txt` does not exist; it should contain a newline-separated list of terminals.
   
   * `nonterminals.txt` - A newline-separated list of nonterminals. If `pcfg.txt` is not present, based on these latter two files, the program generates all
   possible production rules as an initial PCFG.
   
   * `training.txt` - A newline-separated list of training sentences.
   
   * `pos.txt` (optional) - This optional file should contain unary rules producing terminals (i. e. POS-tags of words). It is used when `pcfg.txt` is
   not available to avoid creating all possible unary productions. The format should follow the format of unary rules in `pcfg.txt`.
   
2. Output files
   * `log/` - A folder containing log files for each training iteration. Each log file contains the PCFG rule-set at the current iteration.
   * `output.txt` - The final set of PCFG rules.
   
3. Steps executed by the program:
   For more detailed description of the actual methods of calculation, please refer to *[Manning and Schütze: Foundations of Statistical Natural Language Processing](http://nlp.stanford.edu/fsnlp/)*
   1. 
      If an initial (P)CFG was supplied, the grammar is read from the corresponding file. If the initial grammar is non-probabilistic, probabilities are initialized as a uniform distribution. If no grammar is supplied, as a first step the program generates all possible CNF productions based on the list of terminals and non-terminals and assigns uniform probabilities to them in the above-mentioned way. Optionally one can provide the list of unary productions, i. e. a POS-tag for each occurring word. This way the system avoids generating all possible unary rules and reads them from `pos.txt` instead. If probabilities are not supplied in that file, a uniform probability distribution is assumed. Finally, as a cleaning-up step, the program deletes all rules that might have zero probability to avoid redundancy in calculations.
   2.
      After reading the training sentences and creating the initial PCFG, the actual training process starts. In each iteration of training, the *inside probabilities* are first calculated.  For practical reasons, zero inside probabilities are omitted from the calculation. As a second step, the calculation of the *outside probabilities* follows. After both matrices have been calculated, the system updates the binary production rules of the PCFG based on the Expectation Maximization (EM) method applied for this particular case. It can be proven that updating the rules in an iterative fashion the model converges to a local maximum. In this case, after each pass on the set of training sentences the difference between the previous and updated rule probabilities is checked; if the difference is less than 0.0001, the training is terminated to avoid unnecessarily long training times or oscillation of probabilities when being stuck in a local maximum (this threshold can be adjusted with the `threshold` parameter of the `training()` function). 
   3.
      After the termination of the training, the final set of PCFG rules are saved into the output file.	