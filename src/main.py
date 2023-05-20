"""Automate README.md generation for your codebase using OpenAI's API."""

import asyncio
import os
from typing import Optional

import dacite
import openai
import pandas as pd
import typer

import builder
import model
import preprocess
from conf import AppConf, AppConfHelper, load_conf_helper
from file_factory import FileHandler
from logger import Logger

app = typer.Typer()
CONFIG_FILE = "conf/conf.toml"
LOGGER = Logger("readmeai_logger")


@app.command()
def main(
    api_key: Optional[str] = typer.Option(None, help="Your OpenAI API key."),
    local: Optional[str] = typer.Option(None, help="Path to local repository."),
    output: str = typer.Option("README_AI.md", help="Path to your README.md file."),
    remote: Optional[str] = typer.Option(None, help="URL to remote repository."),
) -> None:
    check_arguments(api_key, local, remote)
    asyncio.run(generate_readme(api_key, local, output, remote))


def check_arguments(
    api_key: Optional[str], local: Optional[str], remote: Optional[str]
) -> None:
    if not os.getenv("OPENAI_API_KEY") and not api_key:
        typer.echo("Error: Please provide your OpenAI API key.")
        raise typer.Exit(code=1)

    if not local and not remote:
        typer.echo("Error: Please provide either a local path or remote URL.")
        raise typer.Exit(code=1)


async def generate_readme(
    api_key: Optional[str], local: Optional[str], output: str, remote: Optional[str]
) -> None:
    LOGGER.info("README-AI is now executing.")

    conf = load_configuration(CONFIG_FILE)
    conf_helper = load_conf_helper(conf)

    set_command_line_arguments(api_key, conf, local, output, remote)

    repo = conf.git.path
    repo_contents = preprocess.get_codebase(repo)
    name = preprocess.get_repo_name(repo)
    conf.git.name = name
    file_exts = conf_helper.language_names
    file_names = conf_helper.dependency_files
    ignore_files = conf_helper.ignore_files
    dependencies = preprocess.get_project_dependencies(repo, file_exts, file_names)

    LOGGER.info(f"Creating README.md for the repository: {name}")
    LOGGER.info(f"Total files to document: {len(repo_contents)}")
    LOGGER.info(f"\nProject dependencies list: {dependencies}\n")

    codebase_docs = await generate_codebase_docs(
        conf, ignore_files, repo_contents, name
    )
    documentation = pd.DataFrame(codebase_docs, columns=["Module", "Summary"])

    LOGGER.info(f"OpenAI generated codebase summaries:\n\n{documentation}\n")

    build_readme(conf, conf_helper, dependencies, documentation)

    LOGGER.info("README-AI execution complete.\n")


def set_command_line_arguments(
    api_key: Optional[str],
    conf: AppConf,
    local: Optional[str],
    output: str,
    remote: Optional[str],
) -> None:
    if api_key:
        openai.api_key = api_key
    if output:
        conf.paths.md = output
    if local:
        conf.git.path, conf.git.local = local, local
        LOGGER.info(f"Using local repository: {conf.git.local}")
    if remote:
        conf.git.path, conf.git.remote = remote, remote
        LOGGER.info(f"Using remote Git repository: {conf.git.remote}")


async def generate_codebase_docs(
    conf: AppConf, ignore_files: list, repo_contents: list, name: str
) -> list:
    prompt_intro = conf.api.prompt_intro
    prompt_slogan = conf.api.prompt_slogan
    codebase_docs = await model.code_to_text(ignore_files, repo_contents)
    introduction = model.generate_summary_text(prompt_intro.format(name))
    intro_slogan = model.generate_summary_text(prompt_slogan.format(name))
    conf.md.intro = conf.md.intro.format(introduction)
    conf.md.slogan = conf.md.slogan.format(intro_slogan)

    return codebase_docs


def build_readme(
    conf: AppConf,
    conf_helper: AppConfHelper,
    dependencies: list,
    docs: pd.DataFrame,
) -> None:
    docs.to_csv(conf.paths.docs, index=False)
    builder.build(conf, conf_helper, dependencies, docs)


def load_configuration(config_path: str) -> AppConf:
    handler = FileHandler()
    conf_dict = handler.read(config_path)
    return dacite.from_dict(AppConf, conf_dict)


if __name__ == "__main__":
    app()
