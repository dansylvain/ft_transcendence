import os
import json
import tournament_app.services.simple_match_consumer as sm_cs
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tournament_app.services.tournament_consumer import tournaments
import requests

def simple_match(request: HttpRequest, user_id):
    
    print(f"dans simple match {user_id}", flush=True)
    if user_id:
        response = requests.get(
                    f"http://databaseapi:8007/api/player/{user_id}/"
                )
        tmp = response.json()
        user_name = tmp["username"]
    else:
        user_name = 0

    return render(
        request,
        "simple_match.html",
        {
            "rasp": os.getenv("rasp", "false"),
            "pidom": os.getenv("HOST_IP", "localhost:8443"),
            "user_id": user_id,
            # "user_name": request.headers.get("X-Username", None),
            "user_name": user_name,
        },
    )

@csrf_exempt
async def match_players_update(request: HttpRequest):
    
    print(f"MATCH PLAYERS UPDATE VIEWS", flush=True)
    
    data = json.loads(request.body.decode("utf-8"))
    match_id = data.get("matchId", None)
    players = data.get("players", [])
    print(f"MATCH PLAYERS UPDATE VIEWS match_id: {match_id} {players}", flush=True)
    match = next(
        (m for m in sm_cs.matchs if m.get("matchId") == match_id), None)
    if match:
        match["players"] = players
        await sm_cs.SimpleConsumer.match_update()
    tournament = next(
        (
            t
            for t in tournaments
            if any(data.get("matchId") == m.get("matchId") for m in t.matchs)
        ),
        None,
    )
    if tournament:
        await tournament.match_players_update(data)
    return JsonResponse({"status": "succes"})

@csrf_exempt
async def match_result(request: HttpRequest):
    
    print("MATCH RESULT", flush=True)
    data = json.loads(request.body.decode("utf-8"))
    match_id = data.get("matchId")
    winner_id = data.get("winnerId")
    looser_id = data.get("looserId")
    p1_id = data.get("p1Id")
    p2_id = data.get("p2Id")
    p1 = next((p for p in sm_cs.players if p.get("playerId") == p1_id), None)
    p2 = next((p for p in sm_cs.players if p.get("playerId") == p2_id), None)
    if p1:
        p1["busy"] = None
    if p2:
        p2["busy"] = None   
    sm_cs.matchs[:] = [m for m in sm_cs.matchs if m.get("matchId") != match_id]
    await sm_cs.SimpleConsumer.match_update()
    tournament = next(
        (
            t
            for t in tournaments
            if any(match_id == m.get("matchId", None) for m in t.matchs)
        ),
        None,
    )
    if tournament:
        await tournament.match_result(match_id, winner_id, looser_id)
    return JsonResponse({"status": "succes"})

def tournament(request: HttpRequest, user_id):
    
    print(f"dans tournament {user_id}, {request.headers.get('X-Username')}", flush=True) 
    
    if user_id:
        response = requests.get(
                    f"http://databaseapi:8007/api/player/{user_id}/"
                )
        tmp = response.json()
        user_name = tmp["username"]
    else:
        user_name = 0
    
    return render(
        request,
        "tournament.html",
        {
            "rasp": os.getenv("rasp", "false"),
            "pidom": os.getenv("HOST_IP", "localhost:8443"),
            "user_id": user_id,
            "user_name": user_name,
        },
    )

def tournament_pattern(request: HttpRequest, tournament_id):
    
    print(f"dans tournament pattern {tournament_id}", flush=True)
    return render(
        request,
        "tournament_pattern.html",
    )
