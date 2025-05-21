#!/bin/bash
# Script to fix the repository structure by moving files from the nested directory

set -e  # Exit on error

MAIN_REPO="/workspaces/motherduckdbt/nba_mvp_dashboard"
NESTED_REPO="$MAIN_REPO/dbt_project/nba_mvp_dashboard"

echo "Fixing repository structure..."
echo "Moving files from nested repo to main repo's dbt_project directory"

# Check if the nested directory exists
if [ ! -d "$NESTED_REPO" ]; then
    echo "Error: Nested repository not found at $NESTED_REPO"
    exit 1
fi

# Move files from dbt_project/nba_mvp_dashboard/dbt_project to the main dbt_project directory
if [ -d "$NESTED_REPO/dbt_project" ]; then
    # Ensure we don't overwrite existing files - check first
    for file in $(find "$NESTED_REPO/dbt_project" -type f); do
        relative_path=${file#"$NESTED_REPO/dbt_project/"}
        target_path="$MAIN_REPO/dbt_project/$relative_path"
        
        if [ -f "$target_path" ]; then
            echo "Warning: File already exists at $target_path - skipping"
        else
            # Create target directory if it doesn't exist
            target_dir=$(dirname "$target_path")
            mkdir -p "$target_dir"
            
            # Move the file
            cp "$file" "$target_path"
            echo "Moved: $file -> $target_path"
        fi
    done
    
    echo "Finished moving files"
    echo "You can review the changes and then remove the nested directory with:"
    echo "rm -rf $NESTED_REPO"
else
    echo "No dbt_project directory found in nested repository"
fi

echo "Repository structure fix complete."
