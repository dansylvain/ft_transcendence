from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.http import Http404
from django_filters import rest_framework as filters
from django.utils import timezone
from rest_framework.response import Response
from .models import Player, Tournament, Match, PlayerStatistics
from .serializers import PlayerSerializer, TournamentSerializer, MatchSerializer, PlayerStatisticsSerializer
from datetime import datetime, timedelta
from django.db.models import Q
import time

# ====================================== FILTERS =======================================
class PlayerFilter(filters.FilterSet):
    username = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Player
        fields = ['username', 'email']

class MatchFilter(filters.FilterSet):
    player1 = filters.NumberFilter()
    player2 = filters.NumberFilter()
    tournament = filters.NumberFilter()
    player_id = filters.NumberFilter(method='filter_by_player')

    class Meta:
        model = Match
        fields = ['player1', 'player2', 'tournament', 'player_id'] # field for query

    #call custom method for this filter
    # queryset is like Match.objects.all()
    # new instance of match filter created for each request 
    def filter_by_player(self, queryset, name, value):
        # Filter matches where the player appears as either player1 or player2
        return queryset.filter(Q(player1=value) | Q(player2=value))

class PlayerStatisticsFilter(filters.FilterSet):
    # use the id of the player model using the '__' to acess the id
    player = filters.CharFilter(field_name='player__id', lookup_expr='icontains')  # Filter by player's username
    # use with /?player_id={id}
    class Meta:
        model = PlayerStatistics
        fields = ['player_id']

# ====================================== VIEWS SETS ====================================
class PlayerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing players
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filterset_class = PlayerFilter
    
    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response(
                {"error": "Player object not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class PlayerStatisticsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStatistics.objects.all()
    serializer_class = PlayerStatisticsSerializer
    filterset_class = PlayerStatisticsFilter

    #update only for a real player not bot or admin
    @action(detail=True, methods=['POST'], url_path='update-stats')
    def update_stats(self, request, player_id=None):
        try:
            # Get the player statistics by player_id
            print(f"Printing player stats for player_id {player_id}", flush=True)
            try:
                player_id = int(player_id)
                if player_id <= 1:
                    return Response({
                        "message": "Player not updated because player is an admin or a bot"
                    }, status=status.HTTP_204_NO_CONTENT)
            except (TypeError, ValueError):
                return Response({
                    "message": "Invalid player_id"
                }, status=status.HTTP_400_BAD_REQUEST)
            player_obj = Player.objects.get(id=player_id)
            player_stats = PlayerStatistics.objects.get(player=player_obj)
            data = {
                "is_won": request.data.get('is_won', 0),
                "is_lost": request.data.get('is_lost', 0),
                "points_scored": request.data.get('points_scored', 0),
                "points_conceded": request.data.get('points_conceded', 0),
                "nb_tournaments_played": request.data.get('nb_tournaments_played', 0),
    			"nb_tournaments_won": request.data.get('nb_tournaments_won', 0),
            }
            # global user stats
            player_stats.games_played += 1
            player_stats.games_won += data["is_won"]
            player_stats.games_lost += data["is_lost"]
            player_stats.points_scored += data["points_scored"]
            player_stats.points_conceded += data["points_conceded"]
            player_stats.nb_tournaments_played += data["nb_tournaments_played"]
            player_stats.nb_tournaments_won += data["nb_tournaments_won"]
    
            gp_total = player_stats.games_played
            gw_total = player_stats.games_won
            ps_total = player_stats.points_scored
            player_stats.win_rate = round((gw_total / gp_total) * 100, 2) if gp_total > 0 else 0.0
            player_stats.average_score = round(ps_total / gp_total, 2) if gp_total > 0 else 0.0
            if data["is_won"] == 1:
                player_stats.c_win_streak += 1
                player_stats.c_lose_streak = 0
                if player_stats.c_win_streak > player_stats.best_win_streak:
                    player_stats.best_win_streak = player_stats.c_win_streak
            elif data["is_lost"] == 1:
                player_stats.c_lose_streak += 1
                player_stats.c_win_streak = 0
                if player_stats.c_lose_streak > player_stats.worst_lose_streak:
                    player_stats.worst_lose_streak = player_stats.c_lose_streak
            player_stats.save()
            now = timezone.localtime(timezone.now())
            today_str = now.date().isoformat()
            # Build daily stat history
            if today_str in player_stats.stats_history:
                existing_record = player_stats.stats_history[today_str]
                existing_record["games_played"] += 1
                existing_record["games_won"] += data["is_won"]
                existing_record["games_lost"] += data["is_lost"]
                existing_record["points_scored"] += data["points_scored"]
                existing_record["points_conceded"] += data["points_conceded"]
                gp = existing_record["games_played"]
                gw = existing_record["games_won"]
                ps = existing_record["points_scored"]
                existing_record["win_rate"] = round((gw / gp) * 100, 2) if gp > 0 else 0.0
                existing_record["average_score"] = round(ps / gp, 2) if gp > 0 else 0.0
                existing_record["worst_lose_streak"] = player_stats.worst_lose_streak
                existing_record["best_win_streak"] = player_stats.best_win_streak
                existing_record["nb_tournaments_played"] += data["nb_tournaments_played"]
                existing_record["nb_tournaments_won"] += data["nb_tournaments_won"]
            else:
                # if data for the current day doesnt exist already
                games_played = 1
                games_won = data["is_won"]
                points_scored = data["points_scored"]
                update_record = {
                    "games_played": games_played,
                    "games_won": data["is_won"],
                    "games_lost": data["is_lost"],
                    "points_scored": data["points_scored"],
                    "points_conceded": data["points_conceded"],
                    "win_rate": round((games_won / games_played) * 100, 2) if games_played > 0 else 0.0,
                    "average_score": round(points_scored / games_played, 2) if games_played > 0 else 0.0,
                    "best_win_streak": player_stats.best_win_streak,
                    "worst_lose_streak": player_stats.worst_lose_streak,
                    "nb_tournaments_played": data["nb_tournaments_played"],
                    "nb_tournaments_won" : data["nb_tournaments_won"],
                }
                player_stats.stats_history[today_str] = update_record
            # Max 30 days history for game stats per day
            """ thirty_days_ago = timezone.now() - timedelta(days=30)
            filtered_history = {}
            for key_str, value in player_stats.update_history.items():
                key_date = datetime.fromisoformat(key_str).date()
                if key_date >= thirty_days_ago.date():
                    filtered_history[key_str] = value
            player_stats.update_history.clear()
            player_stats.update_history = filtered_history """
            player_stats.save()
            return Response({
                "message": "Player stats updated successfully",
            }, status=status.HTTP_200_OK)
        except PlayerStatistics.DoesNotExist:
            return Response({
                "error": "Player statistics not found"
            }, status=status.HTTP_404_NOT_FOUND)
    
    # detail false because do not depend on primary key will be 
    # /api/playerstats/get-top-players/
    @action(detail=False, methods=['GET'], url_path='get-top-players')
    def get_top_players(self, request):
        """
        Custom action to get top players by win rate
        """
        try:
            top_players = PlayerStatistics.objects.top_by_win_rate()
            serialized_data = PlayerStatisticsSerializer(top_players, many=True).data
            return Response(serialized_data)
        except Exception as e:
            return Response(
                {"error": f"Something went wrong: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response(
                {"error": "Player statistics not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )



class TournamentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing tournaments (read-only)
    """
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response(
                {"error": "Player not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class MatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing matches (read-only)
    """
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    filterset_class = MatchFilter

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response(
                {"error": "Player not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )