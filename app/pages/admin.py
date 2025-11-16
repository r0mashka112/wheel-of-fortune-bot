from sqladmin import ModelView

from app.api.models import Player, Prize


class PlayerAdmin(ModelView, model = Player):
    column_exclude_list = [Player.prize]
    column_details_exclude_list = [Player.prize]
    form_excluded_columns = [Player.prize, Player.created_at, Player.updated_at]

    can_create = False
    can_edit = False


class PrizeAdmin(ModelView, model = Prize):
    column_exclude_list = [Prize.players]
    column_details_exclude_list = [Prize.players]
    form_excluded_columns = [Prize.players, Prize.created_at, Prize.updated_at]