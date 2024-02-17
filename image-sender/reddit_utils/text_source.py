class TextSource:
    def __init__(self) -> None:
        pass

    def get_new_messages(self) -> list[str]:
        raise NotImplementedError()