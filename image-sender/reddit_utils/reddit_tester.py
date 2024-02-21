import praw
from dotenv import load_dotenv
import os

load_dotenv()

reddit = praw.Reddit(
    client_id = os.getenv("REDDIT_CLIENT_ID"),
    client_secret = os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent = os.getenv("REDDIT_USER_AGENT")
)

subreddit_name = 'bostonceltics'

# subreddit = reddit.subreddit(subreddit_name)

# # pinned_posts = []
# # for submission in subreddit.hot(limit=5):
# #         if submission.stickied:
# #                 pinned_posts.append(submission)

# first_pin = subreddit.sticky(number=1)



submission_id = '19ax7b8'

submission = reddit.submission(id=submission_id)

print(submission.title)