"""Run or update the project. This file uses the `doit` Python package. It works
like a Makefile, but is Python-based

"""

#######################################
## Configuration and Helpers for PyDoit
#######################################
## Make sure the src folder is in the path
import sys

sys.path.insert(1, "./src/")

import shutil
from os import environ, getcwd, path
from pathlib import Path

from colorama import Fore, Style, init

## Custom reporter: Print PyDoit Text in Green
# This is helpful because some tasks write to sterr and pollute the output in
# the console. I don't want to mute this output, because this can sometimes
# cause issues when, for example, LaTeX hangs on an error and requires
# presses on the keyboard before continuing. However, I want to be able
# to easily see the task lines printed by PyDoit. I want them to stand out
# from among all the other lines printed to the console.
from doit.reporter import ConsoleReporter

from settings import config

try:
    in_slurm = environ["SLURM_JOB_ID"] is not None
except:
    in_slurm = False


class GreenReporter(ConsoleReporter):
    def write(self, stuff, **kwargs):
        doit_mark = stuff.split(" ")[0].ljust(2)
        task = " ".join(stuff.split(" ")[1:]).strip() + "\n"
        output = (
            Fore.GREEN
            + doit_mark
            + f" {path.basename(getcwd())}: "
            + task
            + Style.RESET_ALL
        )
        self.outstream.write(output)


if not in_slurm:
    DOIT_CONFIG = {
        "reporter": GreenReporter,
        # other config here...
        # "cleanforget": True, # Doit will forget about tasks that have been cleaned.
        "backend": "sqlite3",
        "dep_file": "./.doit-db.sqlite",
    }
else:
    DOIT_CONFIG = {"backend": "sqlite3", "dep_file": "./.doit-db.sqlite"}
init(autoreset=True)


BASE_DIR = config("BASE_DIR")
DATA_DIR = config("DATA_DIR")
MANUAL_DATA_DIR = config("MANUAL_DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")
REPORTS_DIR = BASE_DIR / "reports"
OS_TYPE = config("OS_TYPE")
USER = config("USER")

## Helpers for handling Jupyter Notebook tasks
environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

# fmt: off
## Helper functions for automatic execution of Jupyter notebooks
def jupyter_execute_notebook(notebook_path):
    return f'jupyter nbconvert --execute --to notebook --ClearMetadataPreprocessor.enabled=True --inplace "{notebook_path}"'
def jupyter_to_html(notebook_path, output_dir=OUTPUT_DIR):
    return f'jupyter nbconvert --to html --output-dir="{output_dir}" "{notebook_path}"'
def jupyter_to_md(notebook_path, output_dir=OUTPUT_DIR):
    """Requires jupytext"""
    return f'jupytext --to markdown --output-dir="{output_dir}" "{notebook_path}"'
def jupyter_clear_output(notebook_path):
    """Clear the output of a notebook"""
    return f'jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --inplace "{notebook_path}"'
# fmt: on


def mv(from_path, to_path):
    """Move a file to a folder"""
    from_path = Path(from_path)
    to_path = Path(to_path)
    to_path.mkdir(parents=True, exist_ok=True)
    if OS_TYPE == "nix":
        command = f'mv "{from_path}" "{to_path}"'
    else:
        command = f'move "{from_path}" "{to_path}"'
    return command


def copy_file(origin_path, destination_path, mkdir=True):
    """Create a Python action for copying a file."""

    def _copy_file():
        origin = Path(origin_path)
        dest = Path(destination_path)
        if mkdir:
            dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, dest)

    return _copy_file


##################################
## Begin rest of PyDoit tasks here
##################################


def task_config():
    """Create empty directories for data and output if they don't exist"""
    return {
        "actions": ["ipython ./src/settings.py"],
        "targets": [DATA_DIR, OUTPUT_DIR],
        "file_dep": ["./src/settings.py"],
        "clean": [],
    }

def task_pull():
    """Pull data from external sources"""
    yield {
        "name": "bonds",
        "doc": "Pull bond prices/yields from WRDS Bond Returns",
        "actions": [
            "ipython ./src/settings.py",
            "ipython ./src/pull_bonds.py",
        ],
        "targets": [DATA_DIR / "bond_prices.parquet"],
        "file_dep": ["./src/settings.py", "./src/pull_bonds.py"],
        "clean": [],
    }
    yield {
        "name": "ratings",
        "doc": "Pull Mergent FISD ratings",
        "actions": [
            "ipython ./src/settings.py",
            "ipython ./src/pull_LSEG_Mergent.py",
        ],
        "targets": [DATA_DIR / "Mergent_FISD_ratings.parquet"],
        "file_dep": ["./src/settings.py", "./src/pull_LSEG_Mergent.py"],
        "clean": [],
    }
    yield {
        "name": "cds",
        "doc": "Pull Markit CDS spreads from WRDS",
        "actions": [
            "ipython ./src/settings.py",
            "ipython ./src/pull_CDS.py",
        ],
        "targets": [DATA_DIR / "CDS.parquet"],
        "file_dep": ["./src/settings.py", "./src/pull_CDS.py"],
        "clean": [],
    }
    yield {
        "name": "treasuries",
        "doc": "Pull CRSP Treasury data from WRDS",
        "actions": [
            "ipython ./src/settings.py",
            "ipython ./src/pull_CRSP_treasuries.py",
        ],
        "targets": [DATA_DIR / "CRSP_treasuries.parquet"],
        "file_dep": ["./src/settings.py", "./src/pull_CRSP_treasuries.py"],
        "clean": [],
    }

def task_filter():
    """Filter + match bonds to CDS (in-sample selection, but data stored through present day for extension)."""
    return {
        "actions": [
            "ipython ./src/settings.py",
            "python ./src/filter_data.py",
        ],
        "file_dep": [
            "./src/settings.py",
            "./src/filter_data.py",
            DATA_DIR / "bond_prices.parquet",
            DATA_DIR / "Mergent_FISD_ratings.parquet",
            DATA_DIR / "CDS.parquet",
        ],
        "targets": [
            DATA_DIR / "matched_bond_cds.parquet",
        ],
        "task_dep": ["pull"],
        "clean": True,
    }

# Unit test for data
def task_test_data_quality():
    """Test data quality after filtering"""
    return {
        'actions': ['pytest tests/test_data_quality.py tests/test_filters.py -v'],
        'file_dep': [DATA_DIR / 'matched_bond_cds.parquet'],
        'task_dep': ['filter'],
        'verbosity': 2,
    }

def task_calc_pecds():
    """Compute PECDS."""
    return {
        "actions": [
            "ipython ./src/settings.py",
            "python -u ./src/calc_PECDS.py",
        ],
        "file_dep": [
            "./src/settings.py",
            "./src/calc_PECDS.py",
            DATA_DIR / "matched_bond_cds.parquet",
            DATA_DIR / "CRSP_treasuries.parquet",
        ],
        "targets": [DATA_DIR / "pecds.parquet"],
        "task_dep": ["filter"],
        "clean": True,
    }

def task_calc_basis():
    """Compute CDS-bond basis."""
    return {
        "actions": ["python ./src/calc_basis.py"],
        "file_dep": ["./src/calc_basis.py", DATA_DIR / "pecds.parquet"],
        "targets": [DATA_DIR / "basis.parquet"],
        "task_dep": ["calc_pecds"],
        "clean": True,
    }


# Unit test to ensure pipeline is working for all data cleaning + calculations
def task_test_pipeline():
    """Test pipeline integrity after calculations"""
    return {
        'actions': ['pytest tests/test_pipeline.py -v'],
        'file_dep': [
            DATA_DIR / 'basis.parquet',
            OUTPUT_DIR / 'table1_replication.tex',
            OUTPUT_DIR / 'replication_figure1.png',
            OUTPUT_DIR / 'extension_figure1.png',
        ],
        'task_dep': ['calc_basis', 'outputs'],  # Added 'outputs' dependency
        'verbosity': 2,
    }

def task_outputs():
    """Generate Figure 1 (png+html), Table 1 (tex), and descriptive outputs."""
    return {
        "actions": [
            "python ./src/replicate_figure1.py",
            "python ./src/replicate_table1.py",
            "python ./src/underlying_data_summary.py",
        ],
        "file_dep": [
            "./src/replicate_figure1.py",
            "./src/replicate_table1.py",
            "./src/underlying_data_summary.py",
            DATA_DIR / "basis.parquet",
        ],
        "targets": [
            OUTPUT_DIR / "replication_figure1.png",
            OUTPUT_DIR / "extension_figure1.png",
            OUTPUT_DIR / "replication_figure1.html",
            OUTPUT_DIR / "extension_figure1.html",
            OUTPUT_DIR / "table1_replication.tex",
            OUTPUT_DIR / "sample_summary_table.tex",
            OUTPUT_DIR / "underlying_spreads.png",
        ],
        "task_dep": ["calc_basis"],
        "clean": True,
    }


# Unit test for how close replication was to paper
def task_test_replication():
    """Test replication quality after generating outputs"""
    return {
        'actions': ['pytest tests/test_replication.py -v'],
        'file_dep': [
            OUTPUT_DIR / 'table1_replication.tex',
            OUTPUT_DIR / 'replication_figure1.png'
        ],
        'task_dep': ['outputs'],
        'verbosity': 2,
    }


notebook_tasks = {
    "notebook_interactive_ipynb": {
        "path": "./src/notebook_interactive_ipynb.py",
        "file_dep": [],
        "targets": [],
    },
}


# fmt: off
def task_run_notebooks():
    """Preps the notebooks for presentation format.
    Execute notebooks if the script version of it has been changed.
    """
    for notebook in notebook_tasks.keys():
        pyfile_path = Path(notebook_tasks[notebook]["path"])
        notebook_path = pyfile_path.with_suffix(".ipynb")
        yield {
            "name": notebook,
            "actions": [
                """python -c "import sys; from datetime import datetime; print(f'Start """ + notebook + """: {datetime.now()}', file=sys.stderr)" """,
                f'jupytext --to notebook --output "{notebook_path}" "{pyfile_path}"',
                jupyter_execute_notebook(notebook_path),
                jupyter_to_html(notebook_path, OUTPUT_DIR),
                mv(notebook_path, REPORTS_DIR),
                """python -c "import sys; from datetime import datetime; print(f'End """ + notebook + """: {datetime.now()}', file=sys.stderr)" """,
            ],
            "file_dep": [
                pyfile_path,
                *notebook_tasks[notebook]["file_dep"],
            ],
            "targets": [
                OUTPUT_DIR / f"{notebook}.html",
                REPORTS_DIR / f"{notebook}.ipynb",
                *notebook_tasks[notebook]["targets"],
            ],
            "clean": True,
        }
# fmt: on

###############################################################
## Task below is for LaTeX compilation
###############################################################


def task_compile_latex_docs():
    """Compile the LaTeX documents to PDFs"""
    file_dep = [
        # "./reports/report_example.tex",
        "./reports/main_report.tex",
        "./reports/my_article_header.sty",
        OUTPUT_DIR / "replication_figure1.png",
        OUTPUT_DIR / "extension_figure1.png",
        OUTPUT_DIR / "table1_replication.tex",
        OUTPUT_DIR / "table1_extension.tex",
    ]
    targets = [
        "./reports/main_report.pdf",
    ]

    return {
        "actions": [
            "latexmk -xelatex -halt-on-error -cd ./reports/main_report.tex",
            "latexmk -xelatex -halt-on-error -c -cd ./reports/main_report.tex",
        ],
        "targets": targets,
        "file_dep": file_dep,
        "task_dep": ["outputs"],
        "clean": True,
    }

sphinx_targets = [
    "./docs/index.html",
]


def task_build_chartbook_site():
    """Compile Sphinx Docs"""
    notebook_scripts = [
        Path(notebook_tasks[notebook]["path"])
        for notebook in notebook_tasks.keys()
    ]
    file_dep = [
        "./README.md",
        "./chartbook.toml",
        *notebook_scripts,
        OUTPUT_DIR / 'replication_figure1.html',
        OUTPUT_DIR / 'extension_figure1.html',
    ]

    return {
        "actions": [
            "chartbook build -f",
        ],  # Use docs as build destination
        "targets": sphinx_targets,
        "file_dep": file_dep,
        "task_dep": [
            "run_notebooks",
            "outputs",
        ],
        "clean": True,
    }