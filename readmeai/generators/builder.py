import os
from pathlib import Path

from readmeai.config.settings import ConfigLoader
from readmeai.generators import badges
from readmeai.ingestion.models import RepositoryContext
from readmeai.readers.git.providers import GitHost
from readmeai.templates.header import HeaderTemplate
from readmeai.templates.quickstart import QuickStartBuilder
from readmeai.templates.contributing import ContributingBuilder
from readmeai.readers.git.metadata import fetch_git_repository_metadata


class MarkdownBuilder:
    """
    Builds each section of the README Markdown file.
    """

    def __init__(
            self,
            config_loader: ConfigLoader,
            repo_context: RepositoryContext,
            temp_dir: str,
    ):
        """
Initializes the class with configuration and repository context.

    This method sets up the instance by loading the configuration, 
    repository context, and temporary directory. It also initializes 
    various attributes related to the configuration and repository.

    Args:
        config_loader: An object responsible for loading configuration settings.
        repo_context: An object that contains context information about the repository.
        temp_dir: A string representing the path to the temporary directory.

    Returns:
        None
    """
        self.config_loader = config_loader
        self.config = config_loader.config
        self.deps = repo_context.dependencies
        self.docs = repo_context.docs_paths
        self.repo_context = repo_context
        self.temp_dir = Path(temp_dir)
        self.md = self.config.md
        self.git = self.config.git
        self.repo_url = (
            self.git.repository
            if self.git.host_domain != GitHost.LOCAL.name.lower()
            else f"../{self.git.name}"
        )
        self.header_template = HeaderTemplate(self.md.header_style)
        self.table_of_contents = self.md.table_of_contents
        self.metadata = fetch_git_repository_metadata(self.repo_url)

    @property
    def header_and_badges(self) -> str:
        """Generates the README header section."""
        md_shields, md_badges = badges.shieldsio_icons(
            self.config,
            self.deps,
            str(self.git.full_name),
            str(self.git.host),
        )

        header_data = {
            "align": self.md.align,
            "image": self.md.image,
            "image_width": self.md.image_width,
            "repo_name": (
                self.git.name.upper() if self.git.name else self.md.placeholder
            ),
            "shields_icons": md_shields,
            "badges_tech_stack": md_badges,
            "badges_tech_stack_text": self.md.badges_tech_stack_text,
        }
        return self.header_template.render(header_data)

    @property
    def installation_guide(self) -> str:
        """Generates the README Installation section."""
        return QuickStartBuilder(
            self.config_loader, self.repo_context
        ).build_installation_section()

    @property
    def getting_started_guide(self) -> str:
        """Generates the README Getting Started section."""
        return QuickStartBuilder(
            self.config_loader, self.repo_context
        ).build_usage_section()

    @property
    def examples(self) -> str:
        """Generates the README Examples section"""
        examples_path = next(
            (path for path in self.docs if path.endswith((
                "examples",
                "tutorials",
                "guides"
            ))),
            ""
        )
        examples_name = (os.path.basename(examples_path)
                         or "Not found any examples")

        return self.md.examples.format(
            examples=examples_name,
            default_branch=self.metadata.default_branch,
            host_domain=self.git.host_domain,
            full_name=self.git.full_name,
            examples_path=examples_path.replace(os.sep, "/"),
        )

    @property
    def contributing(self) -> str:
        """Generates the README Contributing section."""
        return ContributingBuilder(
            self.config_loader, self.repo_context
        ).build()

    @property
    def license(self) -> str:
        """Generates the README License section"""
        license_path = next(
            (path for path in self.docs if path.startswith((
                "LICENSE",
                "LICENCE"
            ))),
            self.metadata.license_url
        )

        return self.md.license.format(
            license_name=self.metadata.license_name or "Not found any License",
            default_branch=self.metadata.default_branch,
            host_domain=self.git.host_domain,
            full_name=self.git.full_name,
            license_path=license_path,
        )

    @property
    def documentation(self) -> str:
        """Generates the README Documentation section"""
        docs = "docs"
        if not self.metadata.homepage_url:
            if "docs" in self.docs:
                homepage_url = (f"https://{self.git.host_domain}/"
                                f"{self.git.full_name}/tree/"
                                f"{self.metadata.default_branch}/docs")
            else:
                docs = "Not found any docs"
                homepage_url = ""
        else:
            homepage_url = self.metadata.homepage_url

        return self.md.documentation.format(
            repo_name=self.git.name, docs=docs, homepage_url=homepage_url
        )

    @property
    def contacts(self) -> str:
        """Generates the README Contacts section"""
        return self.md.contacts

    @property
    def acknowledgments(self) -> str:
        """Generates the README Contacts section"""
        return self.md.acknowledgments

    @property
    def citation(self) -> str:
        """Generates the README Citation section"""
        for path in self.docs:
            if path.startswith("CITATION"):
                return self.md.citation + self.md.citation_v1.format(
                    host_domain=self.git.host_domain,
                    full_name=self.git.full_name,
                    default_branch=self.metadata.default_branch,
                    citation_path=path,
                )

        return self.md.citation + self.md.citation_v2.format(
            owner=self.metadata.owner,
            year=self.metadata.created_at.split('-')[0],
            repo_name=self.git.name,
            publisher=self.git.host_domain,
            repository_url=self.git.repository,
        )

    def build(self) -> str:
        """Builds each section of the README.md file."""
        readme_md_contents = [
            self.header_and_badges,
            self.md.overview,
            self.table_of_contents,
            self.md.core_features,
            self.installation_guide,
            self.examples,
            self.documentation,
            self.getting_started_guide,
            self.contributing,
            self.license,
            self.acknowledgments,
            self.contacts,
            self.citation,
        ]

        return "\n".join(readme_md_contents)
