import tempfile
from typing import Optional, Union

from readmeai.config.constants import ImageOptions
from readmeai.readmegen_article.config.settings import ArticleConfigLoader
from readmeai.config.settings import ConfigLoader

from readmeai.readmegen_article.generators.builder import ArticleMarkdownBuilder
from readmeai.generators.builder import MarkdownBuilder
from readmeai.ingestion.models import RepositoryContext
from readmeai.ingestion.pipeline import RepositoryProcessor
from readmeai.logger import get_logger
from readmeai.models.factory import ModelFactory
from readmeai.postprocessor import response_cleaner
from readmeai.readers.git.repository import load_data
from readmeai.utils.file_handler import FileHandler

_logger = get_logger(__name__)


def readme_generator(
        config: Union[ConfigLoader, ArticleConfigLoader], 
        output_file: str, article: Optional[str]
) -> None:
    """Processes the repository and builds the README file."""

    with tempfile.TemporaryDirectory() as temp_dir:

        repo_path = load_data(config.config.git.repository, temp_dir)

        processor: RepositoryProcessor = RepositoryProcessor(config=config)
        context: RepositoryContext = processor.process_repository(
            repo_path=repo_path
        )

        log_repository_context(context)

        llm = ModelFactory.get_backend(config, context)

        if article is None:
            responses = llm.batch_request()

            (
                file_summaries,
                core_features,
                overview,
            ) = responses

            config.config.md.overview = config.config.md.overview.format(
                response_cleaner.process_markdown(overview)
            )
            config.config.md.core_features = config.config.md.core_features.format(
                response_cleaner.process_markdown(core_features)
            )

        else:
            responses = llm.article_batch_request(article)

            (
                file_summary,
                pdf_summary,
                overview,
                content,
                algorithms,
            ) = responses

            config.config.md.overview = config.config.md.overview.format(
                response_cleaner.process_markdown(overview)
            )
            config.config.md.content = config.config.md.content.format(
                response_cleaner.process_markdown(content)
            )
            config.config.md.algorithms = config.config.md.algorithms.format(
                response_cleaner.process_markdown(algorithms)
            )

        if config.config.md.image in [None, "", ImageOptions.ITMO_LOGO.value]:
            config.config.md.image = ImageOptions.ITMO_LOGO.value

        if article is None:
            readme_md_content = MarkdownBuilder(config, context, temp_dir).build()
        else:
            readme_md_content = ArticleMarkdownBuilder(config).build()

        FileHandler().write(output_file, readme_md_content)

        log_process_completion(output_file)


def log_repository_context(context: RepositoryContext) -> None:
    """Logs a snippet of the processed repository context data."""
    _logger.info(f"Total files analyzed: {len(context.files)}")
    _logger.info(f"Metadata extracted: {context.metadata}")
    _logger.info(f"Dependencies: {context.dependencies}")
    _logger.info(f"Languages: {context.language_counts}")


def log_process_completion(output_file: str) -> None:
    """Logs the completion of the README generation process."""
    _logger.info("README.md file generated successfully.")
    _logger.info(f"Output file saved @ {output_file}")
