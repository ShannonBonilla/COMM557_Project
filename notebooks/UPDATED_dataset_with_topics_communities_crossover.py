import pandas as pd
import os

current_folder = os.path.dirname(os.path.abspath(__file__))

repo_root = os.path.abspath(os.path.join(current_folder, '..'))

data_folder = os.path.join(repo_root, 'data')

# Load Lea's existing file with topics, communities, and crossover information
dataset_file = os.path.join(data_folder, 'data_with_topics_communities_crossover.csv')
dataset_with_topics_communities_crossover = pd.read_csv(dataset_file)

unique_pairs = dataset_with_topics_communities_crossover[['track_name', 'artist_name']].drop_duplicates()
print("Number of unique track+artist pairs in Lea's dataset:", len(unique_pairs))

# Load and combine Spotify data
spotify_files = [
    'spotify_top_charts_19.csv',
    'spotify_top_charts_20.csv',
    'spotify_top_charts_21.csv',
    'spotify_top_charts_22.csv'
]

spotify_dfs = []
for file in spotify_files:
    file_path = os.path.join(data_folder, file)
    year_str = file.split('_')[-1].split('.')[0]
    year = int('20' + year_str)
    df = pd.read_csv(file_path)
    df['year'] = year
    df = df.rename(columns={'artist_names': 'artist_name'})
    spotify_dfs.append(df)

spotify_all = pd.concat(spotify_dfs, ignore_index=True)

# Load and combine TikTok data
tiktok_files = [
    'TikTok_songs_2019.csv',
    'TikTok_songs_2020.csv',
    'TikTok_songs_2021.csv',
    'TikTok_songs_2022.csv'
]

tiktok_dfs = []
for file in tiktok_files:
    file_path = os.path.join(data_folder, file)
    year = int(file.split('_')[-1].split('.')[0])
    df = pd.read_csv(file_path)
    df['year'] = year
    tiktok_dfs.append(df)

tiktok_all = pd.concat(tiktok_dfs, ignore_index=True)

# Outer join TikTok and Spotify datasets on track_name, artist_name, year
merged_all = pd.merge(
    tiktok_all,
    spotify_all[['track_name', 'artist_name', 'year', 'weeks_on_chart']],
    on=['track_name', 'artist_name', 'year'],
    how='outer'
)

# Compute number of years a song appears on Spotify charts
year_counts = merged_all.groupby(['track_name', 'artist_name'])['year'].nunique().reset_index()
year_counts = year_counts.rename(columns={'year': 'year_count'})

merged_all = merged_all.merge(year_counts, on=['track_name', 'artist_name'], how='left')

# Compute upper quartile weeks on chart from Spotify data
upper_quartile_weeks = spotify_all['weeks_on_chart'].quantile(0.75)

# Classify chart longevity
def classify_longevity(row):
    if row['year_count'] > 1:
        return 'sustained'
    elif pd.notna(row['weeks_on_chart']):
        return 'sustained' if row['weeks_on_chart'] > upper_quartile_weeks else 'brief'
    else:
        return 'unknown'  # TikTok-only or no Spotify weeks_on_chart data

merged_all['chart_longevity'] = merged_all.apply(classify_longevity, axis=1)

# Fix the "Some" by BOL4 entry
mask = merged_all['track_name'].str.strip().str.lower().eq('some') & merged_all['artist_name'].str.contains('bol', case=False, na=False)

# Merge with Lea's dataset. The new columns are 'year','weeks_on_chart', and 'chart_longevity'
final_dataset = dataset_with_topics_communities_crossover.merge(
    merged_all[['track_name', 'artist_name', 'year', 'weeks_on_chart','chart_longevity']],
    on=['track_name', 'artist_name'],
    how='left'
)

mask_final = final_dataset['track_name'].str.strip().str.lower().eq('some') & final_dataset['artist_name'].str.contains('bol', case=False, na=False)
final_dataset.loc[mask_final, 'year'] = 2021
final_dataset.loc[mask_final, 'chart_longevity'] = 'unknown'

final_dataset = final_dataset.drop_duplicates()

# Save the final dataset
output_file = os.path.join(data_folder, 'UPDATED_dataset_with_topics_communities_crossover.csv')
final_dataset.to_csv(output_file, index=False)

print("Updated dataset saved successfully.")

# Print cutoff for sustained success
print(f"Current cutoff for sustained success (weeks on chart, upper quartile): {upper_quartile_weeks}")

# Count unique track+artist pairs with their chart longevity
unique_pairs = final_dataset[['track_name', 'artist_name', 'chart_longevity']].drop_duplicates()

# Count how many in each category
category_counts = unique_pairs['chart_longevity'].value_counts()

# Calculate percentages
category_percentages = unique_pairs['chart_longevity'].value_counts(normalize=True) * 100

# Print results
print("\nCounts of unique track+artist pairs per category:")
print(category_counts)
print("\nPercentages of unique track+artist pairs per category:")
print(category_percentages)