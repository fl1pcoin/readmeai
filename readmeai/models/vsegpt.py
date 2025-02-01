import os
from typing import Any

import openai

from readmeai.config.constants import LLMService
from readmeai.config.settings import ConfigLoader
from readmeai.ingestion.models import RepositoryContext
from readmeai.models.base import BaseModelHandler
from readmeai.models.tokens import token_handler


class OpenAIHandler(BaseModelHandler):
    """
    OpenAI API LLM implementation, with VseGPT support.
    """

    def __init__(
            self,
            config_loader: ConfigLoader,
            context: RepositoryContext,
    ) -> None:
        super().__init__(config_loader, context)
        self._model_settings()

    def _model_settings(self):
        self.model = self.config.llm.model
        self.temperature = self.config.llm.temperature
        self.tokens = self.config.llm.tokens

        if self.config.llm.api == LLMService.OPENAI.name:
            self.client = openai.OpenAI(
                base_url="https://api.openai.com/v1",
                api_key=os.getenv("OPENAI_API_KEY")
            )

        elif self.config.llm.api == LLMService.VSEGPT.name:
            self.client = openai.OpenAI(
                base_url="https://api.vsegpt.ru/v1",
                api_key=os.getenv("VSE_GPT_KEY")
            )

    def _make_request(
            self,
            index: str | None,
            prompt: str | None,
            tokens: int | None,
            temperature: float,
            repo_files: Any,
    ) -> Any:
        prompt = token_handler(self.config, index, prompt, tokens)

        response_big = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            temperature=temperature,
            max_tokens=tokens,
        )

        response = response_big.choices[0].message.content
        return index, response
