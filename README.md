# Sharemind
A demonstation of the core functionality of the Sharemind multiparty computation system for secure data mining.

This should be used for demonstration or educational purposes only, and not for any secure computation.
See the "Sharemind" academic paper for more details:

* D. Bogdanov, S. Laur and J. Willemson, "Sharemind: A framework for fast privacy-preserving computations," in Computer Security-ESORICS 2008: 13th European Symposium on Research in Computer Security, Málaga, Spain, October 6-8, 2008. Proceedings 13, 2008.

Written by Ofek Zeevi.

---

## Installation & Usage Guide

### If you have poetry installed:
Simply run - 
```
poetry install
poetry shell
```

### If you don't have / don't want to use poetry:
Install the `.tar.gz` or `wheel` from the `dist` folder (using `pip`).
E.g. run -
```
pip install dist/sharemind-0.1.0-py3-none-any.whl
```
to install the `wheel` in your local python environment.

### How to use
To use the package, you can run -
```
sharemind --help
```
or
```
python -m sharemind --help
```
and you'll see a help page with all the supported commands.

---

**Note:** This program was written in and tested on Python 3.12. 
It should work on older Python 3 versions, but that is not guaranteed.
