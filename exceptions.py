
class Impossible(Exception):
    """Exception raised when an impossible action is requested.

    (e.g. healing when at full health)
    """
    pass

class UserError(Exception):
    """Exception for when the user does something wrong."""
    pass

class VimError(UserError):
    """Exception for when the user tries an invalid vim command."""
    def __init__(self,message:str="Invalid command."):
        # Just doing this to standardize the error messages somewhat.
        #  (A more specific message is still *allowed*, but I'll try
        #   to avoid doing that.)
        super().__init__(message)
