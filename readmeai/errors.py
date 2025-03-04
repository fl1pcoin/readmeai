from __future__ import annotations


class ReadmeAIError(Exception):
    """
    Base class for exceptions in this module.
    """

    ...


class ReadmeGeneratorError(Exception):
    """
    Raised when an error occurs during README generation.
    """

    def __init__(self, message, *args):
        """
Initializes an instance of the class with a custom error message.

    This method sets the error message to indicate an issue with generating
    a README file. It also calls the initializer of the superclass with
    the formatted message.

    Args:
        message: A string containing the specific error message.
        *args: Additional positional arguments to be passed to the superclass.

    Returns:
        None
    """
        self.message = f"Error generating README: {message}"
        super().__init__(self.message)


# ----------------- CLI ----------------------------------


class CLIError(ReadmeAIError):
    """Exceptions related to the CLI."""

    def __init__(self, message, *args):
        """
Initializes an instance of the class with a custom error message.

    This method sets up the error message for an invalid option provided to the command-line interface (CLI).

    Args:
        message: A string containing the specific invalid option message.
        *args: Additional arguments to be passed to the superclass initializer.

    Returns:
        None
    """
        super().__init__(f"Invalid option provided to CLI: {message}", *args)


# ----------------- File System ----------------------------------


class FileSystemError(ReadmeAIError):
    """
    Exceptions related to file system operations.
    """

    def __init__(self, message, *args):
        """
Initializes a FileSystemError with a custom message.

    This method sets up the error message for the FileSystemError 
    by calling the superclass constructor with a formatted message.

    Args:
        message: A string containing the error message to be displayed.
        *args: Additional arguments to be passed to the superclass constructor.

    Returns:
        None
    """
        super().__init__(f"File system error: {message}", *args)


class FileReadError(FileSystemError):
    """
    Raised when a file cannot be read.
    """

    ...


class FileWriteError(FileSystemError):
    """
    Raised when a file cannot be written to.
    """

    ...


# ----------------- Git ----------------------------------


class GitValidationError(ReadmeAIError):
    """
    Base class errors validating Git repositories.
    """

    ...


class GitCloneError(GitValidationError):
    """
    Raised when a Git repository cannot be cloned.
    """

    def __init__(self, repository: str, *args):
        """
Initializes an instance of the class.

    This method sets the repository attribute and calls the superclass 
    initializer with a formatted error message indicating the failure 
    to clone the specified repository.

    Args:
        repository: The name or URL of the repository that failed to clone.
        *args: Additional arguments to be passed to the superclass initializer.

    Returns:
        None
    """
        self.repository = repository
        super().__init__(f"Failed to clone repository: {repository}", *args)


class GitURLError(GitValidationError):
    """
    Raised when an invalid Git repository URL is provided.
    """

    def __init__(self, url: str, *args):
        """
Initializes an instance of the class with a specified URL.

    This method sets the URL attribute and calls the superclass 
    initializer with a formatted error message.

    Args:
        self: The instance of the class.
        url: The URL of the Git repository.
        *args: Additional arguments to be passed to the superclass initializer.

    Returns:
        None
    """
        self.url = url
        super().__init__(f"Invalid Git repository URL: {url}", *args)


class InvalidRepositoryError(GitValidationError):
    """
    Raised when an invalid repository is provided.
    """

    def __init__(self, repository: str, *args):
        """
Initializes an instance of the class.

    This method sets the repository attribute and calls the superclass 
    initializer with a formatted error message.

    Args:
        repository: The repository string that is being validated.
        *args: Additional arguments to be passed to the superclass initializer.

    Returns:
        None
    """
        self.repository = repository
        super().__init__(f"Invalid repository provided: {repository}", *args)


class UnsupportedGitHostError(GitValidationError):
    """
    Raised when an unsupported Git host is provided.
    """

    def __init__(self, host: str, *args):
        """
Initializes an instance of the class.

    This method sets the host attribute and calls the superclass 
    initializer with a formatted error message indicating an 
    unsupported Git host.

    Args:
        host: The host string representing the Git host.
        *args: Additional arguments to be passed to the superclass 
            initializer.

    Returns:
        None
    """
        self.host = host
        super().__init__(f"Unsupported Git host: {host}", *args)


# ----------------- Repository ----------------------------------


class RepositoryProcessingError(ReadmeAIError):
    """
    Raised when an error occurs during repository processing.
    """

    ...


# ----------------- LLM API ----------------------------------


class UnsupportedServiceError(ReadmeAIError):
    """
    Raised when an unsupported LLM service is provided.
    """

    def __init__(self, message, *args):
        """
Initializes the instance with a message.

    This method calls the superclass's initializer with the provided message
    and any additional arguments.

    Args:
        message: The message to be passed to the superclass initializer.
        *args: Additional arguments to be passed to the superclass initializer.

    Returns:
        None
    """
        super().__init__(message, *args)
