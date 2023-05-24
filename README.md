# Tributaries

A library for managing [UnifiedML](github.com/agi-init/UnifiedML) apps on remote servers that support SLURM job scheduling.

## 5 setup steps

Most of them involve just getting this repo under your GitHub account.

**Step 1.** Make this repo into a personal GitHub repo under your GitHub account.

**Step 2.** Clone a copy of it (your version) on your local machine and remote machines.

**Step 3.** Make sure your local and remote machines both have [UnifiedML](github.com/agi-init/UnifiedML) cloned with corresponding UnifiedML-installed [conda]() environments that can be activated.

**Step 4.** Make sure both your local and remote machines have ssh keys registered with GitHub such that push/pulls can be done without needing password authentication. See GitHub's ssh-key-generating [docs](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) for step-by-step instructions on how to do this. This is necessary so that your version of this repo can stay automatically synced across your local and remote clones.
* Or make your version of the repo public.

**Step 5.** On your local machine, modify your [```Central.py```](Central.py) file with the correct info/credentials of your remote server(s).

## Defining experiment sweeps

Create sweep files like [this one](Sweeps/XRD/Paper1.py), where you can define what set of experiments to launch and how to plot them.

## Selecting a sweep

Select the sweep file you want to launch/plot by pointing to it with the [```sweep_path=```](Central.py#L14) variable at the top of [```Central.py```](Central.py#L14).

## Automatic launching from your local machine

Launch selected sweeps remotely via ```python LaunchRemote.py```.

## Automatic plotting from your local machine

Plot selected sweeps locally via ```python PlotRemote.py```.

#

[Licensed under the MIT license.](MIT_LICENSE)
