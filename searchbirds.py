from model import User, Bird, Observation, connect_to_db, db
import pprint

def birdsearch(this_user_id = None, bird_limit = "all", spuh = "all", order="all", family = "all", region = "all", other=None):
	""" 
	I take parameters from the server and return a list of orders and a dictionary like so:
	dict = {order: {family_1: {birdA: {bird: data}, birdB: {bird: data}}}}
	"""
	
	def test_for_semicolons(term):
		"""
		Take a str and look for any semicolons.

		Returns True if no semicolons are found (true = probably not malicious input)
		"""

		if term.find(';') == -1:
			return True
		else:
			return False

	semicolon_test_results = map(test_for_semicolons, locals().keys())

	if False in semicolon_test_results:
		return "Semicolons are not allowed in birdsearch inputs."


	# begin building an SQL query
	q = Bird.query
	print "Running query"

	# If the user is filtering by whether or not a bird is on their life list
	if bird_limit != "all":
		print "bird limit var: ", bird_limit  
		print "user id: ", this_user_id 
		obs_query = db.session.query(Observation.bird_id).filter(Observation.user_id == this_user_id)
		obs_list = [obs[0] for obs in obs_query.all()]

		# Only show birds the user HAS seen.
		if bird_limit == "my_birds": # this will be called with "my_birds" whenever a logged in user loads the homepage.
			q = q.filter(Bird.taxon_id.in_(obs_list))

		# only show birds the user HAS NOT seen.
		elif bird_limit == "not_my_birds":
			q = q.filter(~Bird.taxon_id.in_(obs_list))

	# right now, "spuh" is just another way of picking an order
	if spuh != "all":
		print "spuh: ", spuh, type(spuh)
		order = spuh

	if order !="all": 
		print "order ", order, type(order)
		q = q.filter_by(sp_order = order)

	if family != "all":
		q = q.filter_by(sp_family = family)

    # search inside the region field
	if region != "all":
		print "region ", region
		q = q.filter(Bird.region.like('%'+region+'%'))

    # put the final query in order by taxon ID but this doesn't work anymore
	#q = q.order_by(Bird.taxon_id)

	##### Now the query that has been built is run several times.

	# Run once to get a list of bird objects. This is in order but the order is not maintained.
	birds = q.order_by(Bird.taxon_id).all()

	# Run once to get a list of family objects
	#families_objects = q.group_by(Bird.sp_family).with_entities(Bird.sp_family).all()

	# Run once to get a list of order objects
	orders_objects = q.group_by(Bird.sp_order).with_entities(Bird.sp_order).all()

	# generate a list of orders as ascii strings.
	orders_list = [order.sp_order.encode('ascii', 'ignore') for order in orders_objects]

	# begin the big dictionary of birds with the orders (strings) as keys.
	birds_dict = {order: {} for order in orders_list}

	# for each order, query for the birds with that order. Group by family and add to dict
	for order in birds_dict.keys():
		families_list = q.filter_by(sp_order = order).group_by(Bird.sp_family).with_entities(Bird.sp_family).all()
		birds_dict[order] = {family[0].encode('ascii', 'ignore'): {} for family in families_list}

	# add birds to the big dictionary of birds.
	# Pull relevant data out of each bird object.
	for bird in birds:
		birds_dict[bird.sp_order.encode('ascii', 'ignore')][bird.sp_family.encode('ascii', 'ignore')][bird.taxon_id.encode('ascii', 'ignore')] = {'order': bird.sp_order.encode('ascii', 'ignore'), 
																												  'family': bird.sp_family.encode('ascii', 'ignore'), 
																												  'sci_name': bird.sci_name, 
																												  'common_name': bird.common_name,
																												  'region': bird.region}

	return {"birds_dict": birds_dict,
			"orders" : orders_list}
