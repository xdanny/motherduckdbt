{{ config(materialized='table') }}

with player_summary as (
    select * from {{ ref('int_player_stats_summary') }}
)

select
    player_name,
    pos,
    age,
    team_abbreviation,
    games_played,
    games_started,
    minutes_played_per_game,
    pts_per_game,
    total_rebounds_per_game,
    assists_per_game,
    steals_per_game,
    blocks_per_game,
    field_goal_percentage,
    three_point_percentage,
    free_throw_percentage,
    effective_field_goal_percentage,
    turnovers_per_game,
    personal_fouls_per_game
from
    player_summary
where
    games_played >= 50
    and pts_per_game >= 20
order by
    pts_per_game desc
