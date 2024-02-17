from reddit_utils.text_source import TextSource
import random

class TestTextSource(TextSource):
    def __init__(self) -> None:
        self.i = 0

    def get_new_messages(self) -> list[str]:
        num_messages = random.randint(1, 10)
        messages = []
        for i in range(0, num_messages):
            messages.append(self.get_next_message())
        return messages
    
    def get_next_message(self) -> str:
        self.i += 1
        return f"Message # {self.i}"