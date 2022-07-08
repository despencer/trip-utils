import json

class Profile:
    def __init__(self):
        self.conditions = Conditions()

class Conditions:
    def __init__(self):
        self.tags = {}

class Tag:
    def __init__(self):
        self.values = {}

class ProfileJson:
    @classmethod
    def load(cls, jprofile):
        profile = Profile()
        profile.conditions = cls.loadconditions(jprofile['conditions'])
        return profile

    @classmethod
    def loadconditions(cls, jcond):
        conditions = Conditions()
        for t,v in jcond.items():
            conditions.tags[t] = cls.loadtag(v)
        return conditions

    @classmethod
    def loadtag(cls, jtag):
        tag = Tag()
        for k,v in jtag.items():
            tag.values[k] = v
        return tag

def load(fname):
    with open(fname) as jfile:
        return ProfileJson.load(json.load(jfile))
