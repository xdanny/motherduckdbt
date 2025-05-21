import streamlit as st
import pandas as pd
import duckdb
import os

# --- Configuration ---
DB_PATH = '../data/nba_analytics.duckdb' # Relative path to the DuckDB file

# --- Helper Functions ---
@st.cache_data # Cache the data loading to improve performance
def load_data_from_duckdb(db_path, table_name="mvp_candidates"):
    """
    Connects to DuckDB and loads data from the specified table.
    """
    # Adjust path to be absolute from the script's directory if necessary,
    # though relative paths usually work fine with Streamlit if the CWD is the project root.
    # For robustness, construct path relative to this script file.
    script_dir = os.path.dirname(__file__)
    absolute_db_path = os.path.join(script_dir, db_path)

    try:
        con = duckdb.connect(database=absolute_db_path, read_only=True)
        query = f"SELECT * FROM {table_name}"
        df = con.execute(query).fetchdf()
        con.close()
        return df
    except Exception as e:
        st.error(f"Error loading data from DuckDB: {e}")
        st.error(f"Attempted to connect to: {absolute_db_path}")
        # Try to list contents of data directory for debugging if path seems wrong
        try:
            data_dir_path = os.path.join(script_dir, '../data/')
            st.info(f"Contents of {data_dir_path}: {os.listdir(data_dir_path)}")
        except Exception as list_e:
            st.warning(f"Could not list contents of data directory: {list_e}")
        return pd.DataFrame() # Return empty DataFrame on error

# --- Main Application ---
st.set_page_config(layout="wide")

st.title("🏀 NBA MVP Candidates Dashboard 🏀")
st.markdown("""
Welcome to the NBA MVP Candidates Dashboard!
This dashboard displays key statistics for top NBA players who are potential MVP candidates,
based on their performance in the 2023 season.
The data is sourced from [Basketball-Reference.com](https://www.basketball-reference.com/)
and processed using a dbt pipeline.
""")

# Load the data
mvp_candidates_df = load_data_from_duckdb(DB_PATH, "mvp_candidates")

if mvp_candidates_df.empty:
    st.warning("No data loaded for MVP candidates. Please check the database connection and dbt models.")
else:
    st.header("🏆 MVP Candidates Statistics (2023 Season)")
    st.markdown(f"Displaying **{len(mvp_candidates_df)}** players who meet the initial MVP criteria (Games Played >= 50, Points Per Game >= 20), ordered by Points Per Game.")
    
    # Displaying the dataframe
    # Making a copy for display modifications if needed, and selecting a subset of columns for better readability
    display_df = mvp_candidates_df[[
        'player_name', 'pos', 'team_abbreviation', 'age', 'games_played', 
        'pts_per_game', 'total_rebounds_per_game', 'assists_per_game', 
        'field_goal_percentage', 'three_point_percentage', 'effective_field_goal_percentage'
    ]].copy()
    
    # Optional: Formatting numeric columns for better display
    for col in ['field_goal_percentage', 'three_point_percentage', 'effective_field_goal_percentage']:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(lambda x: f"{x:.3f}" if pd.notnull(x) else x)
    for col in ['pts_per_game', 'total_rebounds_per_game', 'assists_per_game']:
         if col in display_df.columns:
            display_df[col] = display_df[col].map(lambda x: f"{x:.1f}" if pd.notnull(x) else x)

    st.dataframe(display_df.reset_index(drop=True))

    st.header("📊 Visualizations")

    # --- Bar Chart: Top N Players by Points Per Game ---
    st.subheader("Top Players by Points Per Game (PTS)")
    
    # Slider to select top N players for the bar chart
    # Ensure max_value is at least 1, and not more than the number of players
    max_players_for_slider = len(mvp_candidates_df)
    default_top_n = min(10, max_players_for_slider) if max_players_for_slider > 0 else 1

    if max_players_for_slider > 0:
        top_n = st.slider("Select number of top players to display:", 
                          min_value=1, 
                          max_value=max_players_for_slider, 
                          value=default_top_n,
                          key="top_n_slider")
        
        # Bar chart data already sorted by pts_per_game desc in mvp_candidates model
        bar_chart_df = mvp_candidates_df.head(top_n).set_index('player_name')
        st.bar_chart(bar_chart_df[['pts_per_game']], height=500)
    else:
        st.info("Not enough data to display bar chart.")


    # --- Scatter Plot: Customizable Stats ---
    st.subheader("Customizable Player Statistics Scatter Plot")
    
    # Define numerical columns for selection
    numerical_cols = [
        'age', 'games_played', 'games_started', 'minutes_played_per_game', 
        'pts_per_game', 'total_rebounds_per_game', 'assists_per_game', 
        'steals_per_game', 'blocks_per_game', 'field_goal_percentage', 
        'three_point_percentage', 'free_throw_percentage', 
        'effective_field_goal_percentage', 'turnovers_per_game', 'personal_fouls_per_game'
    ]
    
    # Check if numerical_cols are in the dataframe
    available_numerical_cols = [col for col in numerical_cols if col in mvp_candidates_df.columns]

    if len(available_numerical_cols) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            x_axis_stat = st.selectbox("Select X-axis statistic:", 
                                       options=available_numerical_cols, 
                                       index=available_numerical_cols.index('assists_per_game') 
                                       if 'assists_per_game' in available_numerical_cols else 0,
                                       key="x_axis_select")
        with col2:
            y_axis_stat = st.selectbox("Select Y-axis statistic:", 
                                       options=available_numerical_cols, 
                                       index=available_numerical_cols.index('total_rebounds_per_game') 
                                       if 'total_rebounds_per_game' in available_numerical_cols else 1,
                                       key="y_axis_select")

        if x_axis_stat and y_axis_stat:
            # Ensure selected columns exist (they should, based on available_numerical_cols)
            if x_axis_stat in mvp_candidates_df.columns and y_axis_stat in mvp_candidates_df.columns:
                st.scatter_chart(
                    mvp_candidates_df,
                    x=x_axis_stat,
                    y=y_axis_stat,
                    # Optional: add player name on hover if Streamlit supports it easily,
                    # or consider color by position/team if desired.
                    # For simplicity, direct plot first.
                    height=500
                )
            else:
                st.warning("Selected columns for scatter plot are not available in the data.")
        else:
            st.info("Please select two statistics to plot.")
    else:
        st.info("Not enough numerical data columns available for scatter plot.")

st.sidebar.header("About")
st.sidebar.info("""
This dashboard is a demonstration of an end-to-end data pipeline project involving:
- Data fetching from the web (`requests`, `BeautifulSoup`)
- Data transformation with dbt (`dbt-duckdb`)
- Data presentation with Streamlit
The source code and more details can be found on GitHub (placeholder).
""")
st.sidebar.markdown("---")
st.sidebar.markdown("To run this app locally:")
st.sidebar.code("streamlit run nba_mvp_dashboard/streamlit_app/app.py")

# --- End of Script ---
