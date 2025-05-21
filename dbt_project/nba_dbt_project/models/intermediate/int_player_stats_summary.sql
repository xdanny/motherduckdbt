{{ config(materialized='table') }}

select
    player_name,
    pos,
    age,
    tm as team_abbreviation, -- Renaming for clarity, was 'tm' in staging
    g as games_played,
    gs as games_started,
    mp as minutes_played_per_game,
    pts_per_game,
    trb_per_game as total_rebounds_per_game,
    ast_per_game as assists_per_game,
    stl_per_game as steals_per_game,
    blk_per_game as blocks_per_game,
    fg_pct as field_goal_percentage,
    fg3_pct as three_point_percentage,
    ft_pct as free_throw_percentage,
    efg_pct as effective_field_goal_percentage,
    tov_per_game as turnovers_per_game,
    pf_per_game as personal_fouls_per_game
from
    {{ ref('stg_player_per_game_stats') }}
-- No specific transformations or aggregations yet, pass-through for now.
-- Filters for player quality (e.g., minimum games played for meaningful stats)
-- are applied in the staging model or could be applied here if needed.
-- For this model, we assume stg_player_per_game_stats is already reasonably filtered.
