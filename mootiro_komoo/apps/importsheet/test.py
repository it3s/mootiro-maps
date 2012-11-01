from gdata.spreadsheets.client import SpreadsheetsClient
from gdata.gauth import AuthSubToken
import feedparser

access_token = 'ya29.AHES6ZQdeMTALUpatmy5yDdTH5okGwZANB3lVF1HULzhaFjS'
tok = AuthSubToken(token_string=access_token)
key = '0Ahdnyvg2LXX-dDFITkdXd0hBNFBDczA4RFV2dVBVM0E'
cs = SpreadsheetsClient()
data = cs.get_list_feed(key, 'od6', auth_token=tok)
d = feedparser.parse(str(data))

# ... d is a browseable dict ... Good Luck!
