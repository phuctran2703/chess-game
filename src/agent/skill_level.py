"""
Skill Level Module for Chess Agents

This module defines the skill level classes and enums for chess agents.
"""

from enum import Enum


class SkillCategory(Enum):
    """Enum representing skill categories"""

    POOR = "Poor"
    AVERAGE = "Average"
    GOOD = "Good"


class SkillLevel:
    """
    Represents a skill level with both a category (Poor/Average/Good)
    and a numeric level (1-10)
    """

    def __init__(self, level=1):
        """
        Initialize a skill level

        Parameters:
        - level: Numeric level from 1-10
        """
        self.set_level(level)

    def set_level(self, level):
        """
        Set the numeric level and update the category

        Parameters:
        - level: Numeric level from 1-10
        """
        if not isinstance(level, int) or level < 1 or level > 10:
            raise ValueError("Skill level must be an integer between 1 and 10")

        self.level = level

        if level <= 3:
            self.category = SkillCategory.POOR
        elif level <= 7:
            self.category = SkillCategory.AVERAGE
        else:
            self.category = SkillCategory.GOOD

    def __str__(self):
        """String representation of skill level"""
        return f"{self.category.value} (Level {self.level})"


def get_skill_level_description(skill_level):
    """
    Get a detailed description of a skill level

    Parameters:
    - skill_level: SkillLevel object

    Returns:
    - String description of the skill level
    """
    if skill_level.category == SkillCategory.POOR:
        if skill_level.level == 1:
            return "Beginner level. Makes random legal moves without evaluation."
        elif skill_level.level == 2:
            return "Novice level. Basic understanding of piece values."
        else:  # level 3
            return "Elementary level. Considers immediate captures and threats."

    elif skill_level.category == SkillCategory.AVERAGE:
        if skill_level.level == 4:
            return "Casual player level. Understands basic tactics."
        elif skill_level.level == 5:
            return "Club player level. Considers short-term plans."
        elif skill_level.level == 6:
            return "Intermediate level. Decent positional understanding."
        else:  # level 7
            return "Advanced club player level. Good tactical awareness."

    else:  # GOOD
        if skill_level.level == 8:
            return "Expert level. Strong tactical and positional play."
        elif skill_level.level == 9:
            return "Master level. Excellent calculation and planning."
        else:  # level 10
            return "Grandmaster level. Superior strategic and tactical understanding."
