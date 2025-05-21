{{ config(materialized='table') }}

with source_data as (
    select * from {{ source('raw_nba_stats', 'player_per_game_stats') }}
),

filtered_source_data as (
    select *
    from source_data
    where
        -- Explicitly cast "Rk" to VARCHAR for the comparison to avoid type inference issues
        -- This is the primary filter for header rows based on the "Rk" column.
        cast("Rk" as VARCHAR) != 'Rk'
        and "Rk" is not null -- Ensures "Rk" column has some value
        -- Further checks for other potential header values in key text columns.
        -- These columns are defined as VARCHAR in sources.yml, so direct string comparison is fine.
        and "Player" is not null and "Player" != 'Player'
        and "Team" is not null and "Team" != 'Team'
        and "Pos" is not null and "Pos" != 'Pos'
)

select
    try_cast("Rk" as integer) as rk, -- Rank, now cast after header filter
    "Player" as player_name,
    "Pos" as pos, -- Position
    try_cast("Age" as integer) as age,
    "Team" as tm, -- Team abbreviation
    try_cast("G" as integer) as g, -- Games played
    try_cast("GS" as integer) as gs, -- Games started
    try_cast("MP" as float) as mp, -- Minutes played per game
    try_cast("FG" as float) as fg, -- Field goals made per game
    try_cast("FGA" as float) as fga, -- Field goals attempted per game
    try_cast("FG%" as float) as fg_pct, -- Field goal percentage
    try_cast("3P" as float) as fg3p, -- 3-point field goals made per game
    try_cast("3PA" as float) as fg3a, -- 3-point field goals attempted per game
    try_cast("3P%" as float) as fg3_pct, -- 3-point field goal percentage
    try_cast("2P" as float) as fg2p, -- 2-point field goals made per game
    try_cast("2PA" as float) as fg2a, -- 2-point field goals attempted per game
    try_cast("2P%" as float) as fg2_pct, -- 2-point field goal percentage
    try_cast("eFG%" as float) as efg_pct, -- Effective field goal percentage
    try_cast("FT" as float) as ft, -- Free throws made per game
    try_cast("FTA" as float) as fta, -- Free throws attempted per game
    try_cast("FT%" as float) as ft_pct, -- Free throw percentage
    try_cast("ORB" as float) as orb_per_game, -- Offensive rebounds per game
    try_cast("DRB" as float) as drb_per_game, -- Defensive rebounds per game
    try_cast("TRB" as float) as trb_per_game, -- Total rebounds per game
    try_cast("AST" as float) as ast_per_game, -- Assists per game
    try_cast("STL" as float) as stl_per_game, -- Steals per game
    try_cast("BLK" as float) as blk_per_game, -- Blocks per game
    try_cast("TOV" as float) as tov_per_game, -- Turnovers per game
    try_cast("PF" as float) as pf_per_game, -- Personal fouls per game
    try_cast("PTS" as float) as pts_per_game, -- Points per game
    "Awards" as awards -- Player awards for the season
from
    filtered_source_data
where
    -- Ensure critical numeric fields are not null after casting.
    -- try_cast will return NULL if conversion fails.
    -- The rk column (originally "Rk") is critical for joining or ordering, ensure it's a valid number.
    rk is not null 
    and g is not null
    and pts_per_game is not null
    and age is not null
    and mp is not null
    -- Add other key metric null checks as needed for analysis integrity
    and fg is not null 
    and trb_per_game is not null
    and ast_per_game is not null
