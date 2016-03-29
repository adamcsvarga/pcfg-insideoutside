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