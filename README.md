# ChatBotTest
Chat bot that converts audio to wav format with a sampling rate of 16kHz, detects faces on the photos an uploads these audio files and photos to FireBase.

This telegram bot has 2 functions:
1) Save audio messages from dialogues to a FireBase database by user IDs. Audio is converted to wav format with a sampling rate of 16kHz.
2) Determines whether there is a face in the photos being sent or not, uploads photos with faces to a FireBase.

This bot uses Firebase as a Database and requires:
1) Bot token
2) Bot username
3) Dowload firebase-adminsdk.json from Firebase and it's path
4) Project id to put it in "initialize_app(cred, {'storageBucket': 'your-project-id.appspot.com'})"

And to create Bot using BotFather.

After this the bot should be up and run without a problem.
