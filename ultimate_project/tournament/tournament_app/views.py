import os
import json
import tournament_app.services.simple_match_consumer as sm_cs
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import tournament_app.services.tournament_consumer as t_cs
import requests
import aiohttp

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
    await sm_cs.SimpleConsumer.match_players_update(data)
    await t_cs.TournamentConsumer.match_players_update(data)
    return JsonResponse({"status": "succes"})

@csrf_exempt
async def match_result(request: HttpRequest):
    
    print("MATCH RESULT", flush=True)
    data = json.loads(request.body.decode("utf-8"))   
    await sm_cs.SimpleConsumer.match_result(data)
    await t_cs.TournamentConsumer.match_result(data)
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

async def send_db(path, result):

	print(f"SEND DB {result}", flush=True)
	return	
	async with aiohttp.ClientSession() as session:
		async with session.post(
			f"http://databaseapi:8007/{path}", json=result) as response:				
			if response.status not in (200, 201):
				err = await response.text()
				print(f"Error HTTP {response.status}: {err}", flush=True)
