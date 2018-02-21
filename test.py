if request.args.get('state') != login_session['state']:
      response = make_response(json.dumps('Invalid state parameter.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response
  access_token = request.data

  print "access token received %s " % access_token
  #Exchange short lived token for long lived one. app_secret is sent to facebook.
  app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
  app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
  url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]

  # Use token to get user info from API
  userinfo_url = "https://graph.facebook.com/v2.8/me"
  # strip expire tag from access token
  token = result.split(',')[0].split(':')[1].replace('"', '')

  url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  data = json.loads(result)
  # sys.stdout = open('output.logs', 'w')
  # print (data["name"]) # Nothing appears below
  # print (data["email"]) # Nothing appears below
  # print (data["id"]) # Nothing appears below
  # sys.stdout = sys.__stdout__ # Reset to the standard output
  # open('output.logs', 'r').read()
  # return "OK"
  login_session['provider'] = 'facebook'
  login_session['username'] = data["name"]
  login_session['email'] = data["email"]
  login_session['facebook_id'] = data["id"]

  # The token must be stored in the login_session in order to properly logout
  login_session['access_token'] = token

  # Get user picture
  url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  data = json.loads(result)

  login_session['picture'] = data["data"]["url"]

  # see if user exists
  user_id = getUserID(login_session['email'])
  if not user_id:
      user_id = createUser(login_session)
  login_session['user_id'] = user_id
