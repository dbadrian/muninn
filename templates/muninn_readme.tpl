# muninn

<@generator-comment>

Muninn is a small personal project to maintain, backup, synchronize dotfiles and other config files for my projects, tools (e.g., sublime, zsh).
It is not meant to be a general tool for everyone. There exist many other [solutions](https://dotfiles.github.io/), so make sure to check them out!

It features its own package/build system, allows to establish dependencies, install arch dependencies etc.

However, this is only a very first prototype. I am currently rewriting most of the package system, implement some basic version tracking, drop the anaconda requirement as far as possible.
Remove the silly dialog dependency. I am also considering extracting the packages into their own (git-powered) repository.


<!s>TOC</!s>


## Requirements
Requires anaconda (can easily be removed if you feel like it) at the moment as its fully integrated into my daily work flows.
This repository contains a conda environment file which can be used to create the proper environment, or used as guidelines if you drop the anaconda depedency.

```
<!s>ANACONDA_REQUIREMENTS_FILE</!s>
```

## Supported Packges
Muninn currently has (very customized support) for the following packages:

<!s>SUPPORTED_PACKAGES_PLACEHOLDER</!s>

## Bootstrap
Well, that works for me...prolly won't for you :)

```bash
bash <(curl -s https://raw.githubusercontent.com/dbadrian/muninn/master/bootstrap.sh)
```

## Disclaimer
(yep...small print at the end)

Is this safe to use? ¯\_(ツ)_/¯ (read: probably not) Why? Well the "build system" allows for user mistakes to become very vicious (which is why you should always read, e.g., AUR PKGBUILD files).
Be happy you will never get to see the cluster...mess of this when it was just bash scripts :).

![Alt Text](http://www.sheawong.com/wp-content/uploads/2013/08/keephatin.gif)
