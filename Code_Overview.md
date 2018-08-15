## Entry point
`single_train.py`
* Creates experiment, which parses command-line arguments
* Runs experiment with `experiment.train_manager.train(experiment_arguments)`
* Computes validation with  `valid_metrics = experiment.train_manager.validate(experiment_arguments)`

Continuous flag explanation:

> Because we do this architecture search we want this thing to be fast, so we only validate at the end. The end is dependent on budget type (minutes, iterations or epochs) and budget value (for example 5 minutes). Single train script is used to retrain already found models or to do manual experiments. In manual experiments you might want to validate multiple times and train forever
So continuous flag trains forever and validates every budget units or when user presses ctrl+c once ( "ctrl+c validation request " is a nice feature, but Im not sure if it works 100% times) and then goes back to training


## Experiment 
`experiment.py`

* Reads and stores all data necessary for running experiment
* Makes use of the `ExperimentArguments` class
* lookup of given model name etc. is based on direct mapping of given name to module names in specific py-files (e.g.
`model.__init__.py` for model name)
* Right now only one fixed trainer (`from src.deep_learning.pytorch.model_trainer import ModelTrainer as TrainerClass
`), meant to be extendable, see below
* Makes two parsing phases, First phase to get classes. Second to get all arguments for all classes
  * First phase creates `ExperimentArguments` with section 'experiments' and does not force usage of all
  CLI args
    * Adds arguments from the experiment class, such as model class name etc + ini file name
    to the arguments to parse
    * Gets inifile from `args, unknown_args = self._ini_file_parser.parse_known_args();
    ini_file = args.ini_file`
    * Uses inifile to update defaults of parser
    
Option to extend code to create different trainers:
>  yes additional model trainers might be implemented, for example cnn model trainer does not require to store states for sequence chunks, thus can potentially run faster




## ExperimentArguments
`experiment_arguments.py`
* Uses `argparse` to parse command line arguments and `configparser` to parse inifile
* First gets ini file from command line arguments using `argparse` and `parse_known_args`
  * `args, unknown_args = self._ini_file_parser.parse_known_args();
    ini_file = args.ini_file`
* Uses inifile values to update defaults of argparse, so ini file values will be overwritten
by command line arguments, only used if command line argument not present
* overwrites `getattr/setattr/setitem/getitem` to allow access of all parameters by . or []
  * not clear if this is used anywhere
* Can supply sections to limit what is parsed from ini-file

Original explanation:

```python

class ExperimentArguments(object):
    """
    Class that extracts arguments declared by different classes used for the experiment run.
    Priority in which arguments are assigned, from the lowest:
    1. Default parameters specified in class declaration.
    2. Parameters provided by the user in the .ini file
    3. Parameters provided by the user as CLI arguments
    4. Parameters specified by the Architecture Optimizer.

    Parsing arguments requires couple stages and might look complicated.
    This class makes it possible to achieve our goals:
        - First we need to extract the location of .ini file from the CLI arguments
        - Using .ini file we need to overwrite default script arguments
        - Based on a subset of script arguments we determine which subclasses are used for the experiment.
          For example which DataReader is used.
        - Then we add arguments required by those classes to the parser and again process all CLI arguments
          asserting that all options were recognized and are correct.
```

Note that list item 3 from the lower list actually happens from "outside" through calls by the
Experiment class inside the constructior of the experiment class.

Next: bayesian_optimization.py / submit/bayesian_optimization_mnist/submit_grid.sh






