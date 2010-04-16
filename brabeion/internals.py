from django.contrib.auth.models import User

from brabeion.base import Badge



class BadgeCache(object):
    """
    This is responsible for storing all badges that have been registered, as
    well as providing the pulic API for awarding badges.
    
    This class should not be instantiated multiple times, if you do it's your
    fault when things break, and you get to pick up all the pieces.
    """
    def __init__(self):
        self._event_registry = {}
        self._registry = {}
    
    def register(self, badge):
        # We should probably duck-type this, but for now it's a decent sanity
        # check.
        assert issubclass(badge, Badge)
        badge = badge()
        self._registry[badge.slug] = badge
        for event in badge.events:
            self._event_registry.setdefault(event, []).append(badge)
    
    def possibly_award_badge(self, event, **state):
        for badge in self._event_registry[event]:
            badge.possibly_award(**state)
            
    def get_all_badges(self):
        return self._registry


class AwardedBadge(object):
    def __init__(self, slug, level, user_id):
        self.slug = slug
        self.level = level
        self._user_id = user_id
        self._badge = badges._registry[slug]
    
    @property
    def user(self):
        if not hasattr(self, "_user"):
            self._user = User.objects.get(pk=self._user_id)
        return self._user
    
    @property
    def name(self):
        return self._badge.levels[self.level].name
        
    @property
    def icon(self):
        from django.conf import settings
        return settings.STATIC_URL+"images/badges/"+self._badge.levels[self.level].name.lower()+"-"+str(self.level)+".png"
    
    @property
    def description(self):
        return self._badge.levels[self.level].description
    
    @property
    def progress(self):
        return self._badge.progress(self.user, self.level)


badges = BadgeCache()
