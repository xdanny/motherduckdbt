import streamlit as st
import pandas as pd
import duckdb
import os
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
DB_PATH = '../data/nba_analytics.duckdb' # Relative path to the DuckDB file from streamlit_app directory

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

    # --- Visualization Tabs ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Points Per Game", "Player Efficiency", "Stats Comparison", "Team Distribution", "Age vs Performance"])
    
    # --- Tab 1: Bar Chart: Top N Players by Points Per Game ---
    with tab1:
        st.subheader("Top Players by Points Per Game (PTS)")
        
        # Slider to select top N players for the bar chart
        max_players_for_slider = len(mvp_candidates_df)
        default_top_n = min(10, max_players_for_slider) if max_players_for_slider > 0 else 1

        if max_players_for_slider > 0:
            top_n = st.slider("Select number of top players to display:", 
                            min_value=1, 
                            max_value=max_players_for_slider, 
                            value=default_top_n,
                            key="top_n_slider")
            
            # Bar chart data already sorted by pts_per_game desc in mvp_candidates model
            bar_chart_df = mvp_candidates_df.head(top_n).sort_values('pts_per_game', ascending=False)
            
            # Using Plotly for better visualization
            fig = px.bar(
                bar_chart_df,
                x='player_name',
                y='pts_per_game',
                color='team_abbreviation',
                text='pts_per_game',
                labels={'pts_per_game': 'Points Per Game', 'player_name': 'Player'},
                title=f'Top {top_n} Players by Points Per Game'
            )
            fig.update_layout(xaxis_tickangle=-45)
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to display bar chart.")
    
    # --- Tab 2: Shooting Efficiency Chart ---
    with tab2:
        st.subheader("Player Shooting Efficiency")
        
        if not mvp_candidates_df.empty:
            # Create a scatter plot of FG% vs. 3P%
            fig = px.scatter(
                mvp_candidates_df,
                x='field_goal_percentage',
                y='three_point_percentage',
                size='pts_per_game',
                color='team_abbreviation',
                hover_name='player_name',
                labels={
                    'field_goal_percentage': 'Field Goal %',
                    'three_point_percentage': '3-Point %',
                    'pts_per_game': 'Points Per Game'
                },
                title="Shooting Efficiency: Field Goal % vs. 3-Point % (bubble size = Points Per Game)"
            )
            fig.update_layout(
                xaxis=dict(tickformat='.3f'),
                yaxis=dict(tickformat='.3f')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation
            st.markdown("""
            This chart visualizes the relationship between a player's field goal percentage and their three-point shooting percentage.
            - **X-axis**: Field Goal Percentage (overall shooting accuracy)
            - **Y-axis**: Three-Point Percentage (accuracy from beyond the arc)
            - **Bubble size**: Points Per Game (scoring volume)
            
            The most efficient shooters appear in the top-right corner (high percentages in both categories).
            """)
        else:
            st.info("Not enough data to create efficiency chart.")
            
    # --- Tab 3: Stats Comparison ---
    with tab3:
        st.subheader("Player Stats Comparison")
        
        if not mvp_candidates_df.empty:
            # Allow user to select players to compare
            all_players = mvp_candidates_df['player_name'].tolist()
            default_players = all_players[:3] if len(all_players) >= 3 else all_players
            
            selected_players = st.multiselect(
                "Select players to compare:",
                options=all_players,
                default=default_players,
                key="player_compare"
            )
            
            if selected_players:
                # Filter for selected players
                comparison_df = mvp_candidates_df[mvp_candidates_df['player_name'].isin(selected_players)]
                
                # Select stats for radar chart
                stats_to_compare = [
                    'pts_per_game', 'assists_per_game', 'total_rebounds_per_game',
                    'steals_per_game', 'blocks_per_game', 'effective_field_goal_percentage'
                ]
                
                # Normalize data for radar chart (0-1 scale)
                radar_df = comparison_df.copy()
                for stat in stats_to_compare:
                    if stat in radar_df.columns:
                        max_val = mvp_candidates_df[stat].max()
                        if max_val > 0:  # Avoid division by zero
                            radar_df[stat] = radar_df[stat] / max_val
                
                # Create radar chart using matplotlib
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111, polar=True)
                
                # Number of variables
                categories = ['Points', 'Assists', 'Rebounds', 'Steals', 'Blocks', 'Shooting Efficiency']
                N = len(categories)
                
                # What will be the angle of each axis in the plot
                angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
                angles += angles[:1]  # Close the loop
                
                # Draw one axis per variable and add labels
                plt.xticks(angles[:-1], categories, size=12)
                
                # Draw ylabels (0-100%)
                ax.set_rlabel_position(0)
                plt.yticks([0.25, 0.5, 0.75], ["25%", "50%", "75%"], color="grey", size=10)
                plt.ylim(0, 1)
                
                # Plot each player
                for i, player in enumerate(selected_players):
                    player_data = radar_df[radar_df['player_name'] == player]
                    if not player_data.empty:
                        values = [player_data[stat].values[0] if stat in player_data.columns else 0 for stat in stats_to_compare]
                        values += values[:1]  # Close the loop
                        ax.plot(angles, values, linewidth=2, linestyle='solid', label=player)
                        ax.fill(angles, values, alpha=0.1)
                
                # Add legend
                plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
                plt.title("Player Stats Comparison (Normalized)", size=15)
                
                st.pyplot(fig)
                
                # Show the raw stats in a table for comparison
                st.subheader("Raw Stats Comparison")
                display_cols = ['player_name', 'team_abbreviation', 'pts_per_game', 'assists_per_game', 
                               'total_rebounds_per_game', 'steals_per_game', 'blocks_per_game', 
                               'field_goal_percentage', 'three_point_percentage']
                st.dataframe(comparison_df[display_cols])
            else:
                st.info("Please select at least one player to compare.")
        else:
            st.info("Not enough data to create comparison chart.")
            
    # --- Tab 4: Team Distribution ---
    with tab4:
        st.subheader("MVP Candidates by Team")
        
        if not mvp_candidates_df.empty:
            team_counts = mvp_candidates_df['team_abbreviation'].value_counts().reset_index()
            team_counts.columns = ['Team', 'Number of MVP Candidates']
            
            fig = px.bar(
                team_counts,
                x='Team',
                y='Number of MVP Candidates',
                color='Team',
                labels={'Team': 'Team', 'Number of MVP Candidates': 'Number of MVP Candidates'},
                title='Number of MVP Candidates by Team'
            )
            fig.update_layout(xaxis_tickangle=0)
            st.plotly_chart(fig, use_container_width=True)
            
            # Pie chart for position distribution
            st.subheader("Position Distribution of MVP Candidates")
            pos_counts = mvp_candidates_df['pos'].value_counts().reset_index()
            pos_counts.columns = ['Position', 'Count']
            
            fig = px.pie(
                pos_counts,
                values='Count',
                names='Position',
                title='MVP Candidates by Position'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to create team distribution chart.")
            
    # --- Tab 5: Age vs Performance ---
    with tab5:
        st.subheader("Age vs. Performance Metrics")
        
        if not mvp_candidates_df.empty:
            # Select performance metric
            metric_options = ['pts_per_game', 'assists_per_game', 'total_rebounds_per_game', 
                             'steals_per_game', 'blocks_per_game', 'field_goal_percentage']
            selected_metric = st.selectbox(
                "Select performance metric:",
                options=metric_options,
                format_func=lambda x: {
                    'pts_per_game': 'Points Per Game',
                    'assists_per_game': 'Assists Per Game',
                    'total_rebounds_per_game': 'Rebounds Per Game',
                    'steals_per_game': 'Steals Per Game',
                    'blocks_per_game': 'Blocks Per Game',
                    'field_goal_percentage': 'Field Goal Percentage'
                }.get(x, x),
                key="age_metric"
            )
            
            # Create scatter plot
            fig = px.scatter(
                mvp_candidates_df,
                x='age',
                y=selected_metric,
                color='pos',
                size='games_played',
                hover_name='player_name',
                labels={
                    'age': 'Age',
                    selected_metric: {
                        'pts_per_game': 'Points Per Game',
                        'assists_per_game': 'Assists Per Game',
                        'total_rebounds_per_game': 'Rebounds Per Game',
                        'steals_per_game': 'Steals Per Game',
                        'blocks_per_game': 'Blocks Per Game',
                        'field_goal_percentage': 'Field Goal Percentage'
                    }.get(selected_metric, selected_metric),
                    'pos': 'Position',
                    'games_played': 'Games Played'
                },
                trendline="ols",
                title=f"Age vs. {selected_metric.replace('_', ' ').title()} (bubble size = Games Played)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add correlation analysis
            correlation = mvp_candidates_df[['age', selected_metric]].corr().iloc[0, 1]
            st.markdown(f"**Correlation between Age and {selected_metric.replace('_', ' ').title()}:** {correlation:.3f}")
            
            if abs(correlation) < 0.2:
                st.markdown("There appears to be little to no correlation between age and this metric.")
            elif abs(correlation) < 0.4:
                st.markdown("There appears to be a weak correlation between age and this metric.")
            elif abs(correlation) < 0.6:
                st.markdown("There appears to be a moderate correlation between age and this metric.")
            elif abs(correlation) < 0.8:
                st.markdown("There appears to be a strong correlation between age and this metric.")
            else:
                st.markdown("There appears to be a very strong correlation between age and this metric.")


    # --- Scatter Plot: Customizable Stats with Plotly ---
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
        col1, col2, col3 = st.columns(3)
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
        with col3:
            color_by = st.selectbox("Color by:", 
                                   options=["team_abbreviation", "pos", "age"],
                                   index=0,
                                   key="color_select")
        
        size_by = st.selectbox("Bubble size by:", 
                               options=["pts_per_game", "minutes_played_per_game", "None"],
                               index=0,
                               key="size_select")

        if x_axis_stat and y_axis_stat:
            # Ensure selected columns exist
            if x_axis_stat in mvp_candidates_df.columns and y_axis_stat in mvp_candidates_df.columns:
                # Use Plotly for a more interactive visualization
                if size_by != "None":
                    fig = px.scatter(
                        mvp_candidates_df,
                        x=x_axis_stat,
                        y=y_axis_stat,
                        color=color_by,
                        size=size_by if size_by != "None" else None,
                        hover_name="player_name",
                        title=f"{y_axis_stat} vs {x_axis_stat} by {color_by}",
                        labels={
                            x_axis_stat: x_axis_stat.replace('_', ' ').title(),
                            y_axis_stat: y_axis_stat.replace('_', ' ').title()
                        }
                    )
                else:
                    fig = px.scatter(
                        mvp_candidates_df,
                        x=x_axis_stat,
                        y=y_axis_stat,
                        color=color_by,
                        hover_name="player_name",
                        title=f"{y_axis_stat} vs {x_axis_stat} by {color_by}",
                        labels={
                            x_axis_stat: x_axis_stat.replace('_', ' ').title(),
                            y_axis_stat: y_axis_stat.replace('_', ' ').title()
                        }
                    )
                
                # Customize the plot
                fig.update_layout(
                    height=600,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Selected columns for scatter plot are not available in the data.")
        else:
            st.info("Please select two statistics to plot.")
    else:
        st.info("Not enough numerical data columns available for scatter plot.")

    # --- Additional Visualizations ---
    st.subheader("Distribution of Points Per Game")
    fig, ax = plt.subplots()
    sns.histplot(mvp_candidates_df['pts_per_game'], kde=True, ax=ax)
    ax.set_title("Distribution of Points Per Game")
    ax.set_xlabel("Points Per Game")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

    st.subheader("Correlation Heatmap")
    correlation_matrix = mvp_candidates_df[available_numerical_cols].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Correlation Heatmap of Player Statistics")
    st.pyplot(fig)

    st.subheader("Interactive Scatter Plot with Plotly")
    if len(available_numerical_cols) >= 2:
        x_axis_stat_plotly = st.selectbox("Select X-axis statistic for Plotly:", options=available_numerical_cols, key="x_axis_plotly")
        y_axis_stat_plotly = st.selectbox("Select Y-axis statistic for Plotly:", options=available_numerical_cols, key="y_axis_plotly")
        if x_axis_stat_plotly and y_axis_stat_plotly:
            fig = px.scatter(
                mvp_candidates_df,
                x=x_axis_stat_plotly,
                y=y_axis_stat_plotly,
                color="team_abbreviation",
                hover_data=["player_name", "pos"],
                title=f"{x_axis_stat_plotly} vs {y_axis_stat_plotly}"
            )
            st.plotly_chart(fig)

    # --- Correlation Heatmap ---
    st.header("🔥 Statistical Correlations")
    st.subheader("Correlation Heatmap of Player Statistics")
    
    if not mvp_candidates_df.empty:
        # Select only numeric columns for correlation
        numeric_df = mvp_candidates_df.select_dtypes(include=['float64', 'int64'])
        
        # Check if we have enough numeric columns
        if len(numeric_df.columns) > 1:
            # Calculate correlations
            corr = numeric_df.corr()
            
            # Use matplotlib for the heatmap
            fig, ax = plt.figure(figsize=(10, 8)), plt.axes()
            sns.heatmap(corr, 
                       annot=True, 
                       cmap='coolwarm', 
                       fmt=".2f",
                       linewidths=0.5,
                       ax=ax)
            plt.title('Correlation Between Player Statistics')
            plt.tight_layout()
            st.pyplot(fig)
            
            st.markdown("""
            **Interpreting the Heatmap**:
            * Values close to 1 indicate strong positive correlation (as one statistic increases, the other also increases)
            * Values close to -1 indicate strong negative correlation (as one statistic increases, the other decreases)
            * Values close to 0 indicate little to no correlation
            """)
        else:
            st.info("Not enough numeric columns to generate correlation heatmap.")
    else:
        st.info("No data available for correlation analysis.")
    
    # --- Position Analysis ---
    st.header("🏀 Position-Based Analysis")
    st.subheader("Statistical Comparison by Player Position")
    
    if not mvp_candidates_df.empty and 'pos' in mvp_candidates_df.columns:
        # Group data by position and calculate mean statistics
        pos_stats = mvp_candidates_df.groupby('pos').agg({
            'pts_per_game': 'mean',
            'total_rebounds_per_game': 'mean',
            'assists_per_game': 'mean',
            'steals_per_game': 'mean',
            'blocks_per_game': 'mean',
            'field_goal_percentage': 'mean'
        }).reset_index()
        
        # Create a radar chart using Plotly
        categories = ['Scoring', 'Rebounds', 'Assists', 'Steals', 'Blocks', 'FG%']
        fig = px.line_polar(
            pos_stats,
            r=[pos_stats['pts_per_game']/pos_stats['pts_per_game'].max(),
               pos_stats['total_rebounds_per_game']/pos_stats['total_rebounds_per_game'].max(),
               pos_stats['assists_per_game']/pos_stats['assists_per_game'].max(),
               pos_stats['steals_per_game']/pos_stats['steals_per_game'].max(),
               pos_stats['blocks_per_game']/pos_stats['blocks_per_game'].max(),
               pos_stats['field_goal_percentage']/pos_stats['field_goal_percentage'].max()],
            theta=categories,
            line_close=True,
            color='pos',
            title="Normalized Statistical Profile by Position",
            labels={'r': 'Normalized Value', 'theta': 'Statistic', 'color': 'Position'}
        )
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display a bar chart comparison for a selected statistic
        selected_stat = st.selectbox(
            "Select a statistic to compare across positions:",
            ['pts_per_game', 'total_rebounds_per_game', 'assists_per_game', 
             'steals_per_game', 'blocks_per_game', 'field_goal_percentage'],
            key="pos_stat_select"
        )
        
        fig = px.bar(
            pos_stats,
            x='pos',
            y=selected_stat,
            title=f"Average {selected_stat.replace('_', ' ').title()} by Position",
            color='pos',
            labels={'pos': 'Position', selected_stat: selected_stat.replace('_', ' ').title()}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Position data not available for comparison.")
    
    # --- Team Analysis ---
    st.header("🏆 Team-Based Analysis")
    st.subheader("MVP Candidates by Team")
    
    if not mvp_candidates_df.empty and 'team_abbreviation' in mvp_candidates_df.columns:
        # Count candidates by team
        team_counts = mvp_candidates_df['team_abbreviation'].value_counts().reset_index()
        team_counts.columns = ['team_abbreviation', 'count']
        
        # Create a bar chart
        fig = px.bar(
            team_counts,
            x='team_abbreviation',
            y='count',
            title="Number of MVP Candidates by Team",
            color='team_abbreviation',
            labels={'team_abbreviation': 'Team', 'count': 'Number of Candidates'}
        )
        fig.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Team with most candidates
        if not team_counts.empty:
            top_team = team_counts.loc[team_counts['count'].idxmax()]
            st.markdown(f"**{top_team['team_abbreviation']}** has the most MVP candidates with **{top_team['count']}** players.")
            
            # Display those players
            st.subheader(f"MVP Candidates from {top_team['team_abbreviation']}")
            team_players = mvp_candidates_df[mvp_candidates_df['team_abbreviation'] == top_team['team_abbreviation']]
            st.dataframe(team_players[['player_name', 'pos', 'age', 'pts_per_game', 'total_rebounds_per_game', 'assists_per_game']])
    else:
        st.info("Team data not available for analysis.")
        
    # --- MVP Scoring Model ---
    st.header("🌟 MVP Probability Model")
    st.subheader("Simple MVP Scoring Model")
    
    if not mvp_candidates_df.empty:
        # Create a simple MVP score based on key statistics
        # Note: This is a simplified model and not a true prediction
        if all(col in mvp_candidates_df.columns for col in ['pts_per_game', 'total_rebounds_per_game', 'assists_per_game']):
            # Create a copy to avoid modifying the original DataFrame
            scoring_df = mvp_candidates_df.copy()
            
            # Normalize key statistics (0-1 scale)
            for stat in ['pts_per_game', 'total_rebounds_per_game', 'assists_per_game']:
                max_val = scoring_df[stat].max()
                if max_val > 0:  # Avoid division by zero
                    scoring_df[f'{stat}_norm'] = scoring_df[stat] / max_val
            
            # Calculate MVP score (simple weighted sum)
            scoring_df['mvp_score'] = (
                scoring_df['pts_per_game_norm'] * 0.5 +  # 50% weight to scoring
                scoring_df['total_rebounds_per_game_norm'] * 0.25 +  # 25% weight to rebounds
                scoring_df['assists_per_game_norm'] * 0.25  # 25% weight to assists
            )
            
            # Sort by MVP score
            scoring_df = scoring_df.sort_values('mvp_score', ascending=False).reset_index(drop=True)
            
            # Display top 10 players by MVP score
            top_mvp_df = scoring_df.head(10)[['player_name', 'team_abbreviation', 'pts_per_game', 
                                              'total_rebounds_per_game', 'assists_per_game', 'mvp_score']]
            
            # Format MVP score
            top_mvp_df['mvp_score'] = top_mvp_df['mvp_score'].map(lambda x: f"{x:.3f}")
            
            st.subheader("Top 10 MVP Candidates by Simple Scoring Model")
            st.dataframe(top_mvp_df)
            
            # Create a horizontal bar chart for MVP scores
            fig = px.bar(
                top_mvp_df,
                y='player_name',
                x='mvp_score',
                orientation='h',
                color='mvp_score',
                title="MVP Score Ranking",
                labels={'player_name': 'Player', 'mvp_score': 'MVP Score'},
                color_continuous_scale='viridis'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Note about the MVP Score:**
            
            This is a simplified model that weights:
            * Points Per Game (50%)
            * Rebounds Per Game (25%)
            * Assists Per Game (25%)
            
            A more sophisticated model would include team record, player efficiency, advanced metrics, 
            media narrative, and historical voting patterns.
            """)
        else:
            st.info("Required statistics not available for MVP scoring.")
    else:
        st.info("No data available for MVP scoring model.")

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
