# muninn

Muninn is a small personal project to maintain, backup, synchronize dotfiles and other config files for my projects, tools (e.g., sublime, zsh).
It is not meant to be a general tool for everyone. There exist many other [solutions](https://dotfiles.github.io/), so make sure to check them out!

**ATTENTION**: Right now, this tool is in very early development, and while I plan to follow [semantic versioning](semver.org) eventually, I am testing out different things atm and often breaking the API (if you wanna call it an API). It's my playground until v1!

Table of Contents
=================

   * [muninn](#muninn)
      * [Requirements](#requirements)
      * [Supported Packges](#supported-packges)
      * [Bootstrap](#bootstrap)
      * [Disclaimer](#disclaimer)

Created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)

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
