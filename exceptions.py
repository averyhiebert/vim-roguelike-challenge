
class Impossible(Exception):
    """Exception raised when an impossible action is requested.

    (e.g. healing when at full health)

    To be logged but not displayed as error text.
    """
    pass

class UserError(Exception):
    """To be used for any type of error that the user should see."""
    pass

class VimError(UserError):
    """Exception for when the user tries an invalid vim command."""
    def __init__(self,attempted_command:str):
        # Just doing this to standardize the error messages somewhat.
        #  (A more specific message is still *allowed*, but I'll try
        #   to avoid doing that.)
        message = f"E492: Not an editor command: {attempted_command}"
        super().__init__(message)

class RegisterError(UserError):
    def __init__(self,register):
        message = f" Not a valid register: {register} "
        super().__init__(message)

class NewGame(Exception):
    pass
