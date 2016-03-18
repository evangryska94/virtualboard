import tornado.web
import tornado.websocket
import json
import jsonschema

from lobby import *

class WebSocketGameHandler(tornado.websocket.WebSocketHandler):
	def open(self, *args):
		self.game = None
		self.name = None
		self.user_id = None

	def on_message(self, message):
		print(message)

		try:
			data = json.loads(message);
		except ValueError, e:
			response = {
				"type" : "error",
				"data" : [
					{
						"msg" : "invalid json message"
					}
				]
			}
			self.write_message(json.dumps(response));
			return

		#Checking whether the message follows the protocol
		#schema = open("socket_protocol_schema.json").read()
		#try:
		#    jsonschema.validate(data, json.loads(schema))
		#except:
		#	print "bad json input, continuing anyway"
		#except jsonschema.ValidationError as e:
    	#	print e.message
		#except jsonschema.SchemaError as e:
    	#	print e

		if data["type"] == "ping":
			response = {
				"type" : "pong",
				"data" : [
					data["data"]
				]
			}
			self.write_message(json.dumps(response))
		elif self.game is None:
			#TODO: error checking and format validation
			if data["type"] == "initHost":
				self.name = data["data"]["name"]
				self.color = data["data"]["color"]
				global next_game_id
				game = Game(data["data"]["gameName"], data["data"]["password"], self, next_game_id)
				games[game.game_id] = game
				next_game_id += 1
				game.connect(self)
			elif data["type"] == "initJoin":
				game_id = data["data"]["gameID"];

				if game_id in games:
					self.name = data["data"]["name"]
					self.color = data["data"]["color"]
					game = games[game_id]
					game.connect(self)
				else:
					response = {
						"type" : "error",
						"data" : [
							{
								"msg" : "Invalid game id"
							}
						]
					}
			elif data["type"] == "listGames":
				game_list = []

				for game_id, game in games.iteritems():
					game_list.append(game.get_basic_info())
				response = {
					"type" : "listGames",
					"data" : game_list
				}
				self.write_message(json.dumps(response))
			else:
				response = {
					"type" : "error",
					"data" : [
						{
							"msg" : "unknown command"
						}
					]
				}
				self.write_message(json.dumps(response))
		else:
			game = self.game;

			if data["type"] == "chat":
				game.chat(self, data["data"])
			elif data["type"] == "beacon":
				game.beacon(self, data["data"])
			elif data["type"] == "pieceTransform":
				game.pieceTransform(self, data["data"])
			elif data["type"] == "pieceAdd":
				game.pieceAdd(self, data["data"])
			elif data["type"] == "pieceRemove":
				game.pieceRemove(self, data["data"])
			elif data["type"] == "setBackground":
				game.setBackground(self, data["data"])
			elif data["type"] == "disconnect":
				game.disconnect(self, data["data"]["msg"])
				self.close() #maybe keep connection open instead for other stuff
			elif data["type"] == "listClients":
				abridged_clients = game.get_abridged_clients(self)
				response = {
					"type" : "listClients",
					"data" : abridged_clients
				}
				self.write_message(json.dumps(response))

			#special piece interactions

			elif data["type"] == "rollDice":
				game.rollDice(self, data["data"])
			elif data["type"] == "flipCard":
				game.flipCard(self, data["data"])
			elif data["type"] == "createDeck":
				game.createDeck(self, data["data"])
			elif data["type"] == "addCardPieceToDeck":
				print data["data"]
				game.addCardToDeck(self, data["data"])
			elif data["type"] == "addCardTypeToDeck":
				print "todo"
				#Todo: Needs to be implemented
			elif data["type"] == "drawCard":
				game.drawCard(self, data["data"])
			elif data["type"] == "createPrivateZone":
				print "todo"
				#Todo: Needs to be implemented
			elif data["type"] == "removePrivateZone":
				print "todo"
				#Todo: Needs to be implemented
			elif data["type"] == "drawScribble":
				print "todo"
				#Todo: Needs to be implemented

			#host only commands
			#do not need to determine if client is host in this function, that is handled by the Game class

			elif data["type"] == "changeHost":
				target = data["data"]["id"]
				message = data["data"]["msg"]
				game.chageHost(self, target, message)
			elif data["type"] == "announcement":
				game.announcement(self, data["data"]["msg"])
			elif data["type"] == "changeServerInfo":
				game.changeServerInfo(self, data["data"])
			elif data["type"] == "kickUser":
				target = data["data"]["id"]
				message = data["data"]["msg"]
				game.kickUser(self, target, message)
			elif data["type"] == "clearBoard":
				game.clearBoard(self);
			elif data["type"] == "closeServer":
				game.closeServer(self);
			elif data["type"] == "loadBoardState":
				game.loadBoardState(self, data["data"]);
			else:
				response = {
					"type" : "error",
					"data" : [
						{
							"msg" : "unknown command"
						}
					]
				}
				self.write_message(json.dumps(response))

	def on_close(self):
		if self.game is not None:
			self.game.disconnect(self, "socket terminated")

class IndexHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(request):
		request.render("index.html")
