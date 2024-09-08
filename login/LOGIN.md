# Proof of concept
See `stockholm_sso_poc.py` for a proof of concept login through Stockholms stad

# The process of logging in with skolplattformen
**Something that should be noted is that I don't have access to the normal user+pass login, or any other SSO login than skolplattformen. Anyone who is willing to help here is very welcome to!**

The login process is quite extrordinary for this application. 
Don't forget to save all cookies in some sort of session since you will need them throughout the whole process and later!

1. Make a request to `https://sso.infomentor.se/login.ashx?idp=stockholm_stu` and make sure to enable redirects
2. After all redirects you'll be at `https://login001.stockholm.se/siteminderagent/forms/aelever.jsp`. 
    - To log in using user+pass you need to extract the line containing `loginForm.jsp`. You can do this with this regex `^.*loginForm.*$`
    - Next you need to extract the path with the parameters. That is possible with this regex `(")([^"]*)(")`.
    - Now append the path with the parameters to the url `https://login001.stockholm.se/siteminderagent/forms/` and make a request
3. Next you need to take the response and get all the parameters which is in a form
    - First filter out the all the lines matching this regex and save the first 7 items. `^.*value.*$` (don't forget multiline and ignorecase!)
    - Next loop over and filter out the actual value and name and add these as parameters. Regex (save group 2 and 4, ignore_case) `(?:NAME=([\"']?)([^\s\"']*)\1\s*VALUE=([\"']?)([^\s\"']*)\3)`
    - Lastly add the username and password as parameters named `user` and `pass` and make a post request with the data to `https://login001.stockholm.se/siteminderagent/forms/login.fcc`
4. The login will now do some redirects until it reaches `login001.stockholm.se/affwebservices/public/saml2sso`, where you'll have to extract a value named SAMLResponse
    - The process is very much alike before. First regex with multiline on the response `^.*SAMLResponse.*$`
    - Now extract the value from the html line `(?:value=([^\"]*)\"([^\"]*)\")` and grab group 1 from the regex match
5. Take the SAMLResponse and post the data to `https://sso.infomentor.se/login.ashx?idp=stockholm_stu`. The json parameter is named `SAMLResponse`
    - On this page you once again have to extract some data. First regex to find the line `^.*oauth_token.*$`
    - Then extract the actual oauth_token `(?:value=([^\"]*)\"([^\"]*)\")` and grab group 1
6. Lastly, make a post request to `https://infomentor.se/swedish/production/mentor/` with the oauth token. The json parameter name is `oauth_token`

Congratulations! If you have saved your cookies throughout this session you should now be logged in and authenticated. 

You can check if you are authenticated or not by making a post request with no data to `https://hub.infomentor.se/authentication/authentication/isauthenticated` which returns a boolean.

## NOTE: You cannot be logged in at 2 places at the same time. This will trigger a forced login-loop.