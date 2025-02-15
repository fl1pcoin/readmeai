from typing import ClassVar

from readmeai.config.constants import LLMService
from readmeai.config.settings import ConfigLoader
from readmeai.errors import UnsupportedServiceError
from readmeai.ingestion.models import RepositoryContext
from readmeai.models.llama import LLamaHandler
from readmeai.models.vsegpt import OpenAIHandler
from readmeai.models.base import BaseModelHandler


class ModelFactory:
    """
    Factory class for creating LLM API handler instances.
    """

    _model_map: ClassVar[dict] = {
        LLMService.OLLAMA.value: LLamaHandler,
        LLMService.VSEGPT.value: OpenAIHandler,
        LLMService.OPENAI.value: OpenAIHandler,
    }

    @staticmethod
    def get_backend(
        config: ConfigLoader, context: RepositoryContext
    ) -> BaseModelHandler:
        """
        Returns the appropriate LLM API handler based on config.toml.
        """
        llm_service = ModelFactory._model_map.get(config.config.llm.api)

        if llm_service is None:
            raise UnsupportedServiceError(
                f"Unsupported LLM service provided: {config.config.llm.api}",
            )

        return llm_service(config, context)
