# Survey of Political Bots on Twitter

This repo is a collection of the code and a limited amount of the data I collected for my Masters Thesis.



## Overview

1. I used [Botcheck](https://botcheck.me/) to find hashtags that were popular with political bots on Twitter. 

![Alt Text](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/Images/TopHashTagsSample.png).

2. I filtered the Twitter Stream on those popular hashtags using [this script](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/StreamingCode/start_stream.py). This allowed me to collect hundreds of thousands of Twitter accounts that were tweeting on political hashtags in 2018. This data collection was sporadic during the summer of 2018 and ended with a focus on bots tweeting about the Brett Kavanaugh confirmation.

3. After collecting political Accounts I obtained each account's CAP (complete automation probability) using [Botometer](https://botometer.iuni.iu.edu/#!/) via [this script](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/BotometerCode/start_botometer.py).

4. I set a CAP score threshold for humans and bots based on previous [research](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/Research/%5B20%5D%20Measuring%20bot%20and%20human%20behavioral%20dynamics%20(used%20Botometer).pdf)

![Alt Text](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/Images/Botometer%20CAP%20Score%20Frequency.png)

5. I trained an [initial model](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/MachineLearningNotebooks/Initial%20ML%20Model.ipynb) to classify Twitter accounts using only their [profile](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/user-object.html) information.

6. I order to assess Twitter's response to political bots I rechecked every account initially classified at a bot (21,418) using Botometer a again. This allowed me to obtain a second CAP score some accounts remained bots (7,496 or ~35%), other accounts were removed presumably due to bot behavior (9,126 or ~43%), and a surprising amount were no longer classified as bots (3,378 or ~16%) classified as human and (1,417 or ~6%) as unknown.

![Alt Text](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/Images/Old%20CAP%20vs%20New%20CAP%20for%20Bots.png)


7. I then trained [new models](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/tree/master/MachineLearningNotebooks) using only the removed bots, and only twice classified bots.

![Alt Text](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/Images/ModelAccuracy.png)


8. I analyzed bots observed tweeting during the controversial [Brett Kavanaugh Supreme Court Nomination](https://en.wikipedia.org/wiki/Brett_Kavanaugh#Sexual_assault_allegations) and compared them to the bots previously observed.

![Alt Text](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/Images/Before%20Kavanaugh%20Account%20Age%20Distribution.png)

![Alt Text](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/Images/Kavanaugh%20Account%20Age%20Distribution.png)

9. Results

**New political bot accounts are created in real-time to respond to political crises**

![Alt Text](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/Images/Account%20Age%20Distribution.png)

**Political bots are more active during these crises**

#### Before Kavanaugh Nomination:

- 408,220 total accounts
- 9,991 bot accounts
- 775,609 tweets sent
- **Bots sent  24,568  tweets or  3.17 % of tweets**
- **Percentage of total accounts that are bots = 2.45%**
- Percentage of total accounts that are humans = 96.42%
- Percentage of total accounts that are unknown = 1.13%
- Overall average account age in days  1,686.679991181226
- Average bot account age in days  698.6344710239215
- Average human account age in days  1,719.1844113612112
- Overall average CAP score  0.05379225294931851
- Average human CAP score  0.03217073246946307
- Average bot CAP score  0.7198592500519072

#### During Kavanaugh Nomination:

- 287,307 total accounts
- 11, 427 bot accounts
- 412,814 tweets sent
- **16,601 tweets or  4.02 % of tweets**
- **Percentage of total accounts that are bots = 3.98%**
- Percentage of total accounts that are humans = 94.12%
- Percentage of total accounts that are unknown = 1.9%
- Overall average account age in days  1,599.7171736156795
- Average bot account age in days  613.3258948105364
- Average human account age in days  1,656.9227358455678
- Overall average CAP score  0.07367285204538905
- Average human CAP score  0.039484313069561155
- Average bot CAP score  0.6990314467440416

**The number of tweets an account has favorited is a strong indicator of bot status**

![Alt Text](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/Images/Average%20Tweets%20Per%20Day.png)




## TLDR

I used machine learning to classify political Twitter accounts as bot or human based on only their user profile.




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

Bots are software applications that execute automated tasks called scripts over the Internet. Bots have become predominant on social media platforms like Twitter, and automate their interactions with other users. Political Twitter bots have emerged that focus their activity on elections, policy issues, and political crises. These political bots have faced increased scrutiny as a result of their association with online manipulation via the spread of misinformation. As bots have become more sophisticated, research has focused on advanced methods to detect their presence on social media platforms. However, little research has been performed on the overall presence of political bots and their dynamic response to political events. The research that has been performed on political bots focuses on these bots in the context of scheduled political events, such as elections. In this paper, we explore the bot response to an unexpected political event, describe the overall presence of political bots on Twitter, and design and employ a model to identify them based on their user profile alone. We collected data for more than 700,00 accounts tweeting with hashtags related to political events in the United States between May 2018 and October 2018. We designed a machine learning algorithm using user profile features alone that achieves approximately 97.4% accuracy in identifying political Twitter bots. In our analysis, **we found (1) new bot accounts are created in response to political events, (2) bot accounts are more active during political controversies, (3) the number of tweets an account has favorited (liked) is a strong determinant of bot status.** [Full paper](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/David%20Troupe%20-%20Masters%20Thesis%20-%20Survery%20of%20Political%20Bots%20on%20Twitter.pdf)    [Slides](https://github.com/dtroupe18/Thesis-Survey-Of-Political-Bots-On-Twitter/blob/master/ThesisDefenseSlides.pdf)


## Link to Data Samples
[Sample Data on Google Drive](https://drive.google.com/drive/folders/1h5TKuJu9VH5C_AcOp47l5f_Mw5QBuKl1?usp=sharing)

* Data Sample
    * **AllUserProfilesWithCapScores.csv** - Approximately 700,000 Twitter accounts with CAP scores from Botometer.
    * **AllBots.csv** - All Twitter accounts with a CAP score over 0.53 (bot threshold).
    * **AllRemovedBots.csv** - All Twitter bots that were removed from Twitter during data collection.
    * **StillActiveBots.csv** - All Twitter bots that were not removed from Twitter during data collection.
    * **RemovedAndStillActiveBots.csv** - Combined file with all removed and still active bots.
    * **StillActiveNotBot.csv** - Accounts that were initially classified as a bot but now have CAP < 0.53.
    * **StillActiveUnknownStatus.csv** - Accounts originally classified as a bot, but now have a CAP between 0.4 - 0.53.


