# MLOps Lab 1

## Question 1

Running `uv init` initialized the Python project and created the basic
project structure.

- `.python-version`: specifies the Python version used by the project.
- `pyproject.toml`: contains the project configuration, metadata,
  Python requirements, and dependencies.
- `README.md`: contains the documentation of the project.
- `src/`: contains the Python source code.
- `.git/`: contains Git's version control information.

## Question 2

Running `dvc init` created the `.dvc` directory and the `.dvcignore` file.

- `.dvc/config`: stores the DVC configuration, such as remote storage settings.
- `.dvc/.gitignore`: prevents local DVC files such as cache and temporary files from being tracked by Git.
- `.dvc/tmp/`: contains temporary files used internally by DVC and should not be pushed to Git.
- `.dvcignore`: works similarly to `.gitignore` and tells DVC which files or folders it should ignore.

The DVC configuration files should be pushed to Git so that the project configuration can be shared with other developers. Temporary files and cached data should not be pushed.


## Question 3

The DVC credentials were stored in the global DVC configuration because the
`--global` option was used.

On Windows, the global DVC configuration is typically stored in:

`C:\Users\<username>\AppData\Local\iterative\dvc\config`

Other configuration options include:

- `--local`: stores settings in `.dvc/config.local` for this project only.
  This file is ignored by Git and is appropriate for credentials.
- No flag: stores configuration in `.dvc/config`, which is intended to be
  shared through Git, so secrets should not be placed there.
- `--system`: stores configuration at the system level for all users.

Credentials should not be pushed to GitHub because they are private secrets.
Only non-sensitive DVC configuration should be committed.


## Question 4

After running `dvc add data`, DVC created or updated the `.gitignore` file
and added:

`/data`

This means Git will ignore the actual `data` folder and its contents.
The dataset itself will therefore not be stored directly in GitHub.

Instead, DVC manages the dataset separately, while Git tracks the small
metadata file that describes the dataset.

## Question 5

DVC created a `data.dvc` file.

It contains metadata describing the tracked `data` directory, including:

- the MD5 hash of the data directory
- the total size of the tracked data
- the number of files
- the hash type
- the path of the tracked directory

In this project, `data.dvc` shows that the tracked `data` directory contains
16,643 files with a total size of about 1.19 GB.

The `data.dvc` file acts as a pointer to the version of the dataset managed
by DVC. This file should be committed to Git, while the actual dataset is
stored in the DVC remote.

## Question 6

The dataset was configured to be stored in the DVC remote on DagsHub rather
than directly in GitHub.

I attempted to upload the dataset using `dvc push`. Most objects began
transferring successfully, but the upload encountered network timeout and
server disconnection errors before all files were transferred.

Since the dataset contains 16,643 files and is approximately 1.19 GB, the
instructor indicated that completing the full dataset upload was not required
if the transfer took too long.

The Git repository still contains `data.dvc`, which identifies the exact
version of the dataset tracked by DVC, while the actual `data/` directory is
ignored by Git.

## Question 7

After cloning the GitHub repository into a new temporary folder, the
`data` directory is not present.

Git contains the `data.dvc` file, which describes the version of the
dataset tracked by DVC, but the actual dataset is stored separately in
the DVC remote.

To retrieve the dataset after cloning the repository, the required
command is:

`dvc pull`

This command uses the information in `data.dvc` to download the
corresponding data from the configured DVC remote.