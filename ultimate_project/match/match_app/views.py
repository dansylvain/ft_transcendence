import os
from django.shortcuts import render
from match_app.services.pong import Pong
from django.http import JsonResponse
from django.http import HttpRequest, HttpResponse, JsonResponse

pongs = []

def new_match(request: HttpRequest):
    
    pong = Pong(int(request.GET.get("p1")), int(request.GET.get("p2")))
    pongs.append(pong)
    return JsonResponse({"matchId": pong.id}, status=201)

def safe_int(value, default=0):

	try:
		return int(value)
	except (TypeError, ValueError) as e:
		print(e)
		return default

def enter_match2d(request: HttpRequest):
    
	client_host = request.get_host().split(":")[0]

	if client_host in ["127.0.0.1", "localhost"]:
		pidom = "localhost:8443"
	else:
		pidom = os.getenv("HOST_IP", "localhost:8443")
	print("ICIIIIIIIIII", flush=True)
	print(f"{safe_int(request.GET.get('playerId', '0'))}, "
		f"{request.GET.get('playerName', '0')}, "
		f"{safe_int(request.GET.get('player2Id', '0'))}, "
		f"{request.GET.get('player2Name', '0')}",
		flush=True)

	return render(
		request,
		"pong2d.html",
		{
			"rasp": os.getenv("rasp", "false"),
			"pidom": os.getenv("HOST_IP", "localhost:8443"),
			"matchId": safe_int(request.GET.get("matchId", "0")),
			"playerId": safe_int(request.GET.get("playerId", "0")),
			"playerName": request.GET.get("playerName", "0"),
			"player2Id": safe_int(request.GET.get("player2Id", "0")),
			"player2Name": request.GET.get("player2Name", "0"),
		},
	)

def enter_match3d(request: HttpRequest):

    return render(
        request,
        "pong3d.html",
        {
            "rasp": os.getenv("rasp", "false"),
            "pidom": os.getenv("HOST_IP", "localhost:8443"),
            "matchId": safe_int(request.GET.get("matchId", "0")),
            "playerId": safe_int(request.GET.get("playerId", "0")),
            "playerName": request.GET.get("playerName", "0"),
        },
    )

async def stop_match(request: HttpRequest, playerId, matchId):

    for p in pongs:
        if p.id == matchId:
            if await p.stop(playerId):
                return JsonResponse({"status": "succes"})
            else:
                return JsonResponse({"status": "fail"}, status=400)
    return JsonResponse({"status": "not authorized"}, status=400)

def del_pong(pong_id):

	print(f"DEL PONG {pong_id}", flush=True)
	from match_app.services.match_consumer import players
		
	pong = next((p for p in pongs if p.id == pong_id), None)
	print(players, flush=True)
	print(pongs, flush=True)
	if pong: 
		players[:] = [
			p for p in players if not any(
				p['playerId'] == po['playerId'] for po in pong.players   
		)]	
		pongs[:] = [p for p in pongs if p.id != pong_id]
	print(players, flush=True)
	print(pongs, flush=True)
