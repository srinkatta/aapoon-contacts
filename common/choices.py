import enum


class EnvironmentChoices(enum.Enum):
    """
    Environment choices for the application.

    PRODUCTION: Production environment
    LOCAL: Local environment
    DEVELOPMENT: Development environment
    QA: Quality Assurance environment
    """

    PRODUCTION = "production"
    LOCAL = "local"
    DEVELOPMENT = "development"
    QA = "qa"

    def __str__(self):
        return self.value  # Ensures string representation of the enum