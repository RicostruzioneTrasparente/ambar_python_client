import os, sys, requests, logging
logging.basicConfig(level=logging.INFO)

class Ambar():

    def __init__(self, email = "", password = "", host = "localhost:80"):

        self.email = email
        self.password = password
        self.host = host if host.startswith("http") else "http://%s" % host
        self.auth(self.email, self.password)

    def auth(self, email = "", password = ""):

        email = email or self.email
        password = password or self.password
        logging.debug("Email: %s - Password: %s" % ( email , '*'*len(password) ))

        if not email or not password:
            logging.error("Error, you must provide auth credentials!")
            return self

        # POST /api/users/login
        req = requests.post(
            "%s/api/users/login" % self.host,
            headers = {
                "ambar-email": "null",
                "ambar-email-token": "null",
                "content-type": "application/json",
                "accept": "application/json"
            },
            json = {
                "email": email,
                "password": password
            }
        )

        if req.status_code == 200:
            res = req.json()
            self.token = res['token']
            logging.debug("Token: %s" % self.token)
            return self
        else:
            logging.error("Error %d in authentication process: %s" % ( req.status_code , req.text ))
            return

    def put(self, filename = "", source = "Default"):

        if not filename:
            logging.error("Error, you must provide the name of an existing file!")
            return {}

        if not self.token:
            self.auth()

        # POST /api/files/:source/:filename
        req = requests.post(
            "%s/api/files/%s/%s" % ( self.host , source , os.path.basename(filename) ),
            headers = {
                "ambar-email": self.email,
                "ambar-email-token": self.token
            },
            files = { "file": ( os.path.basename(filename) , open(filename,"rb") ) }
        )

        if req.status_code == 200:
            logging.debug("Ok! %s" % req.text)
            res = req.json()
            self.last_meta_id = res['metaId']
            return res
        else:
            logging.warning("Warning, received a %d response: %s" % ( req.status_code , req.text ))
            return {}

    def search(self, query = "", size = 10, page = 0):

        if not query:
            logging.error("Error, you must provide a query string!")
            return []

        if not self.token:
            self.auth()

        # GET /api/search
        req = requests.get(
            "%s/api/search" % self.host,
            headers = {
                "ambar-email": self.email,
                "ambar-email-token": self.token
            },
            params = {
                "query": query,
                "size": size,
                "page": page
            }
        )

        if req.status_code == 200:
            res = req.json()
            logging.info("Ok, found %d matching documents!" % len(res['hits']))
            return res['hits']
        else:
            logging.warning("Warning, received a %d response: %s" % ( req.status_code , req.text ))
            return []

    def scan(self, query = "", size = 10):

        if not query:
            logging.error("Error, you must provide a query string!")
            return {}

        if not self.token:
            self.auth()

        page = 0
        while True:

            docs = self.search(query,size,page)
            if not docs:
                break

            for doc in docs:
                yield doc

            page += 1

    def check(self, id = ""):
        return bool(self.get_meta(id))

    def get_meta(self, id = ""):
        res = self.get("meta",id)
        if res is not None:
            return res.json()

    def get_text(self, id = ""):
        res = self.get("text",id)
        if res is not None:
            return res.text

    def get_source(self, id = ""):
        res = self.get("source",id)
        if res is not None:
            return res.raw

    def get(self, action = "", id = ""):

        if not action:
            logging.error("Error, you must provide an action!")
            return

        id = id or self.last_meta_id
        if not id:
            logging.error("Error, you must provide a document id!")
            return

        # GET /api/files/direct/:id/:action
        req = requests.get(
            "%s/api/files/direct/%s/%s" % ( self.host , id , action ),
            headers = {
                "ambar-email": self.email,
                "ambar-email-token": self.token
            }
        )

        if req.status_code == 200:
            logging.info("Ok, found data for %s document!" % id)
            return req
        else:
            logging.warning("Warning, received a %d response: %s" % ( req.status_code , req.text ))


if __name__ == "__main__":

    if len(sys.argv) > 2:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        logging.error("Error, you must provide auth credentials!")

    if len(sys.argv) > 3:

        host = sys.argv[3]

        ambar = Ambar(
            email = email,
            password = password,
            host = host
        )

    else:

        ambar = Ambar(
            email = email,
            password = password
        )

    if ambar.token:
        print("It works!")

