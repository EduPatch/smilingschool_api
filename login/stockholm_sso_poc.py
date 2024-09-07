'''
MIT License

Copyright (c) 2024 Alexander Hübner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import requests, re, pickle, sys

def main():
    session = craft_session()
    if len(sys.argv) < 2:
        # Function to handle skolplattformen
        samlresponse = login_to_sso(session)
        # Handle infomentor
        login_to_infomentor(session, samlresponse)
    else:
        with open(sys.argv[1], 'rb') as f:
            session.cookies.update(pickle.load(f))
    # Time to make our final request, to check if we are authenticated!
    response = session.post("https://hub.infomentor.se/authentication/authentication/isauthenticated")
    print(response.content, response.status_code)
    if input("Do you want to save cookies to log in more easily next time?(Y/N)").strip().lower() == "y":
        with open("cookiefile", 'wb') as f:
            pickle.dump(session.cookies, f)

def login_to_sso(session):
    # Start setting up login object. We will get back to this later!
    print("NONE OF THE DATA YOU INPUT IS SAVED ANYWHERE BY THIS PROOF OF CONCEPT!")
    username = input('Please input your username:').strip()
    password = input('Please input your password:').strip()
    login_data_dict = {
        "user": username,
        "password": password,
        "SMENC": "",
        "SMLOCALE": "",
        "target": "",
        "smauthreason": "",
        "smagentname": "",
        "smquerydata": "",
        "postpreservationdata": "",
        "submit": ""
    }

    # Start of the login procedure
    infomentor_login_ashx = "https://sso.infomentor.se/login.ashx?idp=stockholm_stu"
    # Since everything in between login.ashx and skolplattformen aelever.jsp is redirects we can let python handle it automatically for us!
    sso_login = session.get(infomentor_login_ashx, allow_redirects=True)
    extracted_login_option_line = re.search(r"^.*loginForm.*$", sso_login.content.decode('utf8'), re.MULTILINE).group()
    # Now we use the extracted login option to navigate to the page and gets its contents, so we once again can extract some data
    login_page = session.get("https://login001.stockholm.se/siteminderagent/forms/" + re.search(r'(")([^"]*)(")', extracted_login_option_line).groups()[1], allow_redirects=False)
    # loop over every value and its key
    for value in re.findall(r"^.*value.*$", login_page.content.decode('utf8'), re.MULTILINE | re.IGNORECASE)[:7]:
        # Catches name and value
        value = re.search(r"""(?:NAME=([\"']?)([^\s\"']*)\1\s*VALUE=([\"']?)([^\s\"']*)\3)""", value, re.IGNORECASE).groups()
        value = (value[1], None if value[3] == 'null' else value[3])
        # Now we are back at creating our login data parameters!
        # insert into our data dictionary
        login_data_dict[value[0]] = value[1]
    # Data is done, time to login!
    saml2sso_page = session.post("https://login001.stockholm.se/siteminderagent/forms/login.fcc", login_data_dict, allow_redirects=True)
    # Okay, almost done. We just have to extract the SAMLResponse and make our request to infomentor!
    samlresponse_line = re.search(r"^.*SAMLResponse.*$", saml2sso_page.content.decode('utf8'), re.MULTILINE).group()
    return re.search(r"""(?:value=([^\"]*)\"([^\"]*)\")""", samlresponse_line).groups()[1]

def login_to_infomentor(session, samlresponse):
    infomentor_login_page = session.post("https://sso.infomentor.se/login.ashx?idp=stockholm_stu", data={"SAMLResponse": samlresponse})
    # Now we have reached the infomentor sector. Time to get our oauth token from this page!
    oauth_token_line = re.search(r"^.*oauth_token.*$", infomentor_login_page.content.decode('utf8'), re.MULTILINE).group()
    oauth_token = re.search(r"""(?:value=([^\"]*)\"([^\"]*)\")""", oauth_token_line).groups()[1]
    # We logged in before in skolplattformen, but now its time to get oauth in infomentor
    # When we do this request we will reach the LoginCallback, which will finally grant us access to our beloved infomentor!
    session.post("https://infomentor.se/swedish/production/mentor/", data={"oauth_token": oauth_token})

def craft_session():
    r = requests.Session()
    r.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Referer": "https://infomentor.se/", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-site", "Sec-Fetch-User": "?1", "Priority": "u=0, i", "Te": "trailers"}
    return r
    
if __name__ == "__main__":
    main()