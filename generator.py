import json
import random
import re
import math

class_file = "core_classes.json"
skills_file = "core_skills.json"


class Character():

	def __init__(self, level=random.randint(1,20)):

		with open(class_file) as json_file:
			class_data = json.load(json_file)
		# class_choices = list(class_data.keys())
		# chosen_class = random.choice(class_choices)
		chosen_class = "paladin"
		self.class_data = class_data[chosen_class]
		self.class_levels = {chosen_class : level}
		self.ability_scores = [0, 0, 0, 0, 0, 0]
		self.abi_mods = [0, 0, 0, 0, 0, 0]
		self.special = []
		self.roll_for_stats()
		self.calc_hit_points()
		self.calc_bab()
		self.calc_saves()
		self.calc_skills()
		self.get_special()
		self.get_spells_per_day()

	def print(self):
		print ("class levels: " + str(self.class_levels))
		print ("abi scores: " + str(self.ability_scores))
		print ("abi mods:   " + str(self.abi_mods))
		print ("net mod:    " + str(self.calc_net_mod(self.ability_scores)))
		print ("hit points: " + str(self.hit_points))
		print ("fort save:  " + str(self.fort_save))
		print ("ref save:  " + str(self.ref_save))
		print ("will save:  " + str(self.will_save))
		print ("Skills with ranks:  ")
		for each_skill in self.skills:
			if self.skills[each_skill]["ranks"] > 0:
				print (" " + each_skill + " : total bonus: " + str(self.skills[each_skill]["total"]))
		print ("Special Abilities: ")
		for each_ability in self.special:
			print (" " + each_ability)
		if self.spells_per_day:
			print (self.spells_per_day)

	def roll_for_stats(self):
		net_mod = 0
		while (net_mod < 1):
			rolls = self.roll_ability_scores()
			net_mod = self.calc_net_mod(rolls)
		self.assign_rolls(rolls)

	def roll_ability_scores(self):
		rolls = [0, 0, 0, 0]
		final_rolls = [0, 0, 0, 0, 0, 0]
		for i in range(6):
			while final_rolls[i] < 6:
				for j in range(4):
					rolls[j] = random.randint(1, 6)
				final_rolls[i] = sum(rolls) - min(rolls)
		return final_rolls

	def calc_net_mod(self, rolls):
		net_mod = 0
		for i in range(6):
			net_mod += self.calc_abi_mod(rolls[i])
		return net_mod

	def assign_rolls(self, final_rolls):
		final_rolls.sort()
		for i in self.class_data["priority_ability_scores"]:
			self.ability_scores[i] = final_rolls.pop()
		for i in range(6):
			if self.ability_scores[i] == 0: # if not yet assigned it's not a priority score
				self.ability_scores[i] = final_rolls.pop(random.randint(0, len(final_rolls)-1))
		self.calc_abi_mods()

	def calc_abi_mod(self, score):
		if score % 2 != 0: 
			score -= 1
		return int( (score - 10) / 2 )

	def calc_abi_mods(self):
		for i in range(6):
			self.abi_mods[i] = self.calc_abi_mod(self.ability_scores[i])

	def calc_bab(self):
		self.bab = 0
		for i in self.class_levels:
			self.bab += int(self.class_levels[i] * self.class_data["bab"])

	def calc_hit_points(self):
		self.hit_points = self.class_data["hit_die"] + self.abi_mods[2]
		for i in self.class_levels:
			for _ in range(self.class_levels[i] - 1):
				self.hit_points += (random.randint(1, self.class_data["hit_die"]) + self.abi_mods[2])

	def calc_saves(self):
		self.fort_save = {"base" : 0, "misc" : 0, "plus_two" : False, "total" : 0}
		self.ref_save = {"base" : 0, "misc" : 0, "plus_two" : False, "total" : 0}
		self.will_save = {"base" : 0, "misc" : 0, "plus_two" : False, "total" : 0}
		for i in self.class_levels:
			if self.class_data["fort"]:
				self.fort_save["plus_two"] = True
				self.fort_save["base"] = int( self.class_levels[i] / 2 )
			else:
				self.fort_save["base"] = int( self.class_levels[i] / 3 )

			if self.class_data["ref"]:
				self.ref_save["plus_two"] = True
				self.ref_save["base"] = int( self.class_levels[i] / 2 )
			else:
				self.ref_save["base"] = int( self.class_levels[i] / 3 )
			if self.class_data["will"]:
				self.will_save["plus_two"] = True
				self.will_save["base"] = int( self.class_levels[i] / 2 )
			else:
				self.will_save["base"] = int( self.class_levels[i] / 3 )
		
		self.fort_save["total"] = self.fort_save["base"] + self.abi_mods[2]
		if self.fort_save["plus_two"]:
			self.fort_save["total"] += 2
		self.ref_save["total"] = self.ref_save["base"] + self.abi_mods[1]
		if self.ref_save["plus_two"]:
			self.ref_save["total"] += 2
		self.will_save["total"] = self.will_save["base"] + self.abi_mods[4]
		if self.will_save["plus_two"]:
			self.will_save["total"] += 2

	def calc_skills(self):
		with open(skills_file) as json_file:
			skill_data = json.load(json_file)
		self.skills = {}
		for each_skill in skill_data:
			self.skills[each_skill] = {"key_abi" : skill_data[each_skill]["key_abi"],
										"ranks" : 0,
										"misc" : 0,
										"armor_check" : skill_data[each_skill]["armor_check"],
										"total" : 0}
		num_of_pri_skills = self.class_data["sppl"] + self.abi_mods[3] # class's sppl + int mod
		priority_skills = set()
		for i in range(num_of_pri_skills):
			while len(priority_skills) < (i+1):
				skill_to_add = random.choice(self.class_data["class_skills"])
				priority_skills.add(skill_to_add)
		for each_skill in priority_skills:
			self.skills[each_skill]["ranks"] = ( list(self.class_levels.values())[0] + 3 )
		for each_skill in self.skills:
			self.skills[each_skill]["total"] = ( self.skills[each_skill]["ranks"] + self.abi_mods[self.skills[each_skill]["key_abi"]] )

	def get_special(self):
		number_abi_pattern = re.compile(r'[A-Za-z /()\+-]*[0-9]+[A-Za-z /()\+-]*')
		number_or_dice = re.compile(r'[-\+]?[0-9]+[d0-9+]?')
		for i in range(list(self.class_levels.values())[0]):
			for each_feature in self.class_data["special"][i]:
				if number_abi_pattern.match(each_feature):
					for old_ability in self.special:
						if number_abi_pattern.match(old_ability):
							if number_or_dice.split(each_feature, 1)[0] == number_or_dice.split(old_ability, 1)[0]:
								self.special.remove(old_ability)
								break
				self.special.append(each_feature)

	def get_spells_per_day(self):
		self.spells_per_day = self.class_data["spells_per_day"][list(self.class_levels.values())[0] - 1]
		self.calc_bonus_spells()
	
	def calc_bonus_spells(self):
		spd_enum = enumerate(self.spells_per_day, (1, 0)[self.class_data["cantrips"]])
		for slvl, spd in spd_enum:
			if slvl != 0:
				self.spells_per_day[(slvl - 1, slvl)[self.class_data["cantrips"]]] += math.ceil((self.abi_mods[self.class_data["bonus_spell_abi"]] - slvl + 1) / 4)

character = Character()
character.print()