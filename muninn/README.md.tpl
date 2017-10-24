# muninn

<@generator-comment>

Muninn is a small personal project to maintain, backup, synchronize dotfiles and other config files for my projects, tools (e.g., sublime, zsh), or backup-solutions.
It is not meant to be a general tool for everyone. Inspired by many other such projects. Just for fun and hopefully I can learn something.

Is this safe to use? ¯\_(ツ)_/¯ (read: hell no)
Why? Cause I didn't make it safe to run yet....and inherently by design of the "build system" (imagine something macgyver built under influence) user mistakes can become very vicious.
Be happy you will never get to see the cluster...mess of this when it was just bash scripts :).

![Alt Text](http://www.sheawong.com/wp-content/uploads/2013/08/keephatin.gif)

## Requirements
Requires anaconda (can easily be removed if you feel like it) at the moment as its fully integrated into my daily work flows.
This repository contains a 

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
