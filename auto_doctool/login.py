import requests, re, pickle, sys

class Im:
    def __init__(self, cookiefile: None):
        self.session = self.craft_session()
        login_with_file_response = self.login_with_cookie(cookiefile)
        if login_with_file_response != 0:
            samlresponse = self.login_to_sso()
            self.login_to_infomentor(samlresponse)
            response = self.session.post("https://hub.infomentor.se/authentication/authentication/isauthenticated")
            if response.content != b'true':
                print("Auth failed")
                exit(1)
            print("Auth success")
            if input("Do you want to save cookies to log in more easily next time?(Y/N)").strip().lower() == "y":
                with open("cookiefile", 'wb') as f:
                    pickle.dump(self.session.cookies, f)

    def login_with_cookie(self, file):
        if file is not None:
            with open(file, 'rb') as f:
                    self.session.cookies.update(pickle.load(f))
            response = self.session.post("https://hub.infomentor.se/authentication/authentication/isauthenticated")
            #print(response.content)
            #oauth_token_line = re.search(r"^.*oauth_token.*$", response.content.decode('utf8'), re.MULTILINE).group()
            #oauth_token = re.search(r"""(?:value=([^\"]*)\"([^\"]*)\")""", oauth_token_line).groups()[1]
            #session.post("https://infomentor.se/swedish/production/mentor/", data={"oauth_token": oauth_token})
            if response.content != b'true':
                print("Auth failed, login please")
                return 1
            print("Auth success")
            return 0
        else:
            return 1

    def login_to_sso(self):
        session = self.session
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
        infomentor_login_ashx = "https://sso.infomentor.se/login.ashx?idp=stockholm_stu"
        sso_login = session.get(infomentor_login_ashx, allow_redirects=True)
        extracted_login_option_line = re.search(r"^.*loginForm.*$", sso_login.content.decode('utf8'), re.MULTILINE).group()
        login_page = session.get("https://login001.stockholm.se/siteminderagent/forms/" + re.search(r'(")([^"]*)(")', extracted_login_option_line).groups()[1], allow_redirects=False)
        for value in re.findall(r"^.*value.*$", login_page.content.decode('utf8'), re.MULTILINE | re.IGNORECASE)[:7]:
            value = re.search(r"""(?:NAME=([\"']?)([^\s\"']*)\1\s*VALUE=([\"']?)([^\s\"']*)\3)""", value, re.IGNORECASE).groups()
            value = (value[1],  value[3])
            login_data_dict[value[0]] = value[1]
        saml2sso_page = session.post("https://login001.stockholm.se/siteminderagent/forms/login.fcc", login_data_dict, allow_redirects=True)
        samlresponse_line = re.search(r"^.*SAMLResponse.*$", saml2sso_page.content.decode('utf8'), re.MULTILINE).group()
        return re.search(r"""(?:value=([^\"]*)\"([^\"]*)\")""", samlresponse_line).groups()[1]

    def login_to_infomentor(self, samlresponse):
        session = self.session
        infomentor_login_page = session.post("https://sso.infomentor.se/login.ashx?idp=stockholm_stu", data={"SAMLResponse": samlresponse})
        oauth_token_line = re.search(r"^.*oauth_token.*$", infomentor_login_page.content.decode('utf8'), re.MULTILINE).group()
        oauth_token = re.search(r"""(?:value=([^\"]*)\"([^\"]*)\")""", oauth_token_line).groups()[1]
        session.post("https://infomentor.se/swedish/production/mentor/", data={"oauth_token": oauth_token})
        session.get("https://hub.infomentor.se/#/")

    def craft_session(self):
        r = requests.Session()
        r.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Origin": "https://hub.infomentor.se", "Referer": "https://hub.infomentor.se/", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-site", "Sec-Fetch-User": "?1", "Priority": "u=0, i", "Te": "trailers"}
        return r
    

    def post(self, url, allow_redirects=True, params=None, data=None):
        return self.session.post(url, data=data if data != None else {}, params=params if params != None else {}, allow_redirects=allow_redirects)
    def get(self, url, allow_redirects=True, params=None):
        return self.session.get(url, params=params if params != None else {}, allow_redirects=allow_redirects)