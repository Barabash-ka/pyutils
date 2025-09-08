# Working with this repo
> reverse chronological order

## 2025-01-26
- returned to and checked the source repo did not change
- moved out of the /d/github_ibm
- used as a basis for learning gradio following the official tutorial
```sh
 4640  2025-01-26 09:09:00 - cd gradio_code_helper/
 4652  2025-01-26 19:32:49 - rm -fr .wenv/  # was disfunctional but not it is not the same one that was created on 2024-12-04
 4660  2025-01-26 19:34:49 - python3.12 -m venv .venv 
 4663  2025-01-26 19:35:27 - . .venv/Scripts/activate
 4670  2025-01-26 19:36:17 - pip install -r requirements.txt
 4671  2025-01-26 19:37:23 - python3.12.exe -m pip install --upgrade pip
```

## 2024-12-04
- discovered on inm github `https://github.ibm.com/girijesh/code-helper`
- tried and found working :-)
```sh
15:10:21 /d/github_ibm $ git clone https://github.ibm.com/girijesh/code-helper
  Cloning into 'code-helper'...
  remote: Enumerating objects: 12, done.
  remote: Counting objects: 100% (12/12), done.
  remote: Compressing objects: 100% (12/12), done.
  remote: Total 12 (delta 3), reused 0 (delta 0), pack-reused 0
  Receiving objects: 100% (12/12), 10.19 KiB | 2.55 MiB/s, done.
  Resolving deltas: 100% (3/3), done.

15:10:34 /d/github_ibm $ cd code-helper/

15:10:40 /d/github_ibm/code-helper (main) $ python -m venv venv

15:11:14 /d/github_ibm/code-helper (main) $ ls
  app.py  LICENSE  Readme.md  requirements.txt  venv/

15:11:24 /d/github_ibm/code-helper (main) $ . venv/Scripts/activate
  (venv)
  15:11:36 /d/github_ibm/code-helper (main) $ pip list
  Package Version
  ------- -------
  pip     24.0

  [notice] A new release of pip is available: 24.0 -> 24.3.1
  [notice] To update, run: python.exe -m pip install --upgrade pip
  (venv)
  15:11:47 /d/github_ibm/code-helper (main) $ python.exe -m pip install --upgrade pip
  Requirement already satisfied: pip in d:\github_ibm\code-helper\venv\lib\site-packages (24.0)
  Collecting pip
    Using cached pip-24.3.1-py3-none-any.whl.metadata (3.7 kB)
  Using cached pip-24.3.1-py3-none-any.whl (1.8 MB)
  Installing collected packages: pip
    Attempting uninstall: pip
      Found existing installation: pip 24.0
      Uninstalling pip-24.0:
        Successfully uninstalled pip-24.0
  Successfully installed pip-24.3.1
  (venv)
```