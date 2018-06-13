from settings import matches, stadiums, wiki, eventsSorted, matchdetails, goals, goals_expanded

pipeline = [
    {"$project": {"matchId":1, "venueName": 1}},
    {"$out": "stadium_matchId"}
]
matches.aggregate(pipeline)

# Get all normal time goals for games excluding penalty and penalty rebounds
pipeline = [
    {"$match": {"isShot": True, "qualifiers.type.value": {"$nin": [9, 501]}, "period.value": {"$in": [1,2]}}},
    {"$group": {"_id": {"matchId": "$matchId"},
                        "goals": {"$sum": {"$cond": ["$isGoal", 1, 0] }}}},
    {"$lookup": {
            "from": "stadium_matchId",
            "localField": "_id.matchId",
            "foreignField": "matchId",
            "as": "venue"}},
    {"$project": {"matchId": "$_id.matchId", "goals":1, "venue": {"$arrayElemAt": ["$venue.venueName",0]}}},
    {"$lookup": {
            "from": "stadiums",
            "localField": "venue",
            "foreignField": "venueName",
            "as": "location"}},
    {"$project": {"matchId": 1, "goals":1, "venue": 1,
                  "elevation": {"$arrayElemAt": ["$location.altitude_data.elevation",0]},
                  "location": {"$arrayElemAt": ["$location.location_data.geometry.location",0]}}},
    {"$lookup": {
                    "from": "matchdetails",
                    "localField": "matchId",
                    "foreignField": "matchId",
                    "as": "details"}},
    {"$project": {"matchId": 1, "goals":1, "venue": 1, "elevation": 1,
                  "location": 1,
                  "startTime":  {"$arrayElemAt": ["$details.startTime",0]}}},
    {"$out":"goals"}
]
eventsSorted.aggregate(pipeline)