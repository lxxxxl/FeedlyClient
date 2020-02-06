FeedlyClient
============

A client for Feedly.[feedly api](http://developer.feedly.com/)

# Usage
## Auth
At first, you can go to [feedly developer](http://developer.feedly.com/v3/sandbox/) to apply for a client id and client secret. Then you can go to feedly to obtain a code.

	FEEDLY_REDIRECT_URI = "http://fabreadly.com/auth_callback"
	FEEDLY_CLIENT_ID="client_id"
	FEEDLY_CLIENT_SECRET="client_secret"
	def get_feedly_client(token=None):
		if token:
			return FeedlyClient(token=token, sandbox=True)
		else:
			return FeedlyClient(
								client_id=FEEDLY_CLIENT_ID, 
								client_secret=FEEDLY_CLIENT_SECRET,
								sandbox=True
			)
	def auth(request):   
		feedly = get_feedly_client()
		# Redirect the user to the feedly authorization URL to get user code
		code_url = feedly.get_code_url(FEEDLY_REDIRECT_URI)    
		return redirect(code_url)

After getting a code, you may exchange it for an access token and a refresh token.

	def callback(request):
		code=request.GET.get('code','')
		if not code:
			return HttpResponse('The authentication is failed.')
		
		feedly = get_feedly_client()
		
		#response of access token
		res_access_token = feedly.get_access_token(FEEDLY_REDIRECT_URI, code)
		# user id
		if 'errorCode' in res_access_token.keys():
			return HttpResponse('The authentication is failed.')
			 
		id = res_access_token['id']
		access_token=res_access_token['access_token']

## get user's subscription
	def feed(access_token):
		'''get user's subscription'''
		feedly = get_feedly_client()
		user_subscriptions = feedly.get_user_subscriptions(access_token)
		
## get stream entries
	def get_entries(token, streamId, max_items_per_page):
		get_feedly_client().get_feed_content(
			token,
			streamId,
			m ax_items_per_page)

## mark/unmark as 'Read Later'
	# mark
	save_for_later(access_token, user_id, entry['id'])
	# unmark
	unsave_for_later(access_token, user_id, entry['id']):
	
# FeedlyClientWrapper
_fcw.py_ script performs download of all entries marked as 'Read Later'.
