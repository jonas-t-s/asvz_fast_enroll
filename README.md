# PoW: ASVZ fast enroll  

This is a small python script that enrolls you (a student of ETH) in asvz classes that require registration (all of them as of summer 2020).

The code logs in before the start of the enrollment and then just posts the enrollment request. This should be faster than a pure selenium registration.

Please get in touch if the script is broken or you need help. 

## Getting Started (log in once)
1. Install Selenium [chromedriver](https://chromedriver.chromium.org/getting-started#Setup) or [geckodriver](https://github.com/mozilla/geckodriver/releases) for [Selenium](http://www.seleniumhq.org/)
2. Clone this repo
3. Install python requirements `pip -r install requirements.txt`
4. Save your netz username and password in a file `credentials.json` in the same folder ```{"username":"your_username", "password":"your_password"}```. Your credentials are only used to login with switch.
5. (Run test with `python3 test.py`)
6. Call `asvz\_register.py <lesson_id>` with find course on asvz, copy the lesson id from the url. 
   Example: for https://schalter.asvz.ch/tn/lessons/95699 `asvz\_register.py 95699`

The script will retrieve the enrollment time and wait for it to start before trying the login. The script must be running to enroll so keep it on a server or some other machine that is online until the enrollment starts.

## I realised to late, that I want a class and now it is full:
It is easy to say, that you should have done it already with the upper script. But however if you're lucky there is somebody who does unregister and you may get this place. 
You just use the script: `python3 waitforempty.py <lesson_id>` and then you just hope you get lucky. If there is a free place you will automatically get enrolled. 
## Acknowledgments

* Inspired by the code of [ChenChen](https://github.com/ChenchenYo/LoginCode)
* The code in this repository is forked and extended from [uniquefine](https://github.com/uniquefine/asvz_fast_enroll)