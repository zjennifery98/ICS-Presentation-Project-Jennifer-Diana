# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import guessing_hard as hard

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.score = 0
        self.digits = 0
        self.puzzle_key = 0

    def set_state(self, state):
        self.state = state
        
    def get_state(self):
        return self.state
    
    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me
        
    def connect_to(self, peer):
        msg = M_CONNECT + peer
        mysend(self.s, msg)
        response = myrecv(self.s)
        if response == (M_CONNECT + 'ok'):
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response == (M_CONNECT + 'busy'):
            self.out_msg += 'User is busy. Please try again later\n'
        elif response == (M_CONNECT + 'hey you'):
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = M_DISCONNECT
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_code, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:
                
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE
                    
                elif my_msg == 'time':
                    mysend(self.s, M_TIME)
                    time_in = myrecv(self.s)
                    self.out_msg += "Time is: " + time_in
                            
                elif my_msg == 'who':
                    mysend(self.s, M_LIST)
                    logged_in = myrecv(self.s)
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in
                            
                elif my_msg[0] == 'c':
                	peer = my_msg[1:]
                	peer = peer.strip()
                	if self.connect_to(peer) == True:
                		self.state = S_CHATTING
                		self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                		self.out_msg += '-----------------------------------\n'
                	else:
                		self.out_msg += 'Connection unsuccessful\n'
                
                elif my_msg[0] == 'g':
                	#self.out_msg += my_msg[1:].strip()
                	game_type = my_msg[1:].strip()
                	mysend(self.s, M_SET + game_type)
                	self.puzzle_key = myrecv(self.s)
                	if game_type == '1':
                		self.state = S_GUESSING_1
                		self.score = 100
                		self.out_msg += 'Now there is a random number between 1 and 99! \n'
                		self.out_msg += 'Take a guess! \n'
                	elif game_type == '2':
                		self.state = S_GUESSING_2
                		self.score = 105
                		self.out_msg += "Welcome to the hard number guessing game. \n"
                		self.out_msg += "The number has " + str(len(self.puzzle_key)) + " digits. \n"
                		self.out_msg += "No two digits are the same. \n"
                		self.out_msg += "A implies the number of correct digits in the correct place; \n"
                		self.out_msg += "B implies the number of correct digits in the wrong place. \n"
                		self.out_msg += "Good luck!"
                
                elif my_msg == "r":
                    self.out_msg += 'Ranking List \n'
                    mysend(self.s, M_RANK + str(self.score))
                    rank = myrecv(self.s)
                    self.out_msg += rank
                    self.state = S_LOGGEDIN
                else:
                    self.out_msg += menu
                    
            if len(peer_msg) > 0:
                if peer_code == M_CONNECT:
                    self.peer = peer_msg
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer 
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                    
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, M_EXCHANGE + "[" + self.me + "] " + my_msg)
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                if peer_code == M_CONNECT:
                    self.out_msg += "(" + peer_msg + " joined)\n"
                else:
                    self.out_msg += peer_msg

            # I got bumped out
            if peer_code == M_DISCONNECT:
                self.state = S_LOGGEDIN

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
        
        elif self.state == S_GUESSING_1:
        	if len(my_msg) > 0:
        		mysend(self.s, M_GUESS + my_msg.strip())
        		response = myrecv(self.s)
        		if self.score > 0:
        			if response == '0':
        				self.out_msg += "Too big"
        				self.score = self.score - 5
        			elif response == '1':
        				self.out_msg += "Too small"  
        				self.score = self.score - 5
        			elif response == '2':
        				self.out_msg += "Correct answer! Congratulations! Your score is " + str(self.score) + "\n Press r to check the ranking list."
        				self.state = S_LOGGEDIN
        				#state1 = True
        		else:
        			self.out_msg += "Time's out! You lost!"
        			self.state = S_LOGGEDIN
        
        elif self.state == S_GUESSING_2:
        	if len(my_msg) > 0:
        		puzzle = hard.Puzzle(int(self.puzzle_key))
        		self.out_msg += '\n Please take a guess: \n'
        		guess = my_msg
        		puzzle.check_answer(guess)
        		self.score -= (5 - len(self.puzzle_key))
        		if puzzle.state == True:
        			self.out_msg += "Correct answer! Congratulations! Your score is " + str(self.score) + "\n Press r to check the ranking list."
        			self.state = S_LOGGEDIN
        		if self.score <= 0:
        			self.out_msg += "Time's out! You lost! "
        			self.state = S_LOGGEDIN
			
#==============================================================================
# invalid state                       
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)
            
        return self.out_msg
