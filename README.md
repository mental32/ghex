# ghex
## A command line GitHub explorer tool

> *Its like [find(1)](http://man7.org/linux/man-pages/man1/find.1.html) but for [GitHub](https://github.com/)*

## Index

 - [Index](#Index)
 - [Brief](#Brief)
 - [Examples](#Examples)
   - [Number of repositoreis using Python](#Number-of-repositories-using-Python)
   - [Issues open over all repositories](#Issues-open-over-all-repositories)
   - [A specific repository as JSON](#A-specific-repository-as-JSON)

## Brief

I use GitHub quite regularly. On occasion I've needed to work with data or
metadata on GitHub or a repository hosted there, I've made this tool to make
that task a lot easier.

## Examples

### Number of repositories using Python

 - `ghex mental32 --type r --language Python | wc -l`

### Issues open over all repositories

 - `ghex mental32 --type r --has-issues`

### A specific repository as JSON

 - `ghex mental32/ghex`
