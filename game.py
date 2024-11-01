import os
import random


class Game:
    def __init__(self, Gid=0):
        self.deck = {}
        self.id = Gid
        self.cards = ['Blue_0', 'Blue_1', 'Blue_2', 'Blue_3', 'Blue_4', 'Blue_5', 'Blue_6', 'Blue_7', 'Blue_8', 'Blue_9',
         'Blue_Draw_Two', 'Blue_Reverse', 'Blue_Skip', 'Blue_0', 'Blue_1', 'Blue_2', 'Blue_3', 'Blue_4', 'Blue_5', 'Blue_6', 'Blue_7', 'Blue_8', 'Blue_9',
         'Blue_Draw_Two', 'Blue_Reverse', 'Blue_Skip',
         #------------------Green-----------------------------------------------------
         'Green_0', 'Green_1', 'Green_2', 'Green_3', 'Green_4', 'Green_5', 'Green_6', 'Green_7', 'Green_8', 'Green_9',
         'Green_Draw_Two', 'Green_Reverse', 'Green_Skip', 'Green_0', 'Green_1', 'Green_2', 'Green_3', 'Green_4', 'Green_5', 'Green_6', 'Green_7', 'Green_8', 'Green_9',
         'Green_Draw_Two', 'Green_Reverse', 'Green_Skip',
         #------------------Red-------------------------------------------------------
         'Red_0', 'Red_1', 'Red_2', 'Red_3', 'Red_4', 'Red_5', 'Red_6', 'Red_7', 'Red_8', 'Red_9',
         'Red_Draw_Two', 'Red_Reverse', 'Red_Skip', 'Red_0', 'Red_1', 'Red_2', 'Red_3', 'Red_4', 'Red_5', 'Red_6', 'Red_7', 'Red_8', 'Red_9',
         'Red_Draw_Two', 'Red_Reverse', 'Red_Skip',
         #----------------Yellow------------------------------------------------------
         'Yellow_0', 'Yellow_1', 'Yellow_2', 'Yellow_3', 'Yellow_4', 'Yellow_5', 'Yellow_6', 'Yellow_7', 'Yellow_8', 'Yellow_9',
         'Yellow_Draw_Two', 'Yellow_Reverse', 'Yellow_Skip', 'Yellow_0', 'Yellow_1', 'Yellow_2', 'Yellow_3', 'Yellow_4', 'Yellow_5', 'Yellow_6', 'Yellow_7', 'Yellow_8', 'Yellow_9',
         'Yellow_Draw_Two', 'Yellow_Reverse', 'Yellow_Skip',
         #-----------------Wilds-----------------------------------------------------
         'Wild_1', 'Wild_2', 'Wild_3', 'Wild_4',
         # ------------------Wild+4-----------------------------------------------------
         'Wild_Draw_Four_1', 'Wild_Draw_Four_2', 'Wild_Draw_Four_3', 'Wild_Draw_Four_4', ]
        self.turn = 0
        self.ready = False # for sockets
        self.sequence = 1
        self.wild_moved = True
        self.points = {}
        self.total_player = 0
        self.illegal_move = False
        self.unos = []
        self.top_card = {'name': "None", 'color': "None", "type": "None"}

    def iscon(self): # for sockets
        return self.ready
    def calculate_points(self, cards):
        points = 0
        for card in cards:
            # Check for special cards that may include a color prefix
            if any(special in card for special in ['Reverse', 'Skip', 'Draw_Two']):
                points += 20
            elif 'Wild' in card:
                points += 50
            else:
                # Assuming cards are in the format 'Color_Number'

                points += int(card.split('_')[1])  # Gets the numeric value after the underscore

        return points
    def shuffle(self, no_players: int):
        self.total_player = no_players
        random.shuffle(self.cards)
        for player in range(no_players):
            cards = random.sample(self.cards, 7)
            self.deck.update({f"{player}": cards})
            self.remove_from_cards(cards)
            points = self.calculate_points(cards)
            self.points.update({player: points})

        random.shuffle(self.cards)

        while True:
            top_card = str(random.choice(self.cards))
            if 'wild' not in top_card.lower() and 'skip' not in top_card.lower() and 'reverse' not in top_card.lower() and 'draw_two' not in top_card.lower():
                break
        color, ctype = top_card.split('_',1)
        self.top_card = {'name': f"{top_card}", 'color': f"{color}", 'type': f"{ctype}"}
        print(f"Deck after Shuffle: {self.deck}")
    def get_deck(self, player=False):
        """
        :return: Deck Of Current Player
        """
        return self.deck[str(self.turn) if not player else str(player)]
    def can_play(self):
        currentcol_dig = []
        for card in self.get_deck():
            col = card.split('_', 1)[0]
            num = card.split('_', 1)[1]
            currentcol_dig.append(col)
            currentcol_dig.append(num)
        if (self.top_card.get('color') in currentcol_dig or self.top_card['type'] in currentcol_dig) or 'Wild' in currentcol_dig:
            return True
        else:
            return False
    def remove_from_cards(self, cards):
        for card in cards:
            if card in self.cards:
                self.cards.remove(card)
    def reset(self):
        self.__init__()
    def draw_card(self):
        newCards = random.choice(self.cards)
        self.deck[f'{str(self.turn)}'] += [newCards]
        self.remove_from_cards([newCards])
        if (newCards.split('_', 1)[0] == self.top_card['color'] or newCards.split('_', 1)[1] == self.top_card[
            'type'] or 'wild' in newCards.lower()):
            return (True, newCards) # Means the card is playable
        else:
            return (False, newCards) # Means the cards is not playable
    def play(self, action: str, wild_color=None):
        """

        :param action: (Required). It is the name of the card or if the second-last card is a Wild card so, it is either 'Draw' or 'Challenge'
        :param wild_color: (Only Wild). The color chosed on the wild card
        :return: weather or not the card is playable
        """
        if action not in self.get_deck() and action not in ['draw_card', 'challenge', 'draw', 'yell_uno']:
            print(action)
            print(self.get_deck())
            raise TypeError("This Card is not in your deck")
        else:
            if action not in ['draw_card', 'challenge', 'draw', 'yell_uno']:
                color, ctype = action.split('_', 1)
        if action.lower() == 'yell_uno':
            if len(self.get_deck()) > 2 and len(self.get_deck(int(self.turn-1))) < 2 and str(self.turn-1) not in self.unos:
                cards = random.sample(self.cards, 2)
                self.deck[str(self.turn-1)].extend(cards)
                self.remove_from_cards(cards)
            elif len(self.get_deck()) > 2:
                raise ValueError(f"You, Cant Shout UNO!. You still have {len(self.get_deck())} cards.")
            else:
                self.unos.append(str(self.turn))



        if action.lower() == 'draw_card':
            action = 'draw_card'
        elif 'wild_draw_four' in self.top_card['name'].lower() and not self.wild_moved:
            if action.lower() == 'draw':
                print('You Choose DRAW against Wild+4')
                newCards = random.sample(self.cards, 4)
                self.deck[f'{str(self.turn)}'] += newCards
                self.remove_from_cards(newCards)
                action = self.top_card.get('name')
                color = self.top_card.get('color')
                ctype = self.top_card.get('type')
                self.illegal_move = False
                self.wild_moved = True
            elif action.lower() == 'challenge':
                if self.illegal_move:
                    print('You Choosed Challenge against Wild+4 and WON')
                    newCards = random.sample(self.cards, 4)
                    self.deck[f'{self.turn-1 if self.turn-1!=-1 else self.total_player-1}'] += newCards
                    self.remove_from_cards(newCards)
                    action = self.top_card.get('name')
                    color = self.top_card.get('color')
                    ctype = self.top_card.get('type')
                else:
                    print('You Choosed Challenge against Wild+4 and FAILED')
                    newCards = random.sample(self.cards, 6)
                    self.deck[f'{self.turn}'] += newCards
                    self.remove_from_cards(newCards)
                    action = self.top_card.get('name')
                    color = self.top_card.get('color')
                    ctype = self.top_card.get('type')
                self.illegal_move = False
                self.wild_moved = True
            else:
                raise TypeError('The Second last card is Wild_Draw_Four. You can only select action "Draw" or "Challenge"')
        elif 'wild' in action.lower():
            self.deck[f'{str(self.turn)}'].remove(action)
            ctype = None
            print('You Moved Wild',end='')
            if 'draw_four' in action.lower():
                print(' Draw 4')
                currentColors = []
                for cd in self.get_deck():
                    col = cd.split('_',1)[0]
                    currentColors.append(col)
                if self.top_card['color'] in currentColors:
                    self.illegal_move = True
                self.wild_moved = False
            print('')
            color = wild_color.capitalize()
        elif (self.top_card.get('color').lower() == color.lower() or self.top_card.get('type').lower() == ctype.lower()) and action not in ['draw_card', 'challenge', 'draw', 'yell_uno']:
            print("Act: "+action)
            print(self.get_deck())
            self.deck[f'{str(self.turn)}'].remove(action)
            if ctype.lower() == 'reverse':
                self.sequence = self.sequence*-1
        else:
            raise TypeError("The Card is not Playable")
        if action == "draw_card":
            ctype = None
            color = None
        self.points[self.turn] = self.calculate_points(self.deck[str(self.turn)])
        self.top_card = {'name': f"{action if action!='draw_card' else self.top_card['name']}", 'color': f"{color if action!='draw_card' else self.top_card['color']}", 'type': f"{ctype if action!='draw_card' else self.top_card['type']}"}
        if (str(ctype).lower() == 'skip'or str(ctype).lower() == 'draw_two') and action != 'draw_card':
            self.turn = (self.turn + 2 * self.sequence) % self.total_player

            # Adjust turn to ensure it stays within the bounds of player indices
            if self.turn < 0:
                self.turn += self.total_player
        else:
            # If the current turn is at the last player and moving forward (sequence = 1) or at the first player and moving backward (sequence = -1)
            if self.turn >= self.total_player - 1 and self.sequence == 1:
                print('Circle Complete')
                self.turn = 0  # Wrap around to the first player
            elif self.turn <= 0 and self.sequence == -1:
                print('Circle Complete')
                self.turn = self.total_player - 1  # Wrap around to the last player
            else:
                # Normal turn increment/decrement based on the sequence value
                self.turn += self.sequence

        if 'draw_two' in action.lower():
            newCards = random.sample(self.cards, 2)
            self.deck[str(self.turn)].extend(newCards)
            self.remove_from_cards(newCards)
    def checkWin(self):
        for i in range(self.total_player):
            if len(self.deck[str(i)]) < 1:
                return i
        return False
    def get_moves(self):
        """
        :return: [:x: is a playable card in deck] if dict is empty, returns False
        """
        playables = []
        if 'Wild_Draw' in self.top_card['name']:
            return ['challenge', 'draw']
        else:
            for card in self.get_deck():
                col = card.split('_', 1)[0]
                ctype = card.split('_', 1)[1]
                if 'wild' in card:
                    playables.append(card)
                elif self.top_card['color'] == col:
                    playables.append(card)
                elif self.top_card['type'] == ctype:
                    playables.append(card)

        return (playables if len(playables) > 0 else ['draw_card'])
    def moveWithBot(self):
        actions = game.get_moves()
        if 'Draw_Four' in game.top_card['name']:
            action = random.choice(actions)
            game.play(action)
            return action, None
        elif actions != 'draw_card':
            color = None
            action = random.choice(actions)
            if 'Wild' in action:
                color = random.choice(['Red', 'Green', 'Blue', 'Yellow'])
            game.play(action, wild_color=color)  # Automatically play 'draw_card'
            return action, color
        else:
            _, card = game.draw_card()
            game.play('draw_card')
            return card

if __name__ == "__main__":
    game = Game()
    game.shuffle(2)

    while True:
        print(game.top_card)
        print(game.points)
        if game.checkWin():
            break
        c = game.can_play()
        print(f"...You {'Can Play' if c else 'Cant Play'}")
        print(f'Its player {game.turn}, You have: \n{game.get_deck()}')
        card = input('Move: ')
        color = None
        if 'wild' in card.lower():
            color = input('Enter color: ')

        game.play(card, color)
        print(game.get_deck())






    print(str(game.checkWin())+ 'HAS WON')