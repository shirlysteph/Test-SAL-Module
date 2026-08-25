#!/usr/bin/env python3


import click
import requests
import json
import sys
import os
from pathlib import Path
from tasks.community_water_system import community_water_system_feature


ONTOLOGY_FILE = Path(__file__).resolve().parent / "ontology.jsonld"


# 1. Top-level main CLI group
@click.group()
def cli():
    """Main application CLI."""
    pass

# 2. 'salmodule' group nested under the main CLI
@cli.group("salmodule")
def salmodule():
    """Implements the salmodule (CLI) specification"""
    pass

# 3. 'ontology' subcommand nested under 'salmodule'
@salmodule.command("ontology")
def ontology():
    """Print the sample-sal-module-1 ontology."""

    try:
        with ONTOLOGY_FILE.open("r", encoding="utf-8") as ontology_file:
            ontology_document = json.load(ontology_file)
    except FileNotFoundError:
        print_err_msg(f"Ontology file not found: {ONTOLOGY_FILE}")
        sys.exit(1)
    except json.JSONDecodeError as error:
        print_err_msg(f"Ontology file contains invalid JSON: {error}")
        sys.exit(1)

    click.echo(json.dumps(ontology_document, indent=4))
    


@salmodule.command("run")
# def run():
#     """Execute the salmodule:Task subclass instance set in SALMODULE_TASK_INSTANCE env"""
#     task_instance = get_salmodule_task_instance()
#     salmodule_task_2_handler(task_instance['@type'])(task_instance)

def run():
    task_instances = get_salmodule_task_instance()

    if not isinstance(task_instances, list):
        task_instances = [task_instances]

    for task_instance in task_instances:
        task_type = task_instance["@type"]
        handler = salmodule_task_2_handler(task_type)
        handler(task_instance)


def print_err_msg(msg):
    """Print an error message as a JSON object to stdout in conformance to salmodule:output SHACL Shape annotation for salmodule:Task base class"""
    err_msg = {
        "@type": "salmodule:Error",
        "rdfs:comment": msg

    }
    print( json.dumps(err_msg))

def get_salmodule_task_instance():
    """Retrieve the SAL Module task instance from the environment variable SALMODULE_TASK_INSTANCE and return it as a dictionary."""
    task_inst = os.environ.get("SALMODULE_TASK_INSTANCE")
    if not task_inst:
        print_err_msg("SALMODULE_TASK_INSTANCE environment variable is not set.")
        sys.exit(1)

    task_inst_dict = json.loads(task_inst)

    return task_inst_dict

def salmodule_task_2_handler(task_name):
    """resolve task name (salmodule:Task subclass) to corresponding handler function."""

    #  Below assumes that SAL abides by @context terms as set forth in a SAL Module's ontology
    #  In the ontology definition (see def ontology()) the task @type is set to a relative path (i.e. just the class Type no ns prefix)
    #  SAL Modules can expect that all json uses keys corresponding to resolvable terms in the ontology's @context.
     
    salmodule_tasks = {
        "CommunityWaterSystemFeature":  community_water_system_feature
    }
    if task_name not in salmodule_tasks:
        print_err_msg(f"Task subclass '{task_name}' is not recognized.")
        sys.exit(1)

    
    return salmodule_tasks[task_name]

if __name__ == "__main__":
    cli()


