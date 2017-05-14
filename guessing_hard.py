#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 13:26:42 2017

@author: JenniferZhang
"""

import random

class Puzzle():
    def __init__(self, key):
        self.state = False
        self.key = str(key)
        self.digits = len(self.key)
        self.every_digit = []
        for d in self.key:
            self.every_digit.append(d)
    
    def check_answer(self, guess):
        self.guess = guess.strip()
        self.guess_digits = len(guess)
        A = 0
        B = 0
        if self.guess_digits != self.digits:
            print("Wrong answer length")
        else:
            self.guess_every_digit = []
            for d in self.guess:
                self.guess_every_digit.append(d)
            for i in range(self.digits):
                if self.guess_every_digit[i] == self.every_digit[i]:
                    A += 1
                elif self.guess_every_digit[i] in self.every_digit:
                    B += 1
            print("A", A, "B", B)
            if A == self.digits and B == 0:
                print("Correct Answer!")
                self.state = True


if __name__ == "__main__":
    number_digits = random.randint(1,5)
    digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    puzzle_key = ''
    for i in range(number_digits):
            digit = digits[random.randint(0, len(digits))]
            digits.remove(digit)
            puzzle_key += str(digit)
    puzzle = Puzzle(int(puzzle_key))
    print("Welcome to the hard number guessing game.")
    print("The number has", puzzle.digits, "digits.")
    print("No two digits are the same.")
    while puzzle.state == False:
        guess = input("Please take a guess: \n")
        puzzle.check_answer(guess)