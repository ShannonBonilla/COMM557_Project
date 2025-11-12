import pandas as pd
import os

current_folder = os.path.dirname(os.path.abspath(__file__))

repo_root = os.path.abspath(os.path.join(current_folder, '..'))

data_folder = os.path.join(repo_root, 'data')

# Load Lea's existing file with topics, communities, and crossover information
dataset_file = os.path.join(data_folder, 'data_with_topics_communities_crossover.csv')
dataset_with_topics_communities_crossover = pd.read_csv(dataset_file)

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
year_counts = spotify_all.groupby(['track_name', 'artist_name'])['year'].nunique().reset_index()
year_counts = year_counts.rename(columns={'year': 'year_count'})

merged_all = merged_all.merge(year_counts, on=['track_name', 'artist_name'], how='left')

# Compute median weeks on chart from Spotify data
median_weeks = spotify_all['weeks_on_chart'].median()

# Classify chart longevity
def classify_longevity(row):
    if row['year_count'] > 1:
        return 'sustained'
    elif pd.notna(row['weeks_on_chart']):
        return 'sustained' if row['weeks_on_chart'] > median_weeks else 'brief'
    else:
        return 'unknown'  # TikTok-only or no Spotify weeks_on_chart data

merged_all['chart_longevity'] = merged_all.apply(classify_longevity, axis=1)

# Merge with Lea's dataset. The new columns are 'year','weeks_on_chart', and 'chart_longevity'
final_dataset = dataset_with_topics_communities_crossover.merge(
    merged_all[['track_name', 'artist_name', 'year', 'weeks_on_chart','chart_longevity']],
    on=['track_name', 'artist_name'],
    how='left'
)

# Save the final dataset
output_file = os.path.join(data_folder, 'UPDATED_dataset_with_topics_communities_crossover.csv')
final_dataset.to_csv(output_file, index=False)

print("Updated dataset saved successfully.")
