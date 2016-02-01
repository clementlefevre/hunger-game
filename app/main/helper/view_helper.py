__author__ = 'ThinkPad'


def current_ranking(all_votes_today, restaurants):
    sorted_restaurants = []
    for resto in restaurants:
        resto_vote = 0

        for today_vote in all_votes_today:
            if today_vote.restaurant_id == resto.id:
                resto_vote += 1
        sorted_restaurants.append((resto, resto_vote))
    if len(sorted_restaurants) > 1:
        sorted_restaurants.sort(key=lambda x: x[1], reverse=True)
        sorted_restaurants = zip(*sorted_restaurants)[0]
    return sorted_restaurants
