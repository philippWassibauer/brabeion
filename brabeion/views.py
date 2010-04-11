from collections import defaultdict

from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from brabeion import badges
from brabeion.models import BadgeAward



def badge_list(request):
    if request.user.is_authenticated():
        user_badges = set((slug, level) for slug, level in
            BadgeAward.objects.filter(
                user = request.user
            ).values_list("slug", "level"))
    else:
        user_badges = []
    all_badges = badges.get_all_badges()
    badges_awarded = BadgeAward.objects.values("slug", "level").annotate(
        num = Count("pk")
    )
    
    badges_dict = defaultdict(list)
    for badge_name in all_badges.keys():
        badge = all_badges[badge_name]
        counter = 0
        for level in badge.levels:
            badges_dict[badge.slug].append({
                "level": counter+1,
                "name": badges._registry[badge.slug].levels[counter].name,
                "description": badges._registry[badge.slug].levels[counter].description,
                #"count": badges_awarded[badge_name].badge["num"],
                "user_has": (badge.slug, counter) in user_badges
            })
            counter = counter+1
    
    for badge_group in badges_dict.values():
        badge_group.sort(key=lambda o: o["level"])
    
    return render_to_response("brabeion/badges.html", {
        "badges": sorted(badges_dict.items()),
    }, context_instance=RequestContext(request))


def badge_detail(request, slug, level):
    
    badge = badges._registry[slug].levels[int(level)]
    
    badge_awards = BadgeAward.objects.filter(
        slug = slug,
        level = level
    ).order_by("-awarded_at")
    
    badge_count = badge_awards.count()
    latest_awards = badge_awards[:50]
    
    return render_to_response("brabeion/badge_detail.html", {
        "badge": badge,
        "badge_count": badge_count,
        "latest_awards": latest_awards,
    }, context_instance=RequestContext(request))
