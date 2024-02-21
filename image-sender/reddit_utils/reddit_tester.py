import praw

reddit = praw.Reddit(
    client_id="aok8zQ9Tq1GXHLFz3OeEiQ",
    client_secret="DJwveTOOEhWfKZ4a-sghgSdJBrLFWw",
    user_agent="Celtics Live 1.0 by /u/jkcars"
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

