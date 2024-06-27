# My git workflows

## New repo

First, create new repo on git server, e.g. `github`.
Next, run the following commands in a local folder.

```
git init                        # create new repo
git add -A                      # add all the files currently in the folder
git status                      # check what was added
git commit -m "<message>"       # commit the added contents to the repository 
git remote add origin <repo>    # add link to the repository
git branch -M main              #
git push -u origin main         # push local repo to origin, set this origin to be used
```

## Sync after .gitignore is updated

```
git rm -r --cached .        # remove everything from local repo while keeping it in local folder
git add .                   # add everything back while respecting .gitignore
git commit -m "<message>"   # commit locally
