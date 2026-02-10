"""Custom error classes for the MCP Financial Server."""


class MCPToolError(Exception):
    """Base error for all MCP tool failures."""

    def __init__(self, message: str, tool_name: str = ""):
        self.tool_name = tool_name
        super().__init__(message)


class CompanyNotFoundError(MCPToolError):
    """Raised when a company ticker is not found."""

    def __init__(self, ticker: str):
        super().__init__(
            f"Company with ticker '{ticker}' not found.",
            tool_name="company_lookup",
        )
        self.ticker = ticker


class ValidationError(MCPToolError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, tool_name="validation")


class DatabaseError(MCPToolError):
    """Raised when a database query fails."""

    def __init__(self, message: str):
        super().__init__(message, tool_name="database")


class RateLimitExceededError(MCPToolError):
    """Raised when rate limit is exceeded."""

    def __init__(self):
        super().__init__(
            "Rate limit exceeded. Please wait before making another request.",
            tool_name="rate_limiter",
        )
