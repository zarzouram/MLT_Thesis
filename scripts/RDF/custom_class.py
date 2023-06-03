from collections import UserDict


class ValueChangedError(Exception):
    """
    Custom exception raised when trying to change the value of an existing key
    in an ImmutableValueDict.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ImmutableValueDict(UserDict):
    """
    Dictionary subclass that raises a ValueChangedError when trying to change
    the value of an existing key.

    Inherits from UserDict.

    Overrides:
        __setitem__ -- Adds a check if key exists and if new value is different
        from old value.

    # Example usage:
    ivd = ImmutableValueDict()
    ivd['a'] = 1  # okay
    ivd['a'] = 1  # okay, value is the same
    ivd['a'] = 2  # raises ValueChangedError: Cannot change value of existing
                  # key "a" from "1" to "2".
    """

    def __setitem__(self, key, val):
        """
        Set a value for a key in the dictionary.

        If the key already exists and the new value is different from the old
        value, raises a ValueChangedError.

        Args:
            key: The key for which to set the value.
            val: The value to set.

        Raises:
            ValueChangedError: If key already exists and new value is different
            from old value.
        """
        print(key in self, self.get(key), "==", val, self.get(key) == val)
        if key in self and self.get(key) == val:
            print(key, val)
            raise ValueChangedError(
                f'Cannot change value of existing key "{key}" from "{self[key]}" to "{val}".'  # noqa: E501
            )

        super().__setitem__(key, val)
