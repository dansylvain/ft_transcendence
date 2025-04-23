from rest_framework import serializers
from .models import Player, Tournament, Match, PlayerStatistics

""" 
Convert Django model instances (like your PlayerStatistics) to 
JSON - so they can be sent over an API.

Validate and deserialize incoming JSON from requests -
so it can be saved to the database.
"""


class PlayerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Player
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "two_fa_enabled",
            "_two_fa_secret",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Extract password from validated data
        password = validated_data.pop("password", None)

        # Create user instance without saving to database
        user = Player(**validated_data)

        # If password was provided, set it using the set_password method
        if password:
            user.set_password(password)

        # Save the user
        user.save()
        return user

    def update(self, instance, validated_data):
        # Handle password updates separately
        password = validated_data.pop("password", None)

        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If password was provided, hash it
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class PlayerNestedSerializer(serializers.ModelSerializer):
    """A simplified serializer for nesting within other serializers"""

    class Meta:
        model = Player
        fields = ["id", "username"]


class PlayerStatisticsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PlayerStatistics
        fields = [
            "player",
            "games_played",
            "games_won",
            "games_lost",
            "points_scored",
            "points_conceded",
            "win_rate",
            "average_score",
            "best_win_streak",
            "c_win_streak",
            "worst_lose_streak",
            "c_lose_streak",
            "nb_tournaments_played",
    		"nb_tournaments_won",
            "last_updated",
            "stats_history", #lifetime daily stat history
        ]
    
    #override orignal reprsentation data
    def to_representation(self, instance):
        data = super().to_representation(instance)
        main_stats = {key: data[key] for key in data if key != 'stats_history'}
        stats_history = data.get('stats_history', {})
        formatted_stats_history = {
            date: {
                "average_score": stats.get("average_score", 0.0),
                "best_win_streak": stats.get("best_win_streak", 0),
                "games_lost": stats.get("games_lost", 0),
                "games_played": stats.get("games_played", 0),
                "games_won": stats.get("games_won", 0),
                "nb_tournaments_played": stats.get("nb_tournaments_played", 0),
                "nb_tournaments_won": stats.get("nb_tournaments_won", 0),
                "points_conceded": stats.get("points_conceded", 0),
                "points_scored": stats.get("points_scored", 0),
                "win_rate": stats.get("win_rate", 0.0),
                "worst_lose_streak": stats.get("worst_lose_streak", 0),
            }
            for date, stats in stats_history.items()
        }
        
        payload = {}
        payload["main_stats"] = main_stats
        payload["stats_history"] = formatted_stats_history
        return payload


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = [
            "id",
            "winner_tournament",
        ]


class MatchSerializer(serializers.ModelSerializer):
    # Add nested player data
    player1_details = PlayerNestedSerializer(source="player1", read_only=True)
    player2_details = PlayerNestedSerializer(source="player2", read_only=True)
    winner_details = PlayerNestedSerializer(source="winner", read_only=True)
    
    winner_tournament = TournamentSerializer(source="tournament", read_only=True)
    
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    end_time =  serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Match
        fields = [
            "id",
            "player1",
            "player1_details",
            "player2",
            "player2_details",
            "winner",
            "winner_details",
            "tournament",
            "winner_tournament",
            "score_p1",
            "score_p2",
            "start_time",
            "end_time",
        ]
