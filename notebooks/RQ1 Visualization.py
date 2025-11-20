import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns

# Load dataset
df = pd.read_csv("data/UPDATED_dataset_with_artist_pop.csv")
print(f"Total rows in dataset: {len(df)}")

# Filter for TikTok Songs Only
df_tiktok = df[df["source"].str.contains("tiktok", case=False, na=False)].copy()
print(f"Total TikTok songs: {len(df_tiktok)}")

# Remote Duplicates Based on track_name and artist_name
df_tiktok_unique = df_tiktok.drop_duplicates(subset=["track_name", "artist_name"])
print(f"Unique TikTok songs (after removing duplicates): {len(df_tiktok_unique)}")

# Count Songs Per Community
community_counts = df_tiktok_unique["community"].value_counts()
print("\nAll communities (sorted by count):")
print(community_counts.head(20))

# Select Top 15 Communities by the number of songs in each community
top15_communities = community_counts.nlargest(15)
top15_ids = top15_communities.index.tolist()

print("\n=== Top 15 Communities (TikTok Songs) ===")
print(top15_communities)

# Get label_short for top 15 communities
df_top15 = df_tiktok_unique[df_tiktok_unique["community"].isin(top15_ids)]  # Changed to df_tiktok_unique
community_labels = df_top15.groupby("community")["label_short"].first()
top15_labels = [community_labels[comm] for comm in top15_ids]

# Visualization 1: Bar Chart
plt.figure(figsize=(14, 7))

sns.barplot(
    x=top15_labels,
    y=top15_communities.values,
    palette="viridis",
    hue=top15_labels,
    legend=False
)

plt.title("Top 15 Lyrical Communities Among TikTok-Trending Songs", fontsize=14, fontweight='bold')
plt.xlabel("Lyrical Themes", fontsize=12)
plt.ylabel("Number of Songs", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", alpha=0.3)

# Add Value Labels on Bars
for i, count in enumerate(top15_communities.values):
    plt.text(i, count + 2, f'{count}', ha='center', fontsize=10)

plt.tight_layout()
plt.show()