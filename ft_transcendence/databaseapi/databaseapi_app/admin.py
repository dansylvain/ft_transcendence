from django.contrib import admin
from .models import Player, Tournament, Match, FriendList, FriendRequest


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "is_active")
    search_fields = ("email", "first_name", "last_name", "username")
    ordering = ("email",)

    # Ensure passwords are hashed when saving a Player in the admin.
    def save_model(self, request, obj, form, change):
        if "password" in form.changed_data:  # Only hash if password was changed
            obj.set_password(obj.password)  # Hash the password before saving
        super().save_model(request, obj, form, change)


#register models in django admin panel
@admin.register(FriendList)
class FriendListAdmin(admin.ModelAdmin):
    list_filter = ["user"]
    list_display = ("user",)
    search_fields = ("user",)
    readonly_fields = ["user"]
    #because not using the decorator @admin.register(FriendList)


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ["sender", "receiver"]
    list_display = ("sender", "receiver") 
    search_field = ("sender__username", "sender__email" , "receiver__username", 
                    "receiver__email")


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("id", "player1", "player2", "winner", "tournament")
