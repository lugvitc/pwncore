<!-- TODO, write more about tox and poetry later -->

# What you need.

Install tox as mentioned [here](https://tox.wiki/en/latest/installation.html)

Then install poetry as detailed [here](https://python-poetry.org/docs/#installation)



## Adding a dependency
Warning, never use pip to add a dependency. Nasty things are gonna
happen if you ignore that advice.

```
$ poetry add yourdep yourdep2 ...
```

The command may take time due to dependency resolution sometimes, but
if it exceeds 5 minutes it is abnormal. Usually it should be done before you notice.

## Spawning a shell in the environment

```
$ poetry shell
```

You can learn more at https://python-poetry.org/docs/cli/

## Running tests

```
$ tox r
```