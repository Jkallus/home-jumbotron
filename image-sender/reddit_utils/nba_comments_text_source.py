import heapq
import logging
import os
import threading
import time
from praw.models import MoreComments
from reddit_utils.reddit_text_source import RedditTextSource

logger = logging.getLogger(__name__)

class NBACommentsTextSource(RedditTextSource):
    def __init__(self) -> None:
        super().__init__()

        subreddit = os.getenv("SUBREDDIT")
        if subreddit is None:
            raise Exception("SUBREDDIT environment variable not set")

        self.subreddit = self.reddit.subreddit(subreddit)
        self.seen_comment_ids = set()
        self.comment_queue = []  # Priority queue for comments
        self.queue_lock = threading.Lock()  # Lock for synchronizing access to the queue
        self.new_comment_event = threading.Event()  # Event to signal when new comments are available

        if "Game Thread" in self.subreddit.sticky(number=1).title:
            self.submission = self.subreddit.sticky(number=1)
        elif "Game Thread" in self.subreddit.sticky(number=2).title:
            self.submission = self.subreddit.sticky(number=2)
        else:
            raise Exception("No Game Thread post found in stickied posts")

        # Start the background thread
        self.update_thread = threading.Thread(target=self.update_comments, daemon=True)
        self.update_thread.start()

    def update_comments(self):
        while True:
            new_comments = []
            for comment in self.subreddit.comments(limit=None):
                # Check if the comment is from the target submission
                if comment.submission.id == self.submission.id:
                    # Skip any comments we've already seen
                    if comment.id not in self.seen_comment_ids:
                        if len(comment.body) < 100:
                            with self.queue_lock:
                                # Add new comments to the priority queue with negative timestamp as priority and comment ID as tiebreaker
                                logging.info(f"Adding comment: {comment.body}")
                                heapq.heappush(self.comment_queue, (-comment.created_utc, comment.id, comment))
                                self.seen_comment_ids.add(comment.id)
                            new_comments.append(comment)

            if new_comments:
                # Signal that new comments are available
                self.new_comment_event.set()

            logger.info(f"Updated comments. Queue size: {len(self.comment_queue)}")
            time.sleep(10)  # Wait for 10 seconds before updating again

    def get_new_messages(self) -> list[str]:
        # Wait for new comments to be available
        self.new_comment_event.wait()

        # Get the 3 most recent comments from the priority queue
        recent_comments = []
        with self.queue_lock:  # Ensure thread-safe access to the priority queue
            while len(self.comment_queue) > 0 and len(recent_comments) < 3:
                _, _, comment = heapq.heappop(self.comment_queue)
                recent_comments.append(comment.body)  # Add the comment body to the list

        # Reset the event if there are no more comments in the queue
        if len(self.comment_queue) == 0:
            self.new_comment_event.clear()

        return recent_comments