from leagueoflegends import LeagueOfLegends, RiotError
lol = LeagueOfLegends('RGAPI-0a05f239-871e-4875-9a06-1d4494833154')

id = lol.get_summoner_by_name('TheMIsterSenpai')
lol.get_games(id)

lol.set_summoner('TheMIsterSenpai')
lol.get_summoner_stats()
lol.get_summoner_ranked_stats()

# Access data through dictionaries
try:
    teams = lol.get_summoner_teams()
    for t in teams:
        print (t["name"])
        for m in t["roster"]["memberList"]:
            id = m["playerId"]
            print (id)
            print (lol.get_summoner_by_id(id)["name"])
except RiotError as e:
    print (e.error_msg)
