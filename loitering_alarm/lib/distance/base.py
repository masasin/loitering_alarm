class DistanceSensor:
    @property
    def distance(self) -> float | None:
        raise NotImplementedError("This method should be overridden in subclasses.")
