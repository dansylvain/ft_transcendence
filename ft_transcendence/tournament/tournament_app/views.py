from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
import requests
import aiohttp
import asyncio

import tournament_app.services.simple_match_consumer as sm_cs
import tournament_app.services.tournament_consumer as t_cs

def simple_match(request: HttpRequest, user_id):
    
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
            "pidom": os.getenv("HOST_IP", "localhost:8443"),
            "user_id": user_id,
            "user_name": user_name,
        },
    )

def watch_dog(request : HttpRequest):

    simple_ret = sm_cs.SimpleConsumer.watch_dog(request)  
    if simple_ret:
        return JsonResponse(simple_ret) 
    tou_ret = t_cs.TournamentConsumer.watch_dog(request)
    if tou_ret:
        return JsonResponse(tou_ret)
    return JsonResponse({"error": "No match found"}, status=504)

@csrf_exempt
async def match_players_update(request: HttpRequest):
    
    data = json.loads(request.body.decode("utf-8"))

    await sm_cs.SimpleConsumer.match_players_update(data)
    await t_cs.TournamentConsumer.match_players_update(data)
    return JsonResponse({"status": "succes"})

@csrf_exempt
async def match_result(request: HttpRequest):
    
    data = json.loads(request.body.decode("utf-8"))  

    await sm_cs.SimpleConsumer.match_result(data)
    await t_cs.TournamentConsumer.match_result(data)
    return JsonResponse({"status": "succes"})

def tournament(request: HttpRequest, user_id):
        
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
            "pidom": os.getenv("HOST_IP", "localhost:8443"),
            "user_id": user_id,
            "user_name": user_name,
        },
    )

def tournament_pattern(request: HttpRequest, tournament_id):
    
    return render(
        request,
        "tournament_pattern.html",
    )

async def send_db(path, result):

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://databaseapi:8007/{path}", json=result,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status in (200, 201):
                    print(f"Success: {response.status}", flush=True)
                else:
                    err = await response.text()
                    print(
                        f"[HTTP ERROR] Status {response.status}: {err}",
                        flush=True
                    )
    except aiohttp.ClientError as e:
        print(f"[REQUEST FAILED] Client error: {str(e)}", flush=True)
    except asyncio.TimeoutError:
        print("[REQUEST FAILED] Timeout error", flush=True)
    except Exception as e:
        print(f"[REQUEST FAILED] Unexpected error: {str(e)}", flush=True)
