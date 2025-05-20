class DatabaseError(Exception):
    """Base class for all database-related exceptions"""
    def __init__(self, message="Database operation failed"):
        self.message = message
        super().__init__(self.message)

class DuplicateEntryError(DatabaseError):
    """Raised when a unique constraint is violated"""
    def __init__(self, field):
        self.field = field
        self.message = f"Duplicate entry for field: {field}"
        super().__init__(self.message)

class RecordNotFoundError(DatabaseError):
    """Raised when a requested record is not found"""
    def __init__(self, model, identifier):
        self.model = model
        self.identifier = identifier
        self.message = f"{model} with id {identifier} not found"
        super().__init__(self.message)

class InvalidDataError(DatabaseError):
    """Raised when invalid data is provided for database operation"""
    def __init__(self, field, value,requirement):
        self.field = field
        self.value = value
        self.requirement = requirement
        self.message = f"Invalid value '{value}' for field '{field}' - {requirement}"
        super().__init__(self.message)

class TransactionError(DatabaseError):
    """Raised when a database transaction fails"""
    def __init__(self, operation):
        self.operation = operation
        self.message = f"Transaction failed during {operation}"
        super().__init__(self.message)

class OperationNotAllowedError(DatabaseError):
    """Raised when an operation is not permitted"""
    def __init__(self, message, detail=None):
        self.message = message
        self.detail = detail
        super().__init__(f"Operasi tidak diizinkan: {message}")