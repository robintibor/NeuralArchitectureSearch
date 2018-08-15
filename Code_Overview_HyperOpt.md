## Entry point
`bayesian_optimization.py`
* creates Experiment
* Initializes `BayesianOptimizer` with arguments parsed by `ExperimentArguments`
class `BayesianOptimizer(**experiment.experiment_arguments.get_arguments())`
* 

## BayesianOptimizer
`src/hpbandster/bayesian_optimizer.py`

* subclasses HPBandster Master class
* runs the `run` method of HPBandster master class in a thread 
 `thread = Thread(target=self.run, name='Optimizer thread',
                        kwargs={'n_iterations': self.n_iterations});
        thread.daemon = True;
        thread.start()`
* **kwargs in constructor supplied to ConfigGenerator 
`ConfigGenerator(self.config_space, working_dir=working_dir, **kwargs)`

## ConfigGenerator
`src/hpbandster/config_generator.py`
* Uses configspace internally to describe search space
* *Somehow needs special back-and-forth conversion for Ordinal Hyperparameters using 
internal `OrdinalChecker` class
  * Converts first to floating between 0 and 1 `v = array[i]; n_v = (v + 0.5) / s`
  * *Unclear: guaranteed that ordinal values always start at 0?
  Or not relevant since backconversion does not depend on it?*
  * `n_v = v*s - 0.5` -> should be correct inversion in any case, independent of
  which is starting value
  * *Still,what is reasoning for this back-and-forth?*
  * *How is this even possible, since there is an exact back-and-forth conversion,
  if the values are integers before, they should still be integers, like 3.0,
  not 3.5 `# For example if s is 4 and v in 1 then 3.5 would round to 4 but we want it to round to 3.`
  * *Is it because BOHP internally treats these values as float, then samples from
  floating range? In that case, is it problematic that many values are mapped to the same*
   
## Worker
* Runs the actual training and validation
`train_metrics = self.train_manager.train(experiment_args);
valid_metrics = self.train_manager.validate(experiment_args)`

