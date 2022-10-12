class TooManyAuthenticationFailure(Exception):

    def __init__(self, account, ip):
        super().__init__()
        self.account=account
        self.ip = ip

