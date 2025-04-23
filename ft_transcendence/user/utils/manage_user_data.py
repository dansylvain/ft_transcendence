import httpx
from django.http import HttpRequest
import os
from typing import Tuple, Dict
from django.http import JsonResponse
from pprint import pprint
from pprint import PrettyPrinter


async def build_context(request: HttpRequest) -> Dict:
    """Build the base context with username from Request if found"""
    username = request.headers.get("X-Username")
    context = {}
    if username:
        context["username"] = username
    else:
        context["username"] = None
    return context

async def get_user_info_w_username(username):
    """
    Get user information by username from the database API
    """
    try:
        async with httpx.AsyncClient() as client:
            
            response = await client.get(
                f"http://databaseapi:8007/api/player/?username={username}"
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
                elif (
                    isinstance(data, dict)
                    and data.get("results")
                    and len(data["results"]) > 0
                ):
                    return data["results"][0]
            return None
    except Exception as e:
        print(f"Error getting user by username: {str(e)}", flush=True)
        return None

async def update_user_w_user_id(user_id, data):
    """
    Update user information in the database API
    """
    try:
        print(f"Updating user {user_id} with data: {data}", flush=True)
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json"}
            response = await client.patch(
                f"http://databaseapi:8007/api/player/{user_id}/",
                json=data,
                headers=headers,
            )
            print(f"Update response status: {response.status_code}", flush=True)
            print(f"Update response content: {response.text}", flush=True)
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"User updated successfully: {result}", flush=True)
                    return result
                except ValueError:
                    print("User updated successfully (non-JSON response)", flush=True)
                    return {"success": True}
            elif response.status_code != 200:
                try:
                    error_response = response.json()
                    error_message = None
                    for field, messages in error_response.items():
                        if messages: 
                            error_message = messages[0] 
                            break 
                    if not error_message:
                        error_message = "An unknown error occurred."
                    print(f"Error message extracted: {error_message}", flush=True)
                    return {"success": False, "error_message": error_message}
                except ValueError:
                    print("Failed to parse error response as JSON", flush=True)
                    return {"success": False, "error_message": "An unknown error occurred."}
    except Exception as e:
        print(f"Exception in update_user: {str(e)}", flush=True)
        return None

async def get_if_user_credentials_valid(username, password):
    """
    Check if the user's credentials are valid using the database API.
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json"}
            data = {
                "username": username,
                "password": password
            }
            response = await client.post(
                "http://databaseapi:8007/api/verify-credentials/",
                headers=headers,
                json=data,
            )
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"User credentials retrieved successfully.", flush=True)
                    return result
                except ValueError:
                    print("User credentials retrieved successfully (non-JSON response)", flush=True)
                    return {"success": True}
            print(f"Error retrieving user credentials: HTTP {response.status_code} - {response.text}",
                flush=True,)
            return None
    except Exception as e:
        print(f"Exception in get_if_user_credentials_valid: {str(e)}", flush=True)
        return None

async def delete_user_w_user_id(user_id):
    """
    Check if the user's credentials are valid using the database API.
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json"}
            response = await client.delete(
                f"http://databaseapi:8007/api/player/{user_id}/",
                headers=headers,   
            )
            if response.status_code == 204:
                try:
                    result = response.json()
                    print(f"User deleted successfully.", flush=True)
                    return result
                except ValueError:
                    print("User deleted successfully (non-JSON response)", flush=True)
                    return {"success": True}
            print(f"Error retrieving user credentials: HTTP {response.status_code} - {response.text}",
                flush=True,)
            return None
    except Exception as e:
        print(f"Exception in get_if_user_credentials_valid: {str(e)}", flush=True)
        return None

async def get_user_game_stats(user_id):
    """
    Get sanitize match data for a user_id from the database API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://databaseapi:8007/api/player_stats/?player_id={user_id}")
            response_data = response.json()
            if isinstance(response_data, list) and response_data:
                payload = response_data[0]
                main_stats = payload.get('main_stats', {})
                stats_history = payload.get('stats_history', {})
            else:
                return None, None
            if response.status_code == 200:
                return main_stats, stats_history
            return None, None
    except Exception as e:
        print(f"Error getting user stats: {str(e)}", flush=True)
        return None, None

async def get_user_match_history(user_id):
    """
    Get sanitize match data for a user_id from the database API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://databaseapi:8007/api/match/?player_id={user_id}")
            response_data = response.json()
            print("JSON DATA TOURNAMENT HISTORY \n\n:", flush=True)
            pprint(response_data)
            print("--\n", flush=True)
            if response.status_code == 200:
                return response_data
            return None, None
    except Exception as e:
        print(f"Error getting user stats: {str(e)}", flush=True)
        return None, None



async def get_user_tournament_history(user_id):
    """
    Get sanitize match data for a user_id from the database API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://databaseapi:8007/api/tournament/?winner_tournament={user_id}")
            response_data = response.json()
            """  print("JSON DATA TOURNAMENT HISTORY \n\n:", flush=True)
            pprint(response_data)
            print("--\n", flush=True) """
            if response.status_code == 200:
                return response_data
            return None, None
    except Exception as e:
        print(f"Error getting user stats: {str(e)}", flush=True)
        return None, None
