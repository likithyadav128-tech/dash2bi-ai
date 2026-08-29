"""
Custom exception hierarchy for Dash2BI AI.
Provides actionable, user-friendly error messages explaining What, Why, and How to fix.
"""

class Dash2BIError(Exception):
    """Base exception for all Dash2BI AI errors."""
    def __init__(self, message: str, details: str = "", solution: str = ""):
        super().__init__(message)
        self.message = message
        self.details = details
        self.solution = solution

    def format_user_message(self) -> str:
        msg = f"**What Happened:** {self.message}"
        if self.details:
            msg += f"\n\n**Why:** {self.details}"
        if self.solution:
            msg += f"\n\n**How to Fix:** {self.solution}"
        return msg


class DatasetValidationError(Dash2BIError):
    """Raised when uploaded CSV/Excel datasets fail validation."""
    pass


class HTMLParsingError(Dash2BIError):
    """Raised when uploaded HTML dashboard fails parsing or component extraction."""
    pass


class MappingError(Dash2BIError):
    """Raised when visual or field mapping fails critically."""
    pass


class DAXValidationError(Dash2BIError):
    """Raised when DAX measure generation or validation fails."""
    pass


class PowerBIExportError(Dash2BIError):
    """Raised when Power BI Project generation or packaging fails."""
    pass
