# Entry point
`single_train.py`
* Creates experiment, which parses command-line arguments
* Runs experiment with `experiment.train_manager.train(experiment_arguments)`
* Computes validation with  `valid_metrics = experiment.train_manager.validate(experiment_arguments)`
* *For some reason, has a continuous flag, where it runs train and valid in loop. Epochs?*



## Experiment 
`experiment.py`

* Reads and stores all data necessary for running experiment
* Makes use of the `ExperimentArguments` class
* lookup of given model name etc. is based on direct mapping of given name to module names in specific py-files (e.g.
`model.__init__.py` for model name)
* *Seems there is only one fixed trainer (`from src.deep_learning.pytorch.model_trainer import ModelTrainer as TrainerClass
`), maybe there were meant to be several options?
* *makes two parsing phases, first phase to get classes? second to get all arguments for all classes?*

