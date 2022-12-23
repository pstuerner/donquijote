<p align="center">
<pre>
    ___              ____       _  _       _       
   /   \___  _ __   /___ \_   _(_)(_) ___ | |_ ___ 
  / /\ / _ \| '_ \ //  / / | | | || |/ _ \| __/ _ \
 / /_// (_) | | | / \_/ /| |_| | || | (_) | ||  __/
/___,' \___/|_| |_\___,_\ \__,_|_|/ |\___/ \__\___|
                                |__/               
</pre>
</p>

</br><hr></br>

<p align="center">
  <img src="bot_qr.png" alt="QR code for chatbot" style="width: 40%; height: 40%;">
</p>

</br><hr></br>

<p align="center">
¡Aprende Español de manera rápida y fácil!<br>
Las palabras más comunes a tu alcances
<p align="center">
Learn Spanish quickly and easily!<br>
The most common words at your fingertips
</br><hr></br>

<p align="center">
  Don Quijote, my noble guide<br>
  In La Mancha, by his side<br>
  I learned the language of Spain<br>
  Through his stories and his pain<br><br>
  His lessons were full of wit<br>
  As he taught me the words and how to fit<br>
  I learned to speak with grace<br>
  Thanks to Don Quijote's embrace<br><br>
  Now I can speak and understand<br>
  The beautiful tongue of this land<br>
  All thanks to my dear friend<br>
  Don Quijote, until the very end
</p>

</br><hr>

<ol>
  <li>Introduction</li>
  <li>Functionalities</li>
  <li>Further Ideas</li>
</ol>

<h3>Introduction</h3>

<p>
This chatbot is designed to help users learn and practice the most frequently used Spanish words in a convenient and interactive way. Built using Python and the <a href="https://github.com/python-telegram-bot/python-telegram-bot" target="_blank">python-telegram-bot</a> framework, the chatbot is able to register new users, change user settings, send daily reminders to practice vocabulary, and test users' knowledge of their learned words. The chatbot can be easily deployed using docker-compose and two Dockerfiles, ensuring it can run nonstop. All that's required is a running MongoDB with a couple of existing collections.
</p>
<p>
You can run the chatbot by yourself. All you need is a bot token that you can create in the Telegram app and a vocabulary collection in your MongoDB with documents in the following format:</br>
<pre>
{
    "vocab_id" : NumberInt(45),
    "freq" : NumberInt(46),
    "abbr" : "nm",
    "sp" : "año",
    "en" : "year",
    "sentence-sp" : "no lo supo hasta casi un año después",
    "sentence-en" : "he didn’t find out until almost a year later",
    "freq_gen" : NumberInt(37168),
    "freq_web" : NumberInt(3792004),
    "genres" : []
}
</pre>
</p>
<p>
Of course it's easier to use my already running version of the DonQuijote bot :) You can find it on Telegram by searching for the following user
</p>
<p align="center">
<b><span style="display: block; text-align: center;">@donquijote_ps_bot</span></b>
</p>
<p>
or scanning the following QR code
</p>
<p align="center">
  <img src="bot_qr.png" alt="QR code for chatbot" style="width: 50%; height: 50%;">
</p>
<p>
and simply initiate the conversation by sending /start.
</p>

<h3>Functionalities</h3>
<p>
This are the main conversation entrypoints of the chatbot.
<h5>/start</h5>
<p>This command begins the conversation with the chatbot and initiates the user setup process. The chatbot will ask the user for their name and preferred learning schedule, such as the number of words they want to learn per day. This information is used to customize the chatbot's interactions with the user and ensure an optimal learning experience.</p>

<h5>/settings</h5>
<p>This command allows the user to change their personal settings, such as their name and learning schedule. The user can use this command at any time to update their information and customize their learning experience with the chatbot.</p>

<h5>/play</h5>
<p>This command initiates a vocabulary practice session with the chatbot. The chatbot will send the user English words and wait for a response. The chatbot will continue sending words until all picked words have been guessed correctly. If the chatbot marks the user's response as incorrect but the user is sure that it was correct, they can send the command <b>/counts</b> to correct the mistake and ensure an accurate evaluation of their vocabulary knowledge. This feature is useful for handling typos or autocorrect issues.</p>

<h5>/learn</h5>
<p>This command allows the user to choose specific word genres to focus on during their learning sessions with the chatbot. The chatbot provides a range of options, such as verbs, adjectives, and nouns, and lets the user decide if they want to learn more or less frequent Spanish words. This feature allows the user to tailor their learning experience to their specific needs and interests.</p>

<h5>/cancel</h5>
<p>This command allows the user to leave a conversation with the chatbot. The user can use this command at any time to end the current interaction and return to the chatbot's main menu.</p>
