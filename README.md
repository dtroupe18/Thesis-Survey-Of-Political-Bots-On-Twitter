# Survey of Political Bots on Twitter

This repo is a collection of the code and a limited amount of the data I collected for my Masters Thesis.

**TLDR** - I used machine learning to classify political Twitter accounts as bot or human based on only their user profile.





## Resources

[Botometer](https://botometer.iuni.iu.edu/#!/) - Provided classification for training data.

[Botometer API](https://github.com/IUNetSci/botometer-python/blob/master/botometer/__init__.py) - Provided base Python code to make Botometer API requests.

[Botcheck](https://botcheck.me/) - Provided trending political bot hashtags to filter the [Twitter Stream](https://developer.twitter.com/en/docs/tutorials/consuming-streaming-data.html).

[Twitter API](https://developer.twitter.com/en/docs.html) - Provided tweet and user profile data collection.

[Twitter Application](https://developer.twitter.com/en/docs/basics/apps.html) - Provided the ability to create my own [Twitter bot](https://twitter.com/BotDetectionBot) 





## Libraries Used

[Tweepy](http://www.tweepy.org/) - An easy-to-use Python library for accessing the Twitter API.

[Scikit-learn](https://scikit-learn.org/stable/) - Machine Learning in Python.

[Pandas](https://pandas.pydata.org/) - Python Data Analysis Library.

[Matplotlib](https://matplotlib.org/) - Matplotlib is a Python 2D plotting library which produces publication quality figures in a variety of hardcopy formats and interactive environments across platforms. 





## Abstract

Bots are software applications that execute automated tasks called scripts over the Internet. Bots have become predominant on social media platforms like Twitter, and automate their interactions with other users. Political Twitter bots have emerged that focus their activity on elections, policy issues, and political crises. These political bots have faced increased scrutiny as a result of their association with online manipulation via the spread of misinformation. As bots have become more sophisticated, research has focused on advanced methods to detect their presence on social media platforms. However, little research has been performed on the overall presence of political bots and their dynamic response to political events. The research that has been performed on political bots focuses on these bots in the context of scheduled political events, such as elections. In this paper, we explore the bot response to an unexpected political event, describe the overall presence of political bots on Twitter, and design and employ a model to identify them based on their user profile alone. We collected data for more than 700,00 accounts tweeting with hashtags related to political events in the United States between May 2018 and October 2018. We designed a machine learning algorithm using user profile features alone that achieves approximately 97.4% accuracy in identifying political Twitter bots. In our analysis, we found (1) new bot accounts are created in response to political events, (2) bot accounts are more active during political controversies, (3) the number of tweets an account has favorited (liked) is a strong determinant of bot status. [Full paper](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/David%20Troupe%20-%20Masters%20Thesis%20-%20Survery%20of%20Political%20Bots%20on%20Twitter.pdf)    [Slides](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/ThesisDefenseSlides.pdf)


## Link to Data Samples
[Sample Data on Google Drive](https://drive.google.com/drive/folders/1h5TKuJu9VH5C_AcOp47l5f_Mw5QBuKl1?usp=sharing)

* Data Sample
    * AllUserProfilesWithCapScores.csv - Approximately 700,000 Twitter accounts with Bot and CAP scores from Botometer.
    * AllBots.csv - All Twitter accounts with a CAP score over 0.53 (bot threshold).
    * AllRemovedBots.csv - All Twitter bots that were removed from Twitter during data collection.
    * StillActiveBots.csv - All Twitter bots that were not removed from Twitter during data collection.
    * RemovedAndStillActiveBots.csv - Combined file with all removed and still active bots.
    * StillActiveNotBot.csv - Accounts that were originally classified as a bot but now have CAP < 0.53 (After recheck).
    * StillActiveUnknownStatus.csv - Accounts originally classified as a bot, but now have a CAP between 0.4 - 0.53.


