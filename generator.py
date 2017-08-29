import json
import random
import re
import math

class_file = "core_classes.json"
races_file = "core_races.json"
skills_file = "all_skills.json"


class Character():

	def __init__(self, level=random.randint(1,20)):

		with open(class_file) as json_file:
			class_data = json.load(json_file)
		chosen_class = random.choice(list(class_data.keys()))
		# chosen_class = "wizard"
		self.class_data = class_data[chosen_class]
		self.class_levels = {chosen_class : level}
		self.ability_scores = [0, 0, 0, 0, 0, 0]
		self.abi_mods = [0, 0, 0, 0, 0, 0]
		self.special = []
		self.languages = set()
		print ("Making a level " + str(level) + " " + str(chosen_class))
		self.roll_for_stats()
		self.initialize_skills()
		self.get_racial_traits()
		self.calc_hit_points()
		self.calc_bab()
		self.calc_saves()
		self.calc_skills()
		self.get_class_special()
		self.get_spells()

	def print(self):
		print ("race: " + str(self.race))
		print ("class levels: " + str(self.class_levels))
		print ("abi scores: " + str(self.ability_scores))
		print ("abi mods:   " + str(self.abi_mods))
		print ("net mod:    " + str(self.calc_net_mod(self.ability_scores)))
		print ("hit points: " + str(self.hit_points))
		print ("fort save:  " + str(self.fort_save))
		print ("ref save:  " + str(self.ref_save))
		print ("will save:  " + str(self.will_save))
		print ("Skills worth printing:  ")
		for each_skill in self.skills:
			if self.skills[each_skill]["ranks"] > 0 or self.skills[each_skill]["misc"] > 0:
				# print (" " + each_skill + " : total : " + str(self.skills[each_skill]["total"]))
				print (" {} : Total:{} (R:{}, M:{})".format(each_skill, self.skills[each_skill]["total"], self.skills[each_skill]["ranks"], self.skills[each_skill]["misc"]))
		print ("Special Abilities: ")
		for each_ability in self.special:
			print (" " + each_ability)
		if self.class_data.get("spells_per_day"):
			print (self.spells_per_day)
			if self.class_data.get("spells_known"):
				print (self.spells_known)
			else:
				print (self.spells_prepared)
		print ("Languages Fluent: ")
		for each_lanaguage in self.languages:
			print (" " + str(each_lanaguage))

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

	def initialize_skills(self):
		with open(skills_file) as json_file:
			skill_data = json.load(json_file)
		self.skills = {}
		for each_skill in skill_data:
			self.skills[each_skill] = {"key_abi" : skill_data[each_skill]["key_abi"],
										"ranks" : 0,
										"misc" : 0,
										"armor_check" : skill_data[each_skill]["armor_check"],
										"total" : 0}

	def initialize_skill(self, new_skill):
		self.skills[new_skill] = {"ranks" : 0, "misc" : 0, "armor_check" : 0, "total" : 0}
		if "Craft" in new_skill or "Knowledge" in new_skill:
			self.skills[new_skill]["key_abi"] = 3
		elif "Perform" in new_skill:
			self.skills[new_skill]["key_abi"] = 5
		elif "Profession" in new_skill:
			self.skills[new_skill]["key_abi"] = 4
		else:
			self.skills[new_skill]["key_abi"] = 2 # *shrug*


	def calc_skills(self):
		priority_skills = set()
		if self.class_data.get("priority_skills"):
			for each_skill in self.class_data["priority_skills"]:
				priority_skills.add(each_skill)
		min_num_pri_skills = math.floor((self.class_data["sppl"] + self.abi_mods[3]) / 2)
		while len(priority_skills) < min_num_pri_skills:
			priority_skills.add(random.choice(self.class_data["class_skills"]))

		max_rank = ( list(self.class_levels.values())[0] + 3 )
		num_skill_points = max_rank * (self.class_data["sppl"] + self.abi_mods[3])

		for each_skill in priority_skills:
			if num_skill_points >= max_rank:
				self.skills[each_skill]["ranks"] = max_rank
				num_skill_points -= max_rank
			else:
				self.skills[each_skill]["ranks"] = num_skill_points
				num_skill_points = 0
				break
		while num_skill_points > 0:
			poss_skill = random.choice(self.class_data["class_skills"])
			if self.skills[poss_skill]["ranks"] < max_rank:
				self.skills[poss_skill]["ranks"] += 1
				num_skill_points -= 1

		for each_skill in self.skills:
			self.skills[each_skill]["total"] = ( self.skills[each_skill]["ranks"] + self.abi_mods[self.skills[each_skill]["key_abi"]] + self.skills[each_skill]["misc"] )

	def get_racial_traits(self):
		with open(races_file) as json_file:
			race_data = json.load(json_file)
		# self.race = random.choice(list(race_data.keys()))
		self.race = "gnome"
		self.race_data = race_data[self.race]

		if self.race_data.get("abi_adjust"):
			for i in range(6):
				self.ability_scores[i] += self.race_data["abi_adjust"][i]
			self.calc_abi_mods()

		if self.race_data.get("skill_adjust"):
			for each_skill in list(self.race_data["skill_adjust"].keys()):
				if each_skill not in self.skills:
					self.initialize_skill(each_skill)
				self.skills[each_skill]["misc"] += self.race_data["skill_adjust"][each_skill]

		for each in self.race_data["special"]:
			self.special.append(each)

		for each in self.race_data["auto_lang"]:
			self.languages.add(each)
		if self.abi_mods[3] > 0:
			while len(self.languages) < (len(self.race_data["auto_lang"]) + self.abi_mods[3]):
				self.languages.add(random.choice(self.race_data["bonus_lang"]))

		self.size = self.race_data["size"]
		self.land_speed = self.race_data["land_speed"]


	def get_class_special(self):
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

	def get_spells(self):
		if self.class_data.get("spells_per_day"):
			self.get_spells_per_day()
			self.learn_prepare_spells()

	def get_spells_per_day(self):
		self.spells_per_day = self.class_data["spells_per_day"][list(self.class_levels.values())[0] - 1]
		self.calc_bonus_spells()
	
	def calc_bonus_spells(self):
		spd_enum = enumerate(self.spells_per_day, (1, 0)[self.class_data["cantrips"]])
		for slvl, spd in spd_enum:
			if slvl != 0:
				self.spells_per_day[(slvl - 1, slvl)[self.class_data["cantrips"]]] += math.ceil((self.abi_mods[self.class_data["bonus_spell_abi"]] - slvl + 1) / 4)

	def learn_prepare_spells(self):
		if self.class_data.get("spells_known"): # Spontaneous caster
			self.spells_known = []
			num_of_spells_known = self.class_data["spells_known"][list(self.class_levels.values())[0] - 1]
			for slvl in range(len(num_of_spells_known)):
				self.spells_known.append(set())
				while len(self.spells_known[slvl]) < num_of_spells_known[slvl]:
					spell_to_add = random.choice(self.class_data["spell_list"][slvl])
					self.spells_known[slvl].add(spell_to_add)
		else: # Prepared caster
			self.spells_prepared = []
			for slvl in range(len(self.spells_per_day)):
				self.spells_prepared.append([])
				for _ in range(self.spells_per_day[slvl]):
					spell_to_add = random.choice(self.class_data["spell_list"][slvl]) 
					self.spells_prepared[slvl].append(spell_to_add)

character = Character()
character.print()