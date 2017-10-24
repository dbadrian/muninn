# muninn

*Attention: This README was automatically generated at 2017-10-24 17:13.*

Muninn is a small personal project to maintain, backup, synchronize dotfiles and other config files for my projects, tools (e.g., sublime, zsh).
It is not meant to be a general tool for everyone. Inspired by many other such projects. Just for fun and hopefully I can learn something.

It features its own package/build system, allows to establish dependencies, install arch dependencies etc.


Table of Contents
=================

   * [muninn](#muninn)
      * [Requirements](#requirements)
      * [Supported Packges](#supported-packges)
      * [Bootstrap](#bootstrap)
      * [Disclaimer](#disclaimer)

Created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)



## Requirements
Requires anaconda (can easily be removed if you feel like it) at the moment as its fully integrated into my daily work flows.
This repository contains a conda environment file which can be used to create the proper environment, or used as guidelines if you drop the anaconda depedency.

```
name: muninn
channels:
- defaults
dependencies:
- openssl=1.0.2k=1
- pip=9.0.1=py36_1
- python=3.6.0=0
- readline=6.2=2
- setuptools=27.2.0=py36_0
- sqlite=3.13.0=0
- tk=8.5.18=0
- wheel=0.29.0=py36_0
- xz=5.2.2=1
- zlib=1.2.8=3
- pip:
  - pythondialog==3.4.0


```

## Supported Packges
Muninn currently has (very customized support) for the following packages:

Package Name | Version | Description | Dependencies Muninn
--- | --- | --- | --- 
zsh | 0.1 | ZSH Config Installer | *None*
st3 | 0.2 | Sublime Text 3 - User Configs/Plugins | *None*
system_setup | 0.1 | ArchLinux System-Configuration | *None*
user_bin | 0.1 | Sync User Bin scripts | *None*
terminator | 0.1 | Terminator Configuration | *None*
tensorflow | 0.1 | Tensorflow compiled from source | *None*
archpackages | 0.1 | Arch Linux Packages Installer | system_setup
git | 0.1 | Git Config Installer | *None*


## Bootstrap
Well, that works for me...prolly won't for you :)

```bash
bash <(curl -s https://raw.githubusercontent.com/dbadrian/muninn/master/bootstrap.sh)
```

## Disclaimer
(yep...small print at the end)
Is this safe to use? ¯\_(ツ)_/¯ (read: hell no)
Why? Cause I didn't make it safe to run yet....and inherently by design of the "build system" (imagine something macgyver built under influence) user mistakes can become very vicious.
Be happy you will never get to see the cluster...mess of this when it was just bash scripts :).

![Alt Text](http://www.sheawong.com/wp-content/uploads/2013/08/keephatin.gif)
