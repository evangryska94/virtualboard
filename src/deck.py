import collections
import random

class Deck:
	#Uses a double ended queue for constant time flip operations
	#in theory it may be possible for combining two decks to be done in constant time
	#but that requires effort

	#class variable
	defaults = [
		"/static/img/card/clubs/ace_of_clubs.png",
		"/static/img/card/diamonds/ace_of_diamonds.png",
		"/static/img/card/hearts/ace_of_hearts.png",
		"/static/img/card/spades/ace_of_spades.png",
		"/static/img/card/clubs/2_of_clubs.png",
		"/static/img/card/diamonds/2_of_diamonds.png",
		"/static/img/card/hearts/2_of_hearts.png",
		"/static/img/card/spades/2_of_spades.png",
		"/static/img/card/clubs/3_of_clubs.png",
		"/static/img/card/diamonds/3_of_diamonds.png",
		"/static/img/card/hearts/3_of_hearts.png",
		"/static/img/card/spades/3_of_spades.png",
		"/static/img/card/clubs/4_of_clubs.png",
		"/static/img/card/diamonds/4_of_diamonds.png",
		"/static/img/card/hearts/4_of_hearts.png",
		"/static/img/card/spades/4_of_spades.png",
		"/static/img/card/clubs/5_of_clubs.png",
		"/static/img/card/diamonds/5_of_diamonds.png",
		"/static/img/card/hearts/5_of_hearts.png",
		"/static/img/card/spades/5_of_spades.png",
		"/static/img/card/clubs/6_of_clubs.png",
		"/static/img/card/diamonds/6_of_diamonds.png",
		"/static/img/card/hearts/6_of_hearts.png",
		"/static/img/card/spades/6_of_spades.png",
		"/static/img/card/clubs/7_of_clubs.png",
		"/static/img/card/diamonds/7_of_diamonds.png",
		"/static/img/card/hearts/7_of_hearts.png",
		"/static/img/card/spades/7_of_spades.png",
		"/static/img/card/clubs/8_of_clubs.png",
		"/static/img/card/diamonds/8_of_diamonds.png",
		"/static/img/card/hearts/8_of_hearts.png",
		"/static/img/card/spades/8_of_spades.png",
		"/static/img/card/clubs/9_of_clubs.png",
		"/static/img/card/diamonds/9_of_diamonds.png",
		"/static/img/card/hearts/9_of_hearts.png",
		"/static/img/card/spades/9_of_spades.png",
		"/static/img/card/clubs/10_of_clubs.png",
		"/static/img/card/diamonds/10_of_diamonds.png",
		"/static/img/card/hearts/10_of_hearts.png",
		"/static/img/card/spades/10_of_spades.png",
		"/static/img/card/clubs/jack_of_clubs.png",
		"/static/img/card/diamonds/jack_of_diamonds.png",
		"/static/img/card/hearts/jack_of_hearts.png",
		"/static/img/card/spades/jack_of_spades.png",
		"/static/img/card/clubs/queen_of_clubs.png",
		"/static/img/card/diamonds/queen_of_diamonds.png",
		"/static/img/card/hearts/queen_of_hearts.png",
		"/static/img/card/spades/queen_of_spades.png",
		"/static/img/card/clubs/king_of_clubs.png",
		"/static/img/card/diamonds/king_of_diamonds.png",
		"/static/img/card/hearts/king_of_hearts.png",
		"/static/img/card/spades/king_of_spades.png"
	]

	def __init__(self, cardData, default_back_icon):
		self.flipped = False
		self.cards = collections.deque()

		if "count" in cardData:
			count = cardData["count"]
		else:
			count = 1
		any_faceup = False

		for i in range(0, count):
			if i < len(cardData["cards"]):
				card_entry = cardData["cards"][i]
				card = {
					"icon" : card_entry["icon"],
					"face_down" : card_entry["faceDown"] == 1
				}

				if "back" in card_entry:
					card["back"] = card_entry["back"]
				else:
					card["back"] = default_back_icon

				if card["face_down"] == 0:
					any_faceup = True
				self.cards.append(card)
			else:
				card = {
					"face_down" : 0 if any_faceup else 1,
					"icon" : Deck.defaults[i % len(Deck.defaults)],
					"back" : default_back_icon
				}
				self.cards.append(card)

		if "shuffle" in cardData and cardData["shuffle"] == 1:
			self.shuffle()

	# Returns the icon to display for the deck
	def get_icon(self):
		if self.flipped:
			piece = self.cards[0]
		else:
			piece = self.cards[-1]

		if piece["face_down"] != self.flipped:
			return piece["back"]
		return piece["icon"]

	# Returns the number of cards in the deck
	def get_size(self):
		return len(self.cards)

	# Flips the deck
	def flip(self):
		self.flipped = not self.flipped

	# If there are more than one cards in the deck returns the top card and removes it from the deck.
	# Otherwise, returns None
	def draw(self):
		if len(self.cards) > 1:
			if self.flipped:
				card = self.cards.popleft()
				card["face_down"] = not card["face_down"]
				return card
			return self.cards.pop()
		return None

	# Adds a card to the deck
	#front - string
	#back - string
	#face_down - boolean
	def add(self, front, back, face_down):
		card = {
			"icon" : front,
			"back" : back
		}

		if self.flipped:
			card["face_down"] = not face_down
			self.cards.appendleft(card)
		else:
			card["face_down"] = face_down
			self.cards.append(card)

	# Shuffles the deck
	def shuffle(self):
		random.shuffle(self.cards)

	# Adds all cards in another deck to this deck
	def absorb(self, other):
		if other.flipped:
			for entry in reversed(other.cards):
				self.add(entry["icon"], entry["back"], not entry["face_down"])
		else:
			for entry in other.cards:
				self.add(entry["icon"], entry["back"], entry["face_down"])

	# Returns a JSON object for the deck. Complete should be true for saving the game, false otherwise
	def get_json_obj(self, complete=False):
		data = {
			"count" : len(self.cards)
		}

		if complete:
			card_data = []

			if self.flipped:
				for card_entry in reversed(self.cards):
					card_data.append({
						"faceDown" : 0 if card_entry["face_down"] else 1,

						"icon" : card_entry["icon"],
						"back" : card_entry["back"]
					})
			else:
				for card_entry in self.cards:
					card_data.append({
						"faceDown" : 1 if card_entry["face_down"] else 0,

						"icon" : card_entry["icon"],
						"back" : card_entry["back"]
					})
			data["cards"] = card_data
		return data

