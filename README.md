# Using Python, Flask, SocketIO, Gevent, and Twitter API that creates a web app that displays photos from cat-related Tweets in real time

1. Client runs FLASK_APP=catapp.py flask run in the command line.
2. Server opens the following URL in browser: http://127.0.0.1/:5000.
3. Tweets stream in, however, the Tweets do not display to console. 	
4. The next steps would be to debug the code, and to search for the following extended entities (“type": "photo”, “display_url”, “sizes” “thumb” and entities with the following hashtags - #cat, #cats, #kittentoday, #instacats, #instacat, #kitty, #catsofinstagram, #CatsOfTwitter, #catstagram, #cutecats, #kittycat, #RealGrumpyCat)
