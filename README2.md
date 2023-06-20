# Tributaries 

A library for mass-deploying [UnifiedML](github.com/agi-init/UnifiedML) apps on [slurm]()-enabled remote servers.

```console
pip install tributaries-ml
```

Simply create and run a python file with a server configuration like this one:

```python
# MyServer.py
from tributaries import my_server


@my_server(sweep='path/to/my/sweep.py')
def main():
    ...
    return server, username, password, func, app_name_paths


if __name__ == '__main__':
    main()
```

That method must return the ```server```, ```username```, ```password```, any additional functions that need to be run (e.g. [connecting to a VPN]()), ... and dictionary of names and paths to any UnifiedML apps you'd like to use.

Note the decorator accepts a sweep file path for picking out the hyperparams to launch the experiments with.

You can define sweep files like this one:

```python
# path/to/my/sweep.py
from tributaries import my_sweep

my_sweep.hyperparams.extend(['...', '...'])  # List of hyperparams
my_sweep.app = 'UnifiedML'
...
```

We've provided plenty [examples]() to make it easy.

You can also pass in the sweep file path via command line with the ```sweep=path.to.my.sweep``` flag.

That's it. Running it will launch the experiments on your remote server. Add the ```plot=true``` or ```plot_sweep=path.to.my.sweep``` flag to instead download plots and checkpoints back down to your local machine.

#### Launching

```console
python MyServer.py sweep=path.to.my.sweep
```

#### Plotting

```console
python MyServer.py plot_sweep=path.to.my.sweep
```

Note: these hyperparams are already fully part of [UnifiedML](github.com/agi-init/UnifiedML), together with the, for example, ```my_server=MyServer.main``` server-path flag.

#

[Licensed under the MIT license.](MIT_LICENSE)
