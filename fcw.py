from client import FeedlyClient
import webbrowser
from bottle import template
import json
import datetime
import re
import pdfkit
import signal



class FeedlyClientWrapper(object):
    config_filename = 'config.json'
    config = None
    feedly_client = None
    sandbox = False
    sigint_received = False
    
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.sigint_handler)
    
    def sigint_handler(self, sig, frame):
        print('Exiting...')
        self.sigint_received = True
    
    
    def get_config(self):
        if self.config == None:
            with open(self.config_filename, 'r') as read_file:
                self.config = json.load(read_file)
        return self.config

    def get_feedly_client(self):
        if self.feedly_client != None:
            return self.feedly_client
        else:
            if self.get_config()['token']:
                self.feedly_client = FeedlyClient(token=self.get_config()['token'], sandbox=self.sandbox)
            else:
                self.feedly_client = FeedlyClient(
                            client_id=self.get_config()['client_id'], 
                            client_secret=self.get_config()['client_secret'],
                            sandbox=self.sandbox
                            )
            return self.feedly_client
            
    def process_authentication(self):
        if not self.get_config()['token']:
            #should authenticate user
            self.authenticate()
        else:
            print('Already authenticated')
            
    def authenticate(self):   
        # Redirect the user to the feedly authorization URL to get user code
        webbrowser.open(self.get_feedly_client().get_code_url(self.get_config()['redirect_uri']))
        # TODO
        # process second phase of authentication
    
    def set_token(self,token):
        self.get_config()['token'] = token
        with open(self.config_filemname, 'w') as write_file:
            json.dump(self.get_config(), write_file)

    def download_saved_for_later(self, html_filename, save_to_pdf=False):

        
        streamId = 'user/{}/tag/global.saved'.format(self.get_config()['client_id'])
        entries = self.get_feedly_client().get_feed_content(self.get_config()['token'], streamId, self.get_config()['max_items'])
        
        html_file = open(html_filename,'ab')
            
            
        while True:
            if not entries:
                return
        
            print('Entries found: {}'.format(len(entries['items'])))
        
            output_html = u''
            entries_to_unsave = []
        
            for item in entries['items']:
                print('Processing {}'.format(item['id']))
                entries_to_unsave.append(item['id'])
                item_info = {}
                item_info['url'] = item['originId']
                item_info['name'] = item['title']
                keywords = ', '
                item_info['keywords'] = ''
                if 'keywords' in item:
                    item_info['keywords'] = keywords.join(item['keywords'])
                item_info['img'] = ''
                if 'visual' in item and 'url' in item['visual']:
                    item_info['img'] = item['visual']['url']
                item_info['desc'] = item['summary']['content']
                item_info['desc'] = re.sub('<img[^<]+?>', '', item_info['desc'])	# strip images from descrtiption
                output_html += template('template.html', item_info)
            
                if save_to_pdf:
                    pdfkit.from_url(item_info['url'] , '{}.pdf'.format(item_info['name'][:40]))
                
            html_file.write(output_html.encode('utf-8').strip())          
            self.get_feedly_client().unsave_for_later(self.get_config()['token'], self.get_config()['client_id'], entries_to_unsave)
            
            if self.sigint_received:
                return
            
            if 'continuation' in entries:
                entries = self.get_feedly_client().get_feed_content(self.get_config()['token'], streamId, self.get_config()['max_items'], entries['continuation'])
            else:
                return
            
    
if __name__ == '__main__':
    
    client = FeedlyClientWrapper()
    client.process_authentication()
    client.download_saved_for_later('{}.html'.format(datetime.date.today().strftime('%Y%m%d')))
    
        
