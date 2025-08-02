import pandas as pd
import os

routes_folder = "datasets/raw/Routes"
output_folder = "datasets/processed"
output_file = "master_routes.csv"

os.makedirs(output_folder, exist_ok=True)

csv_files = [file for file in os.listdir(routes_folder) if file.endswith(".csv")]

all_data = []

for file in csv_files:
    file_path = os.path.join(routes_folder, file)
    try:
        df = pd.read_csv(file_path)
        # df['TrainNo'] = file.replace(".csv", "")
        all_data.append(df)
    except Exception as e:
        print(f"⚠️ Could not read {file}: {e}")

# === Merge all DataFrames ===
merged_df = pd.concat(all_data, ignore_index=True)

merged_df.to_csv(os.path.join(output_folder, output_file), index=False)
print(f"✅ Merged {len(csv_files)} files into '{output_file}'")