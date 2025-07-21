class LCD:
    def clear(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def return_home(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def write(self, text: str) -> None:
        raise NotImplementedError("This method should be overridden by subclasses.")

    def set_cursor(self, line: int, col: int) -> None:
        raise NotImplementedError("This method should be overridden by subclasses.")

    def is_available(self) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses.")
